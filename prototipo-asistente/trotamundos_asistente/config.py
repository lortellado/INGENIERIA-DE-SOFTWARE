"""Configuración y supuestos del prototipo.

Los valores numéricos que el enunciado no fija son supuestos del grupo
(Iteración 5, Step 7). Están todos acá para poder ajustarlos en un solo lugar.
"""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class Reloj:
    """Reloj real. Se inyecta para poder probar vencimientos sin esperar."""

    def ahora(self) -> float:
        return time.time()


class RelojManual(Reloj):
    """Reloj controlable, para las pruebas."""

    def __init__(self, inicio: float = 1_800_000_000.0):
        self._t = inicio

    def ahora(self) -> float:
        return self._t

    def avanzar(self, segundos: float) -> None:
        self._t += segundos


@dataclass(frozen=True)
class Config:
    # --- Secretos del prototipo (en producción vendrían del Secret Store) ---
    jwt_secret: bytes = field(default_factory=lambda: secrets.token_bytes(32))
    confirm_secret: bytes = field(default_factory=lambda: secrets.token_bytes(32))

    jwt_ttl_s: int = 900                  # ADR-005: tokens de corta vida
    confirmacion_ttl_s: int = 300         # ADR-033: 5 minutos (supuesto)
    conversacion_ttl_s: int = 86_400      # ADR-036: 24 horas (supuesto)
    modelo_timeout_s: float = 2.0         # ADR-034: valor inicial a calibrar
    breaker_fallos: int = 2               # fallos seguidos que abren el circuito
    breaker_pausa_s: float = 10.0         # tiempo con el circuito abierto
    max_pasos_por_turno: int = 5          # herramientas encadenadas por mensaje
    fallos_para_derivar: int = 2          # ADR-031: dos "no entendí" seguidos
    pedidos_por_minuto: int = 20          # ADR-036: límite por usuario
    max_concurrentes: int = 8             # ADR-036: tope de turnos simultáneos
    max_mensaje: int = 1000               # caracteres por mensaje
    historial_max: int = 12               # mensajes que se envían al motor
