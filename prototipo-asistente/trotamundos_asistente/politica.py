"""Escalation Policy (ADR-031): reglas DETERMINISTAS de derivación a una persona.

No las decide el modelo: se evalúan antes de llamarlo, así que funcionan aunque
el modelo esté caído (QA-15) y no se pueden saltear con un prompt (QA-13).
"""
from __future__ import annotations

import re
from typing import Optional

from .minimizador import normalizar

REGLAS = (
    ("emergencia", re.compile(
        r"\b(emergencia|urgente|urgencia|accidente|hospital|robaron|robo|perdi\w* (?:el |mi )?pasaporte|varad\w+)\b")),
    ("pago_o_reembolso", re.compile(
        r"\b(reembols\w*|devoluci\w*|pago\w*|cobr\w*|tarjeta|factura\w*|cargo duplicado)\b")),
    ("cancelacion", re.compile(r"\bcancel\w*")),
    ("pedido_de_persona", re.compile(
        r"\b(reclamo\w*|queja\w*)\b|"
        r"\b(hablar|comunicar\w*|contactar\w*|quiero)\b.*\b(persona|humano|agente|asesor|agencia)\b")),
)


class PoliticaEscalamiento:
    def __init__(self, fallos_para_derivar: int):
        self._fallos = fallos_para_derivar

    def evaluar(self, texto: str) -> Optional[str]:
        """Devuelve el motivo de derivación o None."""
        norm = normalizar(texto)
        for motivo, patron in REGLAS:
            if patron.search(norm):
                return motivo
        return None

    def derivar_por_fallos(self, fallos_consecutivos: int) -> bool:
        return fallos_consecutivos >= self._fallos
