"""Data Minimizer (ADR-035): único camino de los datos hacia el modelo.

Lista blanca de campos: lo que no está nombrado acá NO sale hacia el modelo.
Quedan afuera: datos personales del viajero, códigos de confirmación y el campo
`notas` (texto libre de terceros: vector de inyección indirecta, CRN-18).
"""
from __future__ import annotations

import re
import unicodedata

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
NUMERO_LARGO = re.compile(r"(?<!\w)\+?\d(?:[\s().-]?\d){8,}(?!\w)")  # teléfonos, tarjetas, documentos
CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")

CAMPOS_VIAJE_RESUMEN = ("id", "nombre", "estado", "fechaInicio", "fechaFin")
CAMPOS_RESERVA = ("id", "tipo", "proveedor", "estado", "inicio", "fin")


def normalizar(texto: str) -> str:
    """Minúsculas y sin acentos (para reglas por palabras clave)."""
    sin = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sin if not unicodedata.combining(c)).lower()


def limpiar_texto(texto, largo: int = 1000) -> str:
    """Redacta emails y números largos y quita caracteres de control."""
    texto = CONTROL.sub(" ", str(texto))
    texto = EMAIL.sub("[email]", texto)
    texto = NUMERO_LARGO.sub("[número]", texto)
    return texto.strip()[:largo]


def _campo(valor) -> str:
    return limpiar_texto(valor, 80) if isinstance(valor, str) else valor


def viajes(lista: list) -> list:
    return [{c: _campo(v.get(c)) for c in CAMPOS_VIAJE_RESUMEN} for v in lista]


def viaje(detalle: dict) -> dict:
    salida = {c: _campo(detalle.get(c)) for c in CAMPOS_VIAJE_RESUMEN}
    salida["reservas"] = [{c: _campo(r.get(c)) for c in CAMPOS_RESERVA}
                          for r in detalle.get("reservas", [])]
    return salida
