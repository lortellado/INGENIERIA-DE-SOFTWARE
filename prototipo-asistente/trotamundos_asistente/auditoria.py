"""Audit Publisher (ADR-033, ADR-035): publica eventos al Audit Log existente.

Los eventos nunca llevan el texto libre de la conversación, solo identificadores.
La lista de eventos debe coincidir con specs/asyncapi.yaml (hay una prueba que lo verifica).
"""
from __future__ import annotations

EVENTOS = (
    "ACCION_PROPUESTA",
    "ACCION_CONFIRMADA",
    "ACCION_EJECUTADA",
    "ACCION_FALLIDA",
    "ACCION_CANCELADA",
    "ACCION_VENCIDA",
    "ACCION_RECHAZADA",
    "DERIVACION_SOLICITADA",
    "HERRAMIENTA_RECHAZADA",
    "MODELO_NO_DISPONIBLE",
)


class PublicadorAuditoria:
    def __init__(self, destino):
        self._destino = destino
        self.errores = 0

    def publicar(self, evento: str, usuario: str, detalle: dict = None) -> None:
        if evento not in EVENTOS:
            raise ValueError(f"evento de auditoría desconocido: {evento}")
        try:
            self._destino.registrar(evento, usuario, detalle or {})
        except Exception:  # un fallo de auditoría no debe tumbar la conversación
            self.errores += 1
