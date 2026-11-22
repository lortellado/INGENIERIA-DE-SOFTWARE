"""Conversation Store (ADR-036): historial y acciones pendientes, con vencimiento.

En memoria y con claves por traveler_id (así se particionaría en un almacén real).
"""
from __future__ import annotations

import copy
import threading
from typing import Optional


class AlmacenConversaciones:
    def __init__(self, reloj, ttl_s: int):
        self._reloj = reloj
        self._ttl = ttl_s
        self._datos: dict = {}
        self._lock = threading.Lock()

    def _purgar(self) -> None:
        ahora = self._reloj.ahora()
        for clave in [k for k, (vence, _) in self._datos.items() if vence <= ahora]:
            del self._datos[clave]

    # --- conversación -----------------------------------------------------
    def obtener(self, traveler_id: str) -> dict:
        with self._lock:
            self._purgar()
            item = self._datos.get(("conv", traveler_id))
            if item:
                return copy.deepcopy(item[1])
        return {"mensajes": [], "fallos": 0, "ultimo_viaje": None}

    def guardar(self, traveler_id: str, conv: dict) -> None:
        with self._lock:
            self._datos[("conv", traveler_id)] = (self._reloj.ahora() + self._ttl, copy.deepcopy(conv))

    # --- acciones pendientes ----------------------------------------------
    def guardar_accion(self, accion_id: str, accion: dict) -> None:
        with self._lock:
            self._datos[("accion", accion_id)] = (self._reloj.ahora() + self._ttl, copy.deepcopy(accion))

    def obtener_accion(self, accion_id: str) -> Optional[dict]:
        with self._lock:
            self._purgar()
            item = self._datos.get(("accion", accion_id))
            return copy.deepcopy(item[1]) if item else None

    def cambiar_estado(self, accion_id: str, desde: Optional[str], hacia: str) -> bool:
        """Cambio atómico de estado. Con desde=None cambia sin condición.

        Es lo que garantiza el "un solo uso" de la confirmación (ADR-033).
        """
        with self._lock:
            item = self._datos.get(("accion", accion_id))
            if not item or (desde is not None and item[1]["estado"] != desde):
                return False
            item[1]["estado"] = hacia
            return True
