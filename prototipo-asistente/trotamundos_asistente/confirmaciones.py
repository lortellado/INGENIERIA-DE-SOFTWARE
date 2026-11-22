"""Action Confirmation Manager (ADR-033): confirmación en dos pasos controlada por el sistema.

Una acción pendiente es: de un solo uso, atada a su contenido y a su dueño, y con vencimiento.
El modelo solo puede PROPONER; confirmar es un endpoint que llama la persona
(no existe ninguna herramienta que confirme).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone

PENDIENTE, CONSUMIDA, CANCELADA, VENCIDA = "PENDIENTE", "CONSUMIDA", "CANCELADA", "VENCIDA"


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).isoformat().replace("+00:00", "Z")


class GestorConfirmaciones:
    def __init__(self, almacen, reloj, secreto: bytes, ttl_s: int, auditoria):
        self._almacen, self._reloj, self._secreto = almacen, reloj, secreto
        self._ttl, self._auditoria = ttl_s, auditoria

    def _mac(self, azar: str, traveler: str, payload: dict, vence: float) -> str:
        contenido = f"{azar}|{traveler}|{json.dumps(payload, sort_keys=True)}|{vence}".encode()
        firma = hmac.new(self._secreto, contenido, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(firma).decode().rstrip("=")[:22]

    def proponer(self, traveler: str, payload: dict, resumen: str) -> dict:
        azar = secrets.token_urlsafe(12)
        vence = self._reloj.ahora() + self._ttl
        accion_id = f"{azar}.{self._mac(azar, traveler, payload, vence)}"
        self._almacen.guardar_accion(accion_id, {
            "traveler": traveler, "payload": payload, "resumen": resumen,
            "vence": vence, "estado": PENDIENTE})
        self._auditoria.publicar("ACCION_PROPUESTA", traveler, {"accionId": accion_id, **payload})
        return {"accionId": accion_id, "resumen": resumen, "vencimiento": _iso(vence)}

    def _integra(self, accion_id: str, accion: dict) -> bool:
        azar, _, mac = accion_id.partition(".")
        esperado = self._mac(azar, accion["traveler"], accion["payload"], accion["vence"])
        return hmac.compare_digest(mac, esperado)

    def consumir(self, traveler: str, accion_id: str):
        """Valida y consume la acción. Devuelve (codigo, accion); codigo 'ok' si puede ejecutarse."""
        accion = self._almacen.obtener_accion(accion_id)
        if accion is None:
            return "no_encontrada", None
        if accion["traveler"] != traveler:
            self._auditoria.publicar("ACCION_RECHAZADA", traveler,
                                     {"accionId": accion_id, "motivo": "otro_usuario"})
            return "otro_usuario", None
        if not self._integra(accion_id, accion):
            return "no_encontrada", None
        if accion["estado"] == CONSUMIDA:
            return "ya_usada", None
        if accion["estado"] == CANCELADA:
            return "cancelada", None
        if accion["estado"] == VENCIDA or self._reloj.ahora() >= accion["vence"]:
            if self._almacen.cambiar_estado(accion_id, PENDIENTE, VENCIDA):
                self._auditoria.publicar("ACCION_VENCIDA", traveler, {"accionId": accion_id})
            return "vencida", None
        if not self._almacen.cambiar_estado(accion_id, PENDIENTE, CONSUMIDA):  # atómico: un solo uso
            return "ya_usada", None
        return "ok", accion

    def cancelar(self, traveler: str, accion_id: str) -> bool:
        accion = self._almacen.obtener_accion(accion_id)
        if accion is None or accion["traveler"] != traveler or accion["estado"] != PENDIENTE:
            return False
        if self._almacen.cambiar_estado(accion_id, PENDIENTE, CANCELADA):
            self._auditoria.publicar("ACCION_CANCELADA", traveler, {"accionId": accion_id})
            return True
        return False
