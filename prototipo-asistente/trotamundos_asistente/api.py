"""Conversation API (REST, contrato en specs/openapi.yaml) y armado de la aplicación.

`Aplicacion.manejar()` recibe método, ruta, cabeceras y cuerpo, y devuelve (estado, dict):
no depende del servidor HTTP, así que se prueba directo y también por HTTP real.
"""
from __future__ import annotations

import json
import re

from . import auth
from .adaptadores import ModeloSimulado
from .almacen import AlmacenConversaciones
from .asistente import Asistente
from .auditoria import PublicadorAuditoria
from .config import Config, Reloj
from .confirmaciones import GestorConfirmaciones
from .guias import CatalogoGuias
from .herramientas import EjecutorHerramientas
from .limites import CupoConcurrente, LimitadorPorUsuario
from .modelo import ModeloProtegido
from .politica import PoliticaEscalamiento
from .sesion import Sesion
from .simulators.pasarela import Pasarela, ProveedorIdentidad
from .simulators.servicios import (AgencyIntegration, AuditLog, TripCommand, TripQuery,
                                   datos_semilla)

PLANTILLAS_ASISTENTE = (
    ("POST", "/v1/asistente/mensajes"),
    ("POST", "/v1/asistente/acciones/{accionId}/confirmar"),
    ("POST", "/v1/asistente/acciones/{accionId}/cancelar"),
)


class Aplicacion:
    def __init__(self, modelo=None, config: Config = None, reloj=None, datos: dict = None):
        self.cfg = config or Config()
        self.reloj = reloj or Reloj()
        self.datos = datos or datos_semilla()
        # --- servicios EXISTENTES (simulados) ---
        self.trip_query = TripQuery(self.datos)
        self.trip_command = TripCommand(self.datos)
        self.agencia = AgencyIntegration(self.datos)
        self.audit_log = AuditLog(self.reloj)
        self.pasarela = Pasarela(self.cfg, self.reloj, self.trip_query, self.trip_command, self.agencia)
        self.idp = ProveedorIdentidad(self.cfg, self.reloj, self.datos)
        # --- Assistant Service (lo nuevo) ---
        self.auditoria = PublicadorAuditoria(self.audit_log)
        self.almacen = AlmacenConversaciones(self.reloj, self.cfg.conversacion_ttl_s)
        self.modelo = ModeloProtegido(modelo or ModeloSimulado(), self.reloj, self.cfg.modelo_timeout_s,
                                      self.cfg.breaker_fallos, self.cfg.breaker_pausa_s)
        self.gestor = GestorConfirmaciones(self.almacen, self.reloj, self.cfg.confirm_secret,
                                           self.cfg.confirmacion_ttl_s, self.auditoria)
        self.ejecutor = EjecutorHerramientas(self.pasarela, self.gestor, self.auditoria)
        self.asistente = Asistente(
            self.cfg, self.modelo, self.ejecutor, self.gestor,
            PoliticaEscalamiento(self.cfg.fallos_para_derivar), CatalogoGuias(), self.almacen,
            LimitadorPorUsuario(self.reloj, self.cfg.pedidos_por_minuto),
            CupoConcurrente(self.cfg.max_concurrentes), self.auditoria)
        self.observados: list = []   # (método, plantilla, estado): lo usa la prueba de contrato

    # ------------------------------------------------------------------ enrutado
    def manejar(self, metodo: str, ruta: str, cabeceras: dict = None, cuerpo=None):
        ruta = ruta.split("?")[0]
        cab = {k.lower(): v for k, v in (cabeceras or {}).items()}
        estado, resp, plantilla = self._enrutar(metodo.upper(), ruta, cab, cuerpo)
        if plantilla:
            self.observados.append((metodo.upper(), plantilla, estado))
        return estado, resp

    def _enrutar(self, metodo, ruta, cab, cuerpo):
        # Rutas de apoyo para la demo (no son parte del contrato del asistente)
        if metodo == "POST" and ruta == "/dev/login":
            datos = self._json(cuerpo)
            token = self.idp.login(datos.get("usuario")) if isinstance(datos, dict) else None
            return (200, {"token": token}, None) if token else (401, {"error": "usuario_desconocido"}, None)
        token = self._token(cab)
        if metodo == "GET" and ruta == "/v1/viajeros/me/viajes":
            return (*self.pasarela.listar_viajes(token), None)
        m = re.fullmatch(r"/v1/viajes/([^/]+)", ruta)
        if metodo == "GET" and m:
            return (*self.pasarela.detalle_viaje(token, m.group(1)), None)

        # Conversation API
        if metodo == "POST" and ruta == "/v1/asistente/mensajes":
            plantilla = "/v1/asistente/mensajes"
            sesion = self._sesion(token)
            if not sesion:
                return 401, {"error": "no_autenticado"}, plantilla
            datos = self._json(cuerpo)
            texto = datos.get("mensaje") if isinstance(datos, dict) else None
            if not isinstance(texto, str) or not texto.strip() or len(texto) > self.cfg.max_mensaje:
                return 400, {"error": "mensaje_invalido"}, plantilla
            return (*self.asistente.enviar_mensaje(sesion, texto), plantilla)

        m = re.fullmatch(r"/v1/asistente/acciones/([^/]+)/(confirmar|cancelar)", ruta)
        if metodo == "POST" and m:
            plantilla = f"/v1/asistente/acciones/{{accionId}}/{m.group(2)}"
            sesion = self._sesion(token)
            if not sesion:
                return 401, {"error": "no_autenticado"}, plantilla
            f = self.asistente.confirmar if m.group(2) == "confirmar" else self.asistente.cancelar
            return (*f(sesion, m.group(1)), plantilla)
        return 404, {"error": "ruta_inexistente"}, None

    @staticmethod
    def _json(cuerpo):
        if cuerpo is None or isinstance(cuerpo, dict):
            return cuerpo or {}
        try:
            return json.loads(cuerpo)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _token(cab: dict):
        valor = cab.get("authorization", "")
        return valor[7:].strip() if valor.lower().startswith("bearer ") else ""

    def _sesion(self, token: str):
        """La identidad sale SOLO del token verificado (ADR-032)."""
        try:
            claims = auth.verificar(token, self.cfg.jwt_secret, self.reloj.ahora())
        except auth.TokenInvalido:
            return None
        return Sesion(traveler_id=claims["sub"], token=token)
