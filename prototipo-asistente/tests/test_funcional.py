"""UC10 a UC13: casos de uso del asistente."""
from tests.base import PruebaApp


class TestConsultas(PruebaApp):          # UC10
    def test_lista_viajes_propios(self):
        estado, r = self.decir(self.ana, "mis viajes")
        self.assertEqual(estado, 200)
        self.assertIn("Madrid en diciembre", r["respuesta"])

    def test_detalle_de_un_viaje(self):
        _, r = self.decir(self.ana, "mostrame el viaje v-ana-1")
        self.assertIn("Hotel Gran Vía", r["respuesta"])
        self.assertIn("R-A2", r["respuesta"])

    def test_mensaje_vacio_o_largo_es_400(self):
        self.assertEqual(self.decir(self.ana, "   ")[0], 400)
        self.assertEqual(self.decir(self.ana, "x" * 1001)[0], 400)

    def test_el_historial_se_conserva_y_vence_a_las_24h(self):
        self.decir(self.ana, "mis viajes")
        self.assertEqual(len(self.app.almacen.obtener("t-ana")["mensajes"]), 2)
        self.reloj.avanzar(self.app.cfg.conversacion_ttl_s + 1)
        self.assertEqual(self.app.almacen.obtener("t-ana")["mensajes"], [])


class TestCambioDeReserva(PruebaApp):    # UC11 (flujo feliz; las garantías están en test_confirmacion)
    def test_cambio_con_confirmacion_de_punta_a_punta(self):
        accion = self.proponer_cambio()
        self.assertIn("2026-12-30", accion["resumen"])
        self.assertEqual(self.fin_hotel(), "2026-12-28")        # todavía nada cambió
        estado, r = self.confirmar(self.ana, accion["accionId"])
        self.assertEqual((estado, r["estado"]), (200, "aplicada"))
        self.assertEqual(self.fin_hotel(), "2026-12-30")

    def test_acepta_fecha_dd_mm_aaaa(self):
        _, r = self.decir(self.ana, "cambiá la salida del hotel del viaje v-ana-1 al 30/12/2026")
        self.assertIn("2026-12-30", r["accionPendiente"]["resumen"])

    def test_sin_id_de_viaje_usa_el_unico_viaje(self):
        _, r = self.decir(self.ana, "pasame la salida del hotel al 2026-12-30")
        self.assertIn("accionPendiente", r)       # encadena consultar_viajes -> consultar_viaje -> proponer_cambio

    def test_fechas_incoherentes_no_generan_accion(self):
        _, r = self.decir(self.ana, "cambiá la entrada del hotel del viaje v-ana-1 al 2027-01-01")
        self.assertNotIn("accionPendiente", r)
        self.assertIn("después del fin", r["respuesta"])


class TestGuias(PruebaApp):              # UC12
    def test_guias_del_catalogo(self):
        casos = {"olvidé mi contraseña": "G-01", "mi reserva del correo no aparece": "G-02",
                 "cómo configuro las notificaciones": "G-03", "quiero cargar una reserva": "G-04"}
        for texto, guia in casos.items():
            _, r = self.decir(self.ana, texto)
            self.assertEqual(r.get("guia"), guia, texto)

    def test_las_guias_no_usan_el_modelo(self):
        from tests.base import ModeloEspia
        espia = ModeloEspia()
        self.crear(modelo=espia)
        self.decir(self.ana, "olvidé mi contraseña")
        self.assertEqual(espia.contextos, [])


class TestDerivacion(PruebaApp):         # UC13
    def test_pedido_riesgoso_se_deriva_a_la_agencia(self):
        for texto in ("quiero cancelar mi vuelo", "necesito un reembolso", "es una emergencia",
                      "quiero hablar con una persona"):
            _, r = self.decir(self.ana, texto)
            self.assertIn("derivacion", r, texto)
        casos = self.app.agencia.casos
        self.assertEqual(len(casos), 4)
        self.assertTrue(all(c["agencia"] == "Agencia Sur" for c in casos))

    def test_sin_agencia_preferida_no_inventa_un_caso(self):
        _, r = self.decir(self.beto, "quiero un reembolso")
        self.assertNotIn("derivacion", r)
        self.assertIn("no tenés una agencia", r["respuesta"])
        self.assertEqual(self.app.agencia.casos, [])

    def test_dos_mensajes_incomprensibles_seguidos_derivan(self):
        _, r1 = self.decir(self.ana, "blablabla")
        _, r2 = self.decir(self.ana, "asdfgh")
        self.assertNotIn("derivacion", r1)
        self.assertIn("derivacion", r2)

    def test_un_mensaje_entendido_reinicia_el_conteo(self):
        self.decir(self.ana, "blablabla")
        self.decir(self.ana, "mis viajes")
        _, r = self.decir(self.ana, "asdfgh")
        self.assertNotIn("derivacion", r)

    def test_la_derivacion_no_envia_datos_personales_a_la_agencia(self):
        self.decir(self.ana, "quiero un reembolso, mi mail es ana@example.com y mi tarjeta 4111 1111 1111 1111")
        resumen = self.app.agencia.casos[0]["resumen"]
        self.assertNotIn("ana@example.com", resumen)
        self.assertNotIn("4111", resumen)


class TestLenguajeNatural(PruebaApp):    # UC10/UC11 sin necesidad de escribir identificadores
    def test_frases_simples_para_ver_los_viajes(self):
        for texto in ("mis viajes", "ver mis viajes", "Mostrame mis viajes", "quiero ver mi viaje",
                      "mis reservas", "qué tengo reservado", "mis vuelos", "mis vacaciones", "mi próximo viaje"):
            _, r = self.decir(self.ana, texto)
            self.assertIn("Madrid en diciembre", r["respuesta"], texto)

    def test_se_puede_elegir_el_viaje_por_su_nombre(self):
        _, r = self.decir(self.ana, "mostrame el viaje de Madrid")
        self.assertIn("R-A2", r["respuesta"])                    # detalle, no solo la lista

    def test_se_puede_pedir_un_cambio_sin_identificadores(self):
        _, r = self.decir(self.ana, "cambiá la salida del hotel de Madrid al 30/12/2026")
        self.assertIn("2026-12-30", r["accionPendiente"]["resumen"])

    def test_nombrar_un_viaje_ajeno_no_lo_revela(self):
        _, r = self.decir(self.ana, "mostrame el hotel de Roma")
        self.assertNotIn("Roma", r["respuesta"])
        self.assertIn("Madrid en diciembre", r["respuesta"])     # solo ve lo suyo
