"""Language Model Port (ADR-034) con timeout, circuit breaker y validación de respuesta.

El resto del asistente solo conoce este módulo: nunca importa un adaptador concreto.
Contrato de un adaptador (`generar`):
    generar(contexto, herramientas) -> uno de
        {"tipo": "texto", "texto": str}
        {"tipo": "herramienta", "nombre": str, "argumentos": dict}
        {"tipo": "no_entendido"}
"""
from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor


class ModeloNoDisponible(Exception):
    """El modelo no respondió bien: timeout, error, respuesta inválida o circuito abierto."""


class ModeloPort(ABC):
    @abstractmethod
    def generar(self, contexto: dict, herramientas: list) -> dict:
        ...


def _validar(r) -> dict:
    if not isinstance(r, dict):
        raise ValueError("respuesta no es un objeto")
    tipo = r.get("tipo")
    if tipo == "texto":
        if not isinstance(r.get("texto"), str) or not r["texto"].strip():
            raise ValueError("texto vacío")
        return {"tipo": "texto", "texto": r["texto"][:4000]}
    if tipo == "herramienta":
        if not isinstance(r.get("nombre"), str) or not isinstance(r.get("argumentos"), dict):
            raise ValueError("llamada a herramienta mal formada")
        return {"tipo": "herramienta", "nombre": r["nombre"], "argumentos": r["argumentos"]}
    if tipo == "no_entendido":
        return {"tipo": "no_entendido"}
    raise ValueError("tipo desconocido")


class ModeloProtegido(ModeloPort):
    """Envuelve un adaptador con las protecciones de ADR-034."""

    def __init__(self, adaptador: ModeloPort, reloj, timeout_s: float,
                 fallos_para_abrir: int, pausa_s: float, hilos: int = 16):
        self._adaptador = adaptador
        self._reloj = reloj
        self._timeout = timeout_s
        self._max_fallos = fallos_para_abrir
        self._pausa = pausa_s
        self._pool = ThreadPoolExecutor(max_workers=hilos, thread_name_prefix="modelo")
        self._lock = threading.Lock()
        self._fallos = 0
        self._abierto_hasta = None
        self._probando = False

    @property
    def estado(self) -> str:
        with self._lock:
            if self._abierto_hasta is None:
                return "cerrado"
            return "abierto" if self._reloj.ahora() < self._abierto_hasta else "semiabierto"

    def generar(self, contexto: dict, herramientas: list) -> dict:
        with self._lock:
            if self._abierto_hasta is not None:
                if self._reloj.ahora() < self._abierto_hasta or self._probando:
                    raise ModeloNoDisponible("circuito_abierto")
                self._probando = True  # semiabierto: deja pasar UNA prueba
        try:
            futuro = self._pool.submit(self._adaptador.generar, contexto, herramientas)
            resultado = _validar(futuro.result(timeout=self._timeout))
        except Exception as exc:
            with self._lock:
                self._fallos += 1
                if self._fallos >= self._max_fallos or self._abierto_hasta is not None:
                    self._abierto_hasta = self._reloj.ahora() + self._pausa
                self._probando = False
            raise ModeloNoDisponible(type(exc).__name__) from exc
        with self._lock:
            self._fallos = 0
            self._abierto_hasta = None
            self._probando = False
        return resultado
