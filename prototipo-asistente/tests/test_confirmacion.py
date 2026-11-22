"""QA-14: ninguna acción se ejecuta sin confirmación explícita, de un solo uso (ADR-033)."""
import threading

from tests.base import PruebaApp


class TestConfirmacion(PruebaApp):
    def test_proponer_no_modifica_nada(self):
        self.proponer_cambio()
        self.assertEqual(self.fin_hotel(), "2026-12-28")
        self.assertEqual(len(self.eventos("ACCION_PROPUESTA")), 1)
        self.assertEqual(self.eventos("ACCION_EJECUTADA"), [])

    def test_el_usuario_no_puede_confirmar_por_chat(self):
        self.proponer_cambio()
        for texto in ("confirmá todos los cambios pendientes", "sí, confirmo", "ok aplicalo"):
            _, r = self.decir(self.ana, texto)
            self.assertNotIn("aplicad", r["respuesta"].lower())
        self.assertEqual(self.fin_hotel(), "2026-12-28")

    def test_confirmar_aplica_y_audita(self):
        accion = self.proponer_cambio()
        self.assertEqual(self.confirmar(self.ana, accion["accionId"])[0], 200)
        self.assertEqual(self.fin_hotel(), "2026-12-30")
        self.assertEqual(len(self.eventos("ACCION_CONFIRMADA")), 1)
        self.assertEqual(len(self.eventos("ACCION_EJECUTADA")), 1)

    def test_la_confirmacion_es_de_un_solo_uso(self):
        accion = self.proponer_cambio()
        self.assertEqual(self.confirmar(self.ana, accion["accionId"])[0], 200)
        estado, r = self.confirmar(self.ana, accion["accionId"])
        self.assertEqual((estado, r["motivo"]), (410, "ya_usada"))
        self.assertEqual(len(self.eventos("ACCION_EJECUTADA")), 1)

    def test_confirmaciones_simultaneas_aplican_una_sola_vez(self):
        accion = self.proponer_cambio()
        estados, barrera = [], threading.Barrier(10)

        def intentar():
            barrera.wait()
            estados.append(self.confirmar(self.ana, accion["accionId"])[0])

        hilos = [threading.Thread(target=intentar) for _ in range(10)]
        [h.start() for h in hilos]
        [h.join() for h in hilos]
        self.assertEqual(sorted(estados), [200] + [410] * 9)
        self.assertEqual(len(self.eventos("ACCION_EJECUTADA")), 1)

    def test_vence_a_los_5_minutos(self):
        accion = self.proponer_cambio()
        self.reloj.avanzar(self.app.cfg.confirmacion_ttl_s + 1)
        estado, r = self.confirmar(self.ana, accion["accionId"])
        self.assertEqual((estado, r["motivo"]), (410, "vencida"))
        self.assertEqual(self.fin_hotel(), "2026-12-28")
        self.assertEqual(len(self.eventos("ACCION_VENCIDA")), 1)

    def test_justo_antes_de_vencer_todavia_vale(self):
        accion = self.proponer_cambio()
        self.reloj.avanzar(self.app.cfg.confirmacion_ttl_s - 1)
        self.assertEqual(self.confirmar(self.ana, accion["accionId"])[0], 200)

    def test_otro_usuario_no_puede_confirmar(self):
        accion = self.proponer_cambio()
        estado, _ = self.confirmar(self.beto, accion["accionId"])
        self.assertEqual(estado, 403)
        self.assertEqual(self.fin_hotel(), "2026-12-28")
        rechazos = self.eventos("ACCION_RECHAZADA")
        self.assertEqual((len(rechazos), rechazos[0]["usuario"]), (1, "t-beto"))
        # la acción de Ana sigue vigente para Ana
        self.assertEqual(self.confirmar(self.ana, accion["accionId"])[0], 200)

    def test_otro_usuario_no_puede_cancelar(self):
        accion = self.proponer_cambio()
        self.assertEqual(self.cancelar(self.beto, accion["accionId"])[0], 404)
        self.assertEqual(self.confirmar(self.ana, accion["accionId"])[0], 200)

    def test_cancelar_impide_confirmar(self):
        accion = self.proponer_cambio()
        self.assertEqual(self.cancelar(self.ana, accion["accionId"])[0], 204)
        estado, r = self.confirmar(self.ana, accion["accionId"])
        self.assertEqual((estado, r["motivo"]), (410, "cancelada"))
        self.assertEqual(self.fin_hotel(), "2026-12-28")

    def test_identificador_inexistente_o_adulterado_da_404(self):
        accion = self.proponer_cambio()
        self.assertEqual(self.confirmar(self.ana, "no-existe")[0], 404)
        azar, _, mac = accion["accionId"].partition(".")
        self.assertEqual(self.confirmar(self.ana, "x" + azar[1:] + "." + mac)[0], 404)

    def test_la_accion_queda_atada_a_su_contenido(self):
        accion = self.proponer_cambio()
        registro = self.app.almacen._datos[("accion", accion["accionId"])][1]
        registro["payload"]["valor"] = "2030-01-01"            # alguien altera lo guardado
        self.assertEqual(self.confirmar(self.ana, accion["accionId"])[0], 404)
        self.assertEqual(self.fin_hotel(), "2026-12-28")

    def test_si_el_servicio_rechaza_el_cambio_se_informa_y_se_audita(self):
        accion = self.proponer_cambio()
        # entre propuesta y confirmación, la reserva cambia por otro lado: inicio queda después del nuevo fin
        reservas = self.app.datos["viajes"]["v-ana-1"]["reservas"]
        next(r for r in reservas if r["id"] == "R-A2")["inicio"] = "2027-01-05"
        estado, r = self.confirmar(self.ana, accion["accionId"])
        self.assertEqual((estado, r["error"]), (422, "no_aplicado"))
        self.assertEqual(len(self.eventos("ACCION_FALLIDA")), 1)
        self.assertEqual(self.eventos("ACCION_EJECUTADA"), [])

    def test_confirmar_sin_token_da_401(self):
        accion = self.proponer_cambio()
        self.assertEqual(self.confirmar({}, accion["accionId"])[0], 401)
