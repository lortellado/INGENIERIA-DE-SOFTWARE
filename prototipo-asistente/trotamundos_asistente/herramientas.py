"""Tool Executor (ADR-031, ADR-032): conjunto CERRADO de herramientas.

* Solo existen las cuatro herramientas de DEFINICIONES; cualquier otra se rechaza y se audita.
* Los argumentos se validan de forma estricta (campos exactos, tipos y formatos).
* Ninguna herramienta recibe un usuario: se usa el token de la sesión (ADR-032).
* `proponer_cambio` NO modifica nada: crea una acción pendiente (ADR-033).
* Todo lo que vuelve hacia el modelo pasa por el Data Minimizer (ADR-035).
"""
from __future__ import annotations

import re
from datetime import date

from . import minimizador

DEFINICIONES = (
    {"nombre": "consultar_viajes",
     "descripcion": "Lista los viajes de la persona que está conversando.",
     "parametros": {}},
    {"nombre": "consultar_viaje",
     "descripcion": "Devuelve el detalle de un viaje propio (reservas con fechas y proveedor).",
     "parametros": {"viajeId": "string"}},
    {"nombre": "proponer_cambio",
     "descripcion": "Prepara, SIN aplicar, un cambio de fecha en una reserva. La persona debe confirmarlo aparte.",
     "parametros": {"viajeId": "string",
                    "cambio": {"reservaId": "string", "campo": "inicio|fin", "valor": "AAAA-MM-DD"}}},
    {"nombre": "solicitar_derivacion",
     "descripcion": "Deriva el caso a la agencia preferida de la persona.",
     "parametros": {"motivo": "string"}},
)

ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ETIQUETA = {"inicio": "la fecha de inicio", "fin": "la fecha de fin"}


def _fecha_ok(valor) -> bool:
    if not isinstance(valor, str) or not FECHA.match(valor):
        return False
    try:
        date.fromisoformat(valor)
        return True
    except ValueError:
        return False


def _args_validos(nombre: str, a) -> bool:
    if not isinstance(a, dict):
        return False
    if nombre == "consultar_viajes":
        return a == {}
    if nombre == "consultar_viaje":
        return set(a) == {"viajeId"} and isinstance(a["viajeId"], str) and bool(ID.match(a["viajeId"]))
    if nombre == "proponer_cambio":
        c = a.get("cambio")
        return (set(a) == {"viajeId", "cambio"} and isinstance(a["viajeId"], str) and bool(ID.match(a["viajeId"]))
                and isinstance(c, dict) and set(c) == {"reservaId", "campo", "valor"}
                and isinstance(c["reservaId"], str) and bool(ID.match(c["reservaId"]))
                and c["campo"] in ("inicio", "fin"))
    if nombre == "solicitar_derivacion":
        return set(a) == {"motivo"} and isinstance(a["motivo"], str) and 0 < len(a["motivo"]) <= 300
    return False


class EjecutorHerramientas:
    def __init__(self, pasarela, gestor_confirmaciones, auditoria):
        self._pasarela, self._gestor, self._auditoria = pasarela, gestor_confirmaciones, auditoria
        self._tabla = {
            "consultar_viajes": self._consultar_viajes,
            "consultar_viaje": self._consultar_viaje,
            "proponer_cambio": self._proponer_cambio,
            "solicitar_derivacion": lambda s, a: self.derivar(s, a["motivo"]),
        }

    @staticmethod
    def definiciones() -> list:
        return [dict(d) for d in DEFINICIONES]

    def ejecutar(self, sesion, nombre: str, args) -> dict:
        """Siempre devuelve un dict; los errores son {"error": codigo}."""
        if nombre not in self._tabla:
            self._auditoria.publicar("HERRAMIENTA_RECHAZADA", sesion.traveler_id,
                                     {"herramienta": str(nombre)[:40], "motivo": "no_permitida"})
            return {"error": "herramienta_no_permitida"}
        if not _args_validos(nombre, args):
            self._auditoria.publicar("HERRAMIENTA_RECHAZADA", sesion.traveler_id,
                                     {"herramienta": nombre, "motivo": "argumentos_invalidos"})
            return {"error": "argumentos_invalidos"}
        return self._tabla[nombre](sesion, args)

    # --- herramientas -------------------------------------------------------
    def _consultar_viajes(self, sesion, _args) -> dict:
        estado, cuerpo = self._pasarela.listar_viajes(sesion.token)
        if estado != 200:
            return {"error": "servicio_no_disponible"}
        return {"viajes": minimizador.viajes(cuerpo["viajes"])}

    def _consultar_viaje(self, sesion, args) -> dict:
        estado, cuerpo = self._pasarela.detalle_viaje(sesion.token, args["viajeId"])
        if estado == 404:
            return {"error": "no_encontrado"}
        if estado != 200:
            return {"error": "servicio_no_disponible"}
        return minimizador.viaje(cuerpo)

    def _proponer_cambio(self, sesion, args) -> dict:
        cambio = args["cambio"]
        estado, viaje = self._pasarela.detalle_viaje(sesion.token, args["viajeId"])
        if estado == 404:
            return {"error": "no_encontrado"}
        if estado != 200:
            return {"error": "servicio_no_disponible"}
        reserva = next((r for r in viaje["reservas"] if r["id"] == cambio["reservaId"]), None)
        if reserva is None:
            return {"error": "reserva_inexistente"}
        campo, valor = cambio["campo"], cambio["valor"]
        if not _fecha_ok(valor):
            return {"error": "fecha_invalida"}
        if reserva[campo] == valor:
            return {"error": "sin_cambios"}
        nuevo = dict(reserva, **{campo: valor})
        if nuevo["inicio"] > nuevo["fin"]:
            return {"error": "fechas_incoherentes"}
        resumen = (f"En el viaje «{viaje['nombre']}», cambiar {ETIQUETA[campo]} de la reserva de "
                   f"{reserva['tipo']} ({reserva['proveedor']}) del {reserva[campo]} al {valor}.")
        payload = {"viajeId": viaje["id"], "reservaId": reserva["id"], "campo": campo, "valor": valor}
        return {"accionPendiente": self._gestor.proponer(sesion.traveler_id, payload, resumen)}

    def derivar(self, sesion, motivo: str, detalle: str = "") -> dict:
        """Abre un caso en la agencia con un resumen mínimo (no se envía la conversación)."""
        resumen = minimizador.limpiar_texto(detalle, 200)
        estado, cuerpo = self._pasarela.abrir_caso(sesion.token, {"motivo": motivo[:300], "resumen": resumen})
        self._auditoria.publicar("DERIVACION_SOLICITADA", sesion.traveler_id,
                                 {"motivo": motivo[:60], "resultado": estado})
        if estado == 201:
            return {"derivacion": {"casoId": cuerpo["casoId"], "agencia": cuerpo["agencia"]}}
        if estado == 409:
            return {"error": "sin_agencia"}
        return {"error": "servicio_no_disponible"}

    # --- ejecución de una acción ya confirmada ------------------------------
    def aplicar(self, sesion, payload: dict):
        """Llama a Trip Command con el token del usuario que confirmó."""
        return self._pasarela.modificar_reserva(
            sesion.token, payload["viajeId"], payload["reservaId"],
            {"campo": payload["campo"], "valor": payload["valor"]})
