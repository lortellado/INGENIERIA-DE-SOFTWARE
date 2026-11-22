"""API Gateway + Identity Provider simulados (ADR-005, ADR-025).

El asistente SOLO habla con los servicios a través de la Pasarela y siempre
con el token del usuario: la Pasarela verifica el token y deriva la identidad.
Nunca se le pasa un identificador de usuario.
"""
from __future__ import annotations

from .. import auth


class ProveedorIdentidad:
    def __init__(self, cfg, reloj, datos: dict):
        self._cfg, self._reloj, self._datos = cfg, reloj, datos

    def login(self, usuario: str):
        sub = self._datos["usuarios"].get(usuario)
        return self.token_para(sub) if sub else None

    def token_para(self, sub: str) -> str:
        return auth.emitir(sub, self._cfg.jwt_secret, self._cfg.jwt_ttl_s, self._reloj.ahora())


class Pasarela:
    def __init__(self, cfg, reloj, trip_query, trip_command, agencia):
        self._cfg, self._reloj = cfg, reloj
        self._tq, self._tc, self._ag = trip_query, trip_command, agencia

    def _sub(self, token: str):
        try:
            return auth.verificar(token, self._cfg.jwt_secret, self._reloj.ahora())["sub"]
        except auth.TokenInvalido:
            return None

    def _con_identidad(self, token, f):
        sub = self._sub(token)
        return (401, {"error": "no_autenticado"}) if sub is None else f(sub)

    # Interfaces existentes que consume el asistente / el panel
    def listar_viajes(self, token):                       # GET /v1/viajeros/me/viajes
        return self._con_identidad(token, self._tq.listar)

    def detalle_viaje(self, token, viaje_id):             # GET /v1/viajes/{id}
        return self._con_identidad(token, lambda s: self._tq.detalle(s, viaje_id))

    def modificar_reserva(self, token, viaje_id, reserva_id, cuerpo):   # Trip Command (UC3)
        return self._con_identidad(token, lambda s: self._tc.modificar_reserva(s, viaje_id, reserva_id, cuerpo))

    def abrir_caso(self, token, cuerpo):                  # Agency Integration
        return self._con_identidad(token, lambda s: self._ag.abrir_caso(s, cuerpo))
