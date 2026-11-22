"""Contrato: lo que implementa la API coincide con specs/openapi.yaml y specs/asyncapi.yaml (ADR-026)."""
import json
import os
import re
import threading
import unittest
import urllib.error
import urllib.request

from tests.base import PruebaApp
from trotamundos_asistente.adaptadores import ModeloQueFalla
from trotamundos_asistente.api import PLANTILLAS_ASISTENTE, Aplicacion
from trotamundos_asistente.auditoria import EVENTOS
from trotamundos_asistente.servidor import crear_servidor

SPECS = os.path.join(os.path.dirname(__file__), "..", "specs")


def leer(nombre):
    with open(os.path.join(SPECS, nombre), encoding="utf-8") as f:
        return f.read()


def rutas_documentadas():
    """Lector mínimo del openapi.yaml (sin dependencias): {(MÉTODO, ruta, estado)}."""
    docs, ruta, metodo = set(), None, None
    for linea in leer("openapi.yaml").splitlines():
        if linea.startswith("components:"):
            break
        if m := re.match(r"^  (/\S+):\s*$", linea):
            ruta = m.group(1)
        elif m := re.match(r"^    (get|post|put|patch|delete):\s*$", linea):
            metodo = m.group(1).upper()
        elif m := re.match(r"^        '(\d{3})':", linea):
            docs.add((metodo, ruta, int(m.group(1))))
    return docs


class TestOpenAPI(PruebaApp):
    def test_las_rutas_documentadas_son_las_implementadas(self):
        documentadas = {(m, r) for m, r, _ in rutas_documentadas()}
        self.assertEqual(documentadas, set(PLANTILLAS_ASISTENTE))

    def test_toda_respuesta_observada_esta_documentada(self):
        a = self.app
        accion = self.proponer_cambio()
        otra = self.proponer_cambio()                           # segunda propuesta, antes de aplicar la primera
        self.confirmar(self.ana, accion["accionId"])            # 200
        self.confirmar(self.ana, accion["accionId"])            # 410
        self.confirmar(self.ana, "no-existe")                   # 404
        self.confirmar(self.beto, otra["accionId"])             # 403
        self.cancelar(self.ana, otra["accionId"])               # 204
        self.cancelar(self.ana, otra["accionId"])               # 404
        self.decir({}, "hola")                                  # 401
        self.decir(self.ana, "")                                # 400
        for _ in range(a.cfg.pedidos_por_minuto + 1):           # 429
            self.decir(self.beto, "mis viajes")
        caido = Aplicacion(modelo=ModeloQueFalla("error"))      # 503
        cab = {"Authorization": "Bearer " + caido.idp.login("ana")}
        self.decir(cab, "hola", app=caido)

        documentadas = rutas_documentadas()
        observados = {(m, p, e) for m, p, e in a.observados + caido.observados}
        self.assertEqual(observados - documentadas, set())
        # las respuestas principales de cada ruta se ejercitaron al menos una vez
        for esperado in [("POST", "/v1/asistente/mensajes", s) for s in (200, 400, 401, 429, 503)] + \
                        [("POST", "/v1/asistente/acciones/{accionId}/confirmar", s) for s in (200, 403, 404, 410)] + \
                        [("POST", "/v1/asistente/acciones/{accionId}/cancelar", s) for s in (204, 404)]:
            self.assertIn(esperado, observados)

    def test_las_respuestas_cumplen_los_esquemas_documentados(self):
        _, r = self.decir(self.ana, "cambiá la salida del hotel del viaje v-ana-1 al 2026-12-30")
        self.assertEqual(set(r["accionPendiente"]), {"accionId", "resumen", "vencimiento"})
        self.assertTrue(re.fullmatch(r"\d{4}-\d{2}-\d{2}T[\d:.]+Z", r["accionPendiente"]["vencimiento"]))
        _, r = self.decir(self.ana, "quiero un reembolso")
        self.assertEqual(set(r["derivacion"]), {"casoId", "agencia"})
        caido = Aplicacion(modelo=ModeloQueFalla("error"))
        cab = {"Authorization": "Bearer " + caido.idp.login("ana")}
        _, r = self.decir(cab, "hola", app=caido)
        self.assertEqual(set(r), {"error", "mensaje", "alternativas"})


class TestAsyncAPI(unittest.TestCase):
    def test_los_eventos_del_codigo_son_los_de_la_spec(self):
        enum = re.findall(r"^\s+- ([A-Z_]+)\s*$", leer("asyncapi.yaml"), re.M)
        self.assertEqual(sorted(enum), sorted(EVENTOS))


class TestHTTPReal(unittest.TestCase):
    """Levanta el servidor de verdad y le habla por HTTP."""

    @classmethod
    def setUpClass(cls):
        cls.app = Aplicacion()
        cls.srv = crear_servidor(cls.app, puerto=0)
        cls.url = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def pedir(self, metodo, ruta, cuerpo=None, token=None):
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        req = urllib.request.Request(self.url + ruta, data=datos, method=metodo)
        if token:
            req.add_header("Authorization", "Bearer " + token)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def test_flujo_completo_por_http(self):
        _, login = self.pedir("POST", "/dev/login", {"usuario": "ana"})
        t = login["token"]
        self.assertEqual(self.pedir("POST", "/v1/asistente/mensajes", {"mensaje": "hola"})[0], 401)
        estado, r = self.pedir("POST", "/v1/asistente/mensajes", {"mensaje": "mis viajes"}, t)
        self.assertEqual(estado, 200)
        _, r = self.pedir("POST", "/v1/asistente/mensajes",
                          {"mensaje": "cambiá la salida del hotel del viaje v-ana-1 al 2026-12-30"}, t)
        accion = r["accionPendiente"]["accionId"]
        self.assertEqual(self.pedir("POST", f"/v1/asistente/acciones/{accion}/confirmar", None, t)[0], 200)
        self.assertEqual(self.pedir("POST", f"/v1/asistente/acciones/{accion}/confirmar", None, t)[0], 410)

    def test_ruta_inexistente_y_json_invalido(self):
        _, login = self.pedir("POST", "/dev/login", {"usuario": "beto"})
        self.assertEqual(self.pedir("GET", "/nada", None, login["token"])[0], 404)
        req = urllib.request.Request(self.url + "/v1/asistente/mensajes", data=b"{no es json", method="POST")
        req.add_header("Authorization", "Bearer " + login["token"])
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)
