"""Adaptadores del Language Model Port (SIMULADOS: no hay un LLM real).

* ModeloSimulado: reglas por palabras clave que imitan a un LLM con herramientas.
  Es el que usa la demo. Un adaptador real (Anthropic, OpenAI, etc.) implementaría
  la misma interfaz `generar` sin tocar ningún otro componente (QA-16).
* ModeloGuionado: devuelve respuestas predefinidas (para pruebas).
* ModeloQueFalla: error, lentitud o respuesta inválida (para probar QA-15).
"""
from __future__ import annotations

import re
import time
from typing import Callable, Optional

from .minimizador import normalizar
from .modelo import ModeloPort

ID_VIAJE = re.compile(r"\bv-[a-z0-9]+-\d+\b", re.I)
FECHA_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
FECHA_DMA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
VERBOS_CAMBIO = ("cambi", "mov", "modific", "adelant", "atras", "extend", "posterg")
CAMPO_FIN = {"salida", "fin", "vuelta", "regreso", "checkout", "check-out"}
CAMPO_INICIO = {"entrada", "inicio", "llegada", "ida", "checkin", "check-in"}
TIPOS = {"hotel": "alojamiento", "alojamiento": "alojamiento", "hostel": "alojamiento",
         "vuelo": "vuelo", "avion": "vuelo"}
# Palabras que indican "quiero ver mis viajes/reservas" (lenguaje natural simple)
PALABRAS_VIAJE = {"viaje", "viajes", "itinerario", "reserva", "reservas", "reservado", "reservados",
                  "vacaciones", "vuelos", "hoteles", "alojamientos", "hospedaje"} | set(TIPOS)
# Palabras que no sirven para identificar un viaje por su nombre
NO_DISTINTIVAS = {"en", "de", "del", "a", "el", "la", "los", "las", "y", "por", "para", "viaje", "viajes"}

ERRORES = {
    "no_encontrado": "No encontré ese viaje en tu cuenta. Revisá el identificador o pedime «mis viajes».",
    "reserva_inexistente": "No encontré esa reserva en el viaje.",
    "fecha_invalida": "La fecha no es válida. Usá el formato AAAA-MM-DD o DD/MM/AAAA.",
    "sin_cambios": "Esa reserva ya tiene esa fecha, no hay nada para cambiar.",
    "fechas_incoherentes": "Con esa fecha el inicio quedaría después del fin de la reserva, así que no puedo proponerlo.",
}


def _tokens(texto: str) -> set:
    return set(re.findall(r"[a-z0-9\-]+", normalizar(texto)))


def _fecha(texto: str) -> Optional[str]:
    m = FECHA_ISO.search(texto)
    if m:
        return m.group(0)
    m = FECHA_DMA.search(texto)
    if m:
        d, mes, a = m.groups()
        return f"{a}-{int(mes):02d}-{int(d):02d}"
    return None


def _intencion_cambio(texto: str) -> Optional[dict]:
    tk = _tokens(texto)
    verbo = any(t.startswith(VERBOS_CAMBIO) for t in tk) or tk & {"pasa", "pasar", "pasame"}
    campo = "fin" if tk & CAMPO_FIN else "inicio" if tk & CAMPO_INICIO else None
    tipo = next((TIPOS[t] for t in tk if t in TIPOS), None)
    valor = _fecha(texto)
    if verbo and campo and tipo and valor:
        return {"campo": campo, "tipo": tipo, "valor": valor}
    return None


def _viajes_nombrados(lista: list, pedido: str) -> list:
    """Viajes cuyo nombre comparte una palabra distintiva con el pedido (ej.: 'Madrid')."""
    palabras = _tokens(pedido)
    return [v for v in lista if (_tokens(v["nombre"]) - NO_DISTINTIVAS) & palabras]


def _llamar(nombre: str, **args) -> dict:
    return {"tipo": "herramienta", "nombre": nombre, "argumentos": args}


def _texto(t: str) -> dict:
    return {"tipo": "texto", "texto": t}


