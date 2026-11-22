"""Guide Catalog (ADR-031, decisión D8): respuestas guiadas a problemas menores (UC12).

Contenido fijo y revisado por el equipo: no lo genera el modelo. Los textos son
de ejemplo; en el sistema real los mantendría el equipo de soporte.
Cada guía se activa si TODAS las raíces de alguno de sus grupos aparecen en el mensaje.
"""
from __future__ import annotations

from typing import Optional

from .minimizador import normalizar
import re

GUIAS = (
    {
        "id": "G-01",
        "titulo": "Cómo restablecer tu contraseña",
        "grupos": (("contrasen",), ("clave", "olvid"), ("clave", "restablec")),
        "pasos": ("En la pantalla de ingreso tocá «Olvidé mi contraseña».",
                  "Ingresá tu email y abrí el enlace que te enviamos.",
                  "Elegí una contraseña nueva y volvé a ingresar."),
    },
    {
        "id": "G-02",
        "titulo": "Una reserva de tu correo no aparece en el viaje",
        "grupos": (("correo", "importa"), ("correo", "aparec"), ("mail", "importa"),
                   ("mail", "aparec"), ("reserv", "aparec"), ("reserv", "import")),
        "pasos": ("Revisá en Ajustes > Correo que la cuenta esté conectada.",
                  "Pedí una nueva lectura con «Sincronizar ahora».",
                  "Si sigue sin aparecer, cargala a mano desde el panel (guía de carga manual)."),
    },
    {
        "id": "G-03",
        "titulo": "Cómo configurar las notificaciones",
        "grupos": (("notificacion",), ("aviso",), ("alerta",)),
        "pasos": ("Entrá a Ajustes > Notificaciones.",
                  "Elegí qué avisos querés recibir (cambios de vuelo, recordatorios).",
                  "Guardá los cambios."),
    },
    {
        "id": "G-04",
        "titulo": "Cómo cargar una reserva a mano",
        "grupos": (("carg", "reserv"), ("agreg", "reserv"), ("anad", "reserv"), ("reserv", "manual")),
        "pasos": ("Abrí el viaje y tocá «Agregar reserva».",
                  "Elegí el tipo (vuelo, alojamiento, otro) y completá fechas y proveedor.",
                  "Guardá: la reserva queda marcada como cargada manualmente."),
    },
)


class CatalogoGuias:
    def buscar(self, texto: str) -> Optional[dict]:
        tokens = re.findall(r"[a-z0-9]+", normalizar(texto))
        for guia in GUIAS:
            for grupo in guia["grupos"]:
                if all(any(t.startswith(raiz) for t in tokens) for raiz in grupo):
                    return guia
        return None

    @staticmethod
    def texto(guia: dict) -> str:
        pasos = "\n".join(f"{i}. {p}" for i, p in enumerate(guia["pasos"], 1))
        return f"{guia['titulo']}:\n{pasos}"
