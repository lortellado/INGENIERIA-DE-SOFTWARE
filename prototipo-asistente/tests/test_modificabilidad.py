"""QA-16: cambiar el proveedor del modelo sin tocar los demás componentes (ADR-034)."""
import os
import unittest

from tests.base import PruebaApp
from trotamundos_asistente.adaptadores import ModeloGuionado

PAQUETE = os.path.join(os.path.dirname(__file__), "..", "trotamundos_asistente")
COMPONENTES = ("asistente", "herramientas", "confirmaciones", "minimizador", "politica",
               "guias", "almacen", "limites", "auditoria", "modelo", "sesion")


class TestIntercambioDeAdaptador(PruebaApp):
    def test_otro_adaptador_cumple_el_mismo_contrato_sin_cambios_en_el_resto(self):
        def otro_proveedor(contexto, herramientas):
            ultimo = contexto["mensajes"][-1]
            if ultimo["rol"] == "usuario":
                return {"tipo": "herramienta", "nombre": "consultar_viajes", "argumentos": {}}
            return {"tipo": "texto", "texto": f"(otro proveedor) {len(ultimo['contenido']['viajes'])} viaje(s)"}

        self.crear(modelo=ModeloGuionado(otro_proveedor))
        estado, r = self.decir(self.ana, "lo que sea")
        self.assertEqual((estado, r["respuesta"]), (200, "(otro proveedor) 1 viaje(s)"))

    def test_un_adaptador_no_puede_saltarse_las_reglas_del_sistema(self):
        malicioso = ModeloGuionado(lambda c, h: {"tipo": "herramienta", "nombre": "confirmar_accion",
                                                 "argumentos": {"accionId": "x"}})
        self.crear(modelo=malicioso)
        estado, r = self.decir(self.ana, "hola")
        self.assertEqual(estado, 200)
        self.assertEqual(len(self.eventos("HERRAMIENTA_RECHAZADA")), 5)

    def test_las_herramientas_se_ofrecen_al_adaptador_en_formato_neutro(self):
        vistas = []
        self.crear(modelo=ModeloGuionado(lambda c, h: vistas.append(h) or {"tipo": "texto", "texto": "ok"}))
        self.decir(self.ana, "hola")
        self.assertEqual([d["nombre"] for d in vistas[0]],
                         ["consultar_viajes", "consultar_viaje", "proponer_cambio", "solicitar_derivacion"])


class TestAcoplamiento(unittest.TestCase):
    def test_ningun_componente_conoce_un_adaptador_concreto(self):
        for nombre in COMPONENTES:
            with open(os.path.join(PAQUETE, nombre + ".py"), encoding="utf-8") as f:
                fuente = f.read()
            for concreto in ("ModeloSimulado", "ModeloGuionado", "ModeloQueFalla", "adaptadores"):
                self.assertNotIn(concreto, fuente, f"{nombre}.py menciona {concreto}")

    def test_solo_api_y_main_importan_adaptadores(self):
        usan = []
        for nombre in sorted(os.listdir(PAQUETE)):
            if nombre.endswith(".py"):
                with open(os.path.join(PAQUETE, nombre), encoding="utf-8") as f:
                    if "adaptadores" in f.read() and nombre != "adaptadores.py":
                        usan.append(nombre)
        self.assertEqual(usan, ["__main__.py", "api.py"])