class ModeloSimulado(ModeloPort):
    def generar(self, contexto: dict, herramientas: list) -> dict:
        mensajes = contexto["mensajes"]
        ultimo = mensajes[-1]
        if ultimo["rol"] == "herramienta":
            return self._tras_herramienta(mensajes, ultimo)
        return self._desde_usuario(ultimo["contenido"])

    def _desde_usuario(self, texto: str) -> dict:
        viaje = ID_VIAJE.search(texto)
        if _intencion_cambio(texto):
            return _llamar("consultar_viaje", viajeId=viaje.group(0).lower()) if viaje \
                else _llamar("consultar_viajes")
        if viaje:
            return _llamar("consultar_viaje", viajeId=viaje.group(0).lower())
        if _tokens(texto) & PALABRAS_VIAJE:
            return _llamar("consultar_viajes")
        return {"tipo": "no_entendido"}

    def _tras_herramienta(self, mensajes: list, ultimo: dict) -> dict:
        nombre, res = ultimo["nombre"], ultimo["contenido"]
        pedido = next((m["contenido"] for m in reversed(mensajes) if m["rol"] == "usuario"), "")
        cambio = _intencion_cambio(pedido)
        if "error" in res:
            return _texto(ERRORES.get(res["error"], f"No pude completar la operación ({res['error']})."))
        if nombre == "consultar_viajes":
            lista = res["viajes"]
            nombrados = _viajes_nombrados(lista, pedido)       # "el viaje de Madrid"
            if cambio:
                elegido = lista if len(lista) == 1 else nombrados
                if len(elegido) == 1:
                    return _llamar("consultar_viaje", viajeId=elegido[0]["id"])
                return _texto("¿De qué viaje? Decime su nombre (por ejemplo «Madrid») o su identificador "
                              "(por ejemplo v-ana-1) para poder proponer el cambio.")
            if len(nombrados) == 1:
                return _llamar("consultar_viaje", viajeId=nombrados[0]["id"])
            if not lista:
                return _texto("Todavía no tenés viajes cargados.")
            filas = "\n".join(f"- {v['id']} · {v['nombre']} ({v['estado']}, {v['fechaInicio']} a {v['fechaFin']})"
                              for v in lista)
            return _texto(f"Tus viajes:\n{filas}")
        if nombre == "consultar_viaje":
            if cambio:
                candidatas = [r for r in res["reservas"] if r["tipo"] == cambio["tipo"]]
                if not candidatas:
                    return _texto(f"No encuentro una reserva de {cambio['tipo']} en ese viaje.")
                if len(candidatas) > 1:
                    return _texto("Hay más de una reserva de ese tipo; indicame el identificador de la reserva.")
                return _llamar("proponer_cambio", viajeId=res["id"],
                               cambio={"reservaId": candidatas[0]["id"], "campo": cambio["campo"],
                                       "valor": cambio["valor"]})
            filas = "\n".join(f"- {r['id']} · {r['tipo']} · {r['proveedor']} · {r['inicio']} → {r['fin']} ({r['estado']})"
                              for r in res["reservas"]) or "- (sin reservas)"
            return _texto(f"{res['nombre']} ({res['estado']}, {res['fechaInicio']} a {res['fechaFin']}):\n{filas}")
        return _texto("Listo.")


class ModeloGuionado(ModeloPort):
    """Responde con lo que se le indique: una lista fija o una función."""

    def __init__(self, respuestas):
        self._respuestas = respuestas
        self.llamadas = 0

    def generar(self, contexto, herramientas):
        self.llamadas += 1
        if callable(self._respuestas):
            return self._respuestas(contexto, herramientas)
        return self._respuestas[min(self.llamadas, len(self._respuestas)) - 1]


class ModeloQueFalla(ModeloPort):
    """modo: 'error' (excepción), 'lento' (duerme `demora_s`) o 'basura' (respuesta inválida)."""

    def __init__(self, modo: str = "error", demora_s: float = 0.5, delegado: ModeloPort = None):
        self.modo, self.demora_s, self.delegado = modo, demora_s, delegado
        self.llamadas = 0

    def generar(self, contexto, herramientas):
        self.llamadas += 1
        if self.modo == "error":
            raise ConnectionError("el proveedor del modelo no responde")
        if self.modo == "basura":
            return {"respuesta": "???"}
        time.sleep(self.demora_s)
        return self.delegado.generar(contexto, herramientas) if self.delegado else _texto("tarde")
