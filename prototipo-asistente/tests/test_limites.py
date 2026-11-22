"""QA-17: el uso intensivo del chat no degrada al resto del sistema (ADR-036)."""
import threading
import time

from tests.base import PruebaApp
from trotamundos_asistente.adaptadores import ModeloGuionado


class TestTasaPorUsuario(PruebaApp):
    def test_supera_el_limite_y_recibe_429_con_retry_after(self):
        for _ in range(self.app.cfg.pedidos_por_minuto):
            self.assertEqual(self.decir(self.ana, "mis viajes")[0], 200)
        estado, r = self.decir(self.ana, "mis viajes")
        self.assertEqual(estado, 429)
        self.assertTrue(1 <= r["retryAfter"] <= 60)

    def test_el_limite_de_un_usuario_no_afecta_a_otro(self):
        for _ in range(self.app.cfg.pedidos_por_minuto + 1):
            self.decir(self.ana, "mis viajes")
        self.assertEqual(self.decir(self.beto, "mis viajes")[0], 200)

    def test_pasada_la_ventana_se_puede_volver_a_escribir(self):
        for _ in range(self.app.cfg.pedidos_por_minuto + 1):
            self.decir(self.ana, "mis viajes")
        self.reloj.avanzar(61)
        self.assertEqual(self.decir(self.ana, "mis viajes")[0], 200)

    def test_el_panel_no_pasa_por_el_limitador(self):
        for _ in range(self.app.cfg.pedidos_por_minuto + 5):
            self.decir(self.ana, "mis viajes")
        self.assertEqual(self.app.manejar("GET", "/v1/viajeros/me/viajes", self.ana)[0], 200)


class TestTopeDeConcurrencia(PruebaApp):
    def test_pico_de_usuarios_se_acota_y_el_panel_sigue_respondiendo(self):
        en_vuelo, pico, lock = [0], [0], threading.Lock()

        def lento(contexto, herramientas):
            with lock:
                en_vuelo[0] += 1
                pico[0] = max(pico[0], en_vuelo[0])
            time.sleep(0.3)
            with lock:
                en_vuelo[0] -= 1
            return {"tipo": "texto", "texto": "ok"}

        self.crear(modelo=ModeloGuionado(lento))
        tope = self.app.cfg.max_concurrentes
        usuarios = 3 * tope
        tokens = [{"Authorization": "Bearer " + self.app.idp.token_para(f"t-u{i}")} for i in range(usuarios)]
        estados, barrera = [], threading.Barrier(usuarios + 1)

        def pedir(cab):
            barrera.wait()
            estados.append(self.decir(cab, "hola")[0])

        hilos = [threading.Thread(target=pedir, args=(t,)) for t in tokens]
        [h.start() for h in hilos]
        barrera.wait()
        time.sleep(0.1)
        t0 = time.time()
        panel = self.app.manejar("GET", "/v1/viajeros/me/viajes", self.ana)[0]   # durante el pico
        demora_panel = time.time() - t0
        [h.join() for h in hilos]

        self.assertEqual(panel, 200)
        self.assertLess(demora_panel, 0.2)
        self.assertLessEqual(pico[0], tope)                  # nunca más de `tope` consultas al modelo a la vez
        self.assertGreaterEqual(estados.count(503), 1)       # el exceso se rechaza rápido
        self.assertEqual(set(estados), {200, 503})
        self.assertEqual(self.decir(self.ana, "hola")[0], 200)   # y se recupera al terminar el pico
