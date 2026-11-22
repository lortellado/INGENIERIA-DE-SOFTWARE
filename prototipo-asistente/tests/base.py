"""Utilidades comunes de las pruebas."""
import unittest

from trotamundos_asistente.adaptadores import ModeloSimulado
from trotamundos_asistente.api import Aplicacion
from trotamundos_asistente.config import Config, RelojManual
from trotamundos_asistente.modelo import ModeloPort


class ModeloEspia(ModeloPort):
    """Envuelve a otro adaptador y guarda todo lo que el modelo llega a ver."""

    def __init__(self, delegado=None):
        self.delegado = delegado or ModeloSimulado()
        self.contextos = []

    def generar(self, contexto, herramientas):
        self.contextos.append(repr(contexto))
        return self.delegado.generar(contexto, herramientas)

    @property
    def todo_lo_visto(self) -> str:
        return "\n".join(self.contextos)


class PruebaApp(unittest.TestCase):
    """Crea una Aplicacion con reloj manual y tokens de ana y beto."""

    def crear(self, modelo=None, **cfg):
        self.reloj = RelojManual()
        self.app = Aplicacion(modelo=modelo, config=Config(**cfg), reloj=self.reloj)
        self.ana = self.cabeceras("ana")
        self.beto = self.cabeceras("beto")
        return self.app

    def setUp(self):
        self.crear()

    def cabeceras(self, usuario):
        return {"Authorization": "Bearer " + self.app.idp.login(usuario)}

    def decir(self, cab, texto, app=None):
        return (app or self.app).manejar("POST", "/v1/asistente/mensajes", cab, {"mensaje": texto})

    def confirmar(self, cab, accion_id):
        return self.app.manejar("POST", f"/v1/asistente/acciones/{accion_id}/confirmar", cab)

    def cancelar(self, cab, accion_id):
        return self.app.manejar("POST", f"/v1/asistente/acciones/{accion_id}/cancelar", cab)

    def proponer_cambio(self, cab=None):
        """Pide mover la salida del hotel de Ana; devuelve la accionPendiente."""
        estado, r = self.decir(cab or self.ana, "cambiá la salida del hotel del viaje v-ana-1 al 2026-12-30")
        self.assertEqual(estado, 200)
        self.assertIn("accionPendiente", r)
        return r["accionPendiente"]

    def fin_hotel(self):
        reservas = self.app.datos["viajes"]["v-ana-1"]["reservas"]
        return next(r for r in reservas if r["id"] == "R-A2")["fin"]

    def eventos(self, nombre):
        return self.app.audit_log.eventos(nombre)
