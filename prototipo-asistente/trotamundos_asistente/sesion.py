"""Sesión autenticada: lo ÚNICO que el asistente sabe de la identidad (ADR-032).

La identidad sale del token verificado. Ninguna herramienta ni el modelo
reciben ni eligen un identificador de usuario.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Sesion:
    traveler_id: str
    token: str
