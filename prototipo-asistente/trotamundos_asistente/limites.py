"""Límites del asistente (ADR-036): tasa por usuario y tope de turnos simultáneos.

El tope de concurrencia es propio del asistente: protege al resto del sistema
(el panel nunca pasa por acá) cuando hay un pico de uso del chat.
"""
from __future__ import annotations

import math
import threading
from collections import deque


class LimitadorPorUsuario:
    def __init__(self, reloj, maximo: int, ventana_s: float = 60.0):
        self._reloj = reloj
        self._max = maximo
        self._ventana = ventana_s
        self._pedidos: dict = {}
        self._lock = threading.Lock()

    def intentar(self, usuario: str):
        """Devuelve (permitido, segundos_para_reintentar)."""
        with self._lock:
            ahora = self._reloj.ahora()
            cola = self._pedidos.setdefault(usuario, deque())
            while cola and ahora - cola[0] >= self._ventana:
                cola.popleft()
            if len(cola) >= self._max:
                return False, max(1, math.ceil(self._ventana - (ahora - cola[0])))
            cola.append(ahora)
            return True, 0


class CupoConcurrente:
    def __init__(self, maximo: int):
        self._sem = threading.BoundedSemaphore(maximo)

    def tomar(self) -> bool:
        return self._sem.acquire(blocking=False)

    def soltar(self) -> None:
        self._sem.release()
