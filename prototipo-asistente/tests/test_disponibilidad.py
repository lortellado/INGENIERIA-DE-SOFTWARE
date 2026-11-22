"""QA-15: si el modelo falla, el resto del sistema sigue y el usuario recibe alternativas (ADR-034)."""
import time

from tests.base import PruebaApp
from trotamundos_asistente.adaptadores import ModeloQueFalla, ModeloSimulado


class TestModeloCaido(PruebaApp):
    def setUp(self):
        self.falla = ModeloQueFalla("error")
        self.crear(modelo=self.falla)

    def test_responde_503_con_alternativas(self):
        estado, r = self.decir(self.ana, "mis viajes")
        self.assertEqual(estado, 503)
        self.assertEqual({a["tipo"] for a in r["alternativas"]}, {"panel", "agencia"})
        self.assertEqual(len(self.eventos("MODELO_NO_DISPONIBLE")), 1)

    def test_el_panel_sigue_funcionando(self):
        self.decir(self.ana, "mis viajes")
        estado, r = self.app.manejar("GET", "/v1/viajeros/me/viajes", self.ana)
        self.assertEqual((estado, r["viajes"][0]["id"]), (200, "v-ana-1"))

    def test_guias_y_derivacion_funcionan_sin_modelo(self):
        _, g = self.decir(self.ana, "olvidé mi contraseña")
        _, d = self.decir(self.ana, "quiero un reembolso")
        self.assertEqual(g["guia"], "G-01")
        self.assertIn("derivacion", d)
        self.assertEqual(self.falla.llamadas, 0)

    def test_el_circuito_se_abre_y_deja_de_llamar_al_modelo(self):
        for _ in range(self.app.cfg.breaker_fallos):
            self.decir(self.ana, "mis viajes")
        self.assertEqual(self.falla.llamadas, 2)
        self.assertEqual(self.app.modelo.estado, "abierto")
        for _ in range(5):
            self.assertEqual(self.decir(self.ana, "mis viajes")[0], 503)
        self.assertEqual(self.falla.llamadas, 2)                 # no insistió

    def test_se_recupera_cuando_el_modelo_vuelve(self):
        for _ in range(2):
            self.decir(self.ana, "mis viajes")
        self.falla.modo = "ok"
        self.falla.delegado = ModeloSimulado()
        self.falla.demora_s = 0
        self.assertEqual(self.decir(self.ana, "mis viajes")[0], 503)    # aún abierto
        self.reloj.avanzar(self.app.cfg.breaker_pausa_s + 1)
        self.assertEqual(self.app.modelo.estado, "semiabierto")
        estado, r = self.decir(self.ana, "mis viajes")
        self.assertEqual(estado, 200)
        self.assertEqual(self.app.modelo.estado, "cerrado")

    def test_si_la_prueba_del_semiabierto_falla_se_reabre(self):
        for _ in range(2):
            self.decir(self.ana, "mis viajes")
        self.reloj.avanzar(self.app.cfg.breaker_pausa_s + 1)
        self.decir(self.ana, "mis viajes")                        # prueba: falla
        self.assertEqual(self.app.modelo.estado, "abierto")
        self.assertEqual(self.falla.llamadas, 3)


class TestTimeoutYRespuestasInvalidas(PruebaApp):
    def test_timeout_corta_la_espera(self):
        self.crear(modelo=ModeloQueFalla("lento", demora_s=1.0), modelo_timeout_s=0.1)
        t0 = time.time()
        estado, _ = self.decir(self.ana, "mis viajes")
        self.assertEqual(estado, 503)
        self.assertLess(time.time() - t0, 0.6)

    def test_respuesta_invalida_del_modelo_cuenta_como_fallo(self):
        self.crear(modelo=ModeloQueFalla("basura"))
        self.assertEqual(self.decir(self.ana, "mis viajes")[0], 503)

    def test_un_modelo_que_pide_tools_sin_fin_se_corta(self):
        from trotamundos_asistente.adaptadores import ModeloGuionado
        bucle = ModeloGuionado(lambda c, h: {"tipo": "herramienta", "nombre": "consultar_viajes", "argumentos": {}})
        self.crear(modelo=bucle)
        estado, r = self.decir(self.ana, "mis viajes")
        self.assertEqual(estado, 200)
        self.assertEqual(bucle.llamadas, self.app.cfg.max_pasos_por_turno)
        self.assertIn("No pude completar", r["respuesta"])
