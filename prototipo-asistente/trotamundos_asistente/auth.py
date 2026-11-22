"""JWT HS256 mínimo (Identity Provider simulado, ADR-005).

Solo para el prototipo: en el sistema real el token lo emite el Identity Provider.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json


class TokenInvalido(Exception):
    pass


def _b64(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


def _unb64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def _firmar(secret: bytes, contenido: str) -> str:
    return _b64(hmac.new(secret, contenido.encode(), hashlib.sha256).digest())


def emitir(sub: str, secret: bytes, ttl_s: int, ahora: float) -> str:
    cabecera = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    cuerpo = _b64(json.dumps({"sub": sub, "iat": int(ahora), "exp": int(ahora) + ttl_s},
                             separators=(",", ":")).encode())
    return f"{cabecera}.{cuerpo}.{_firmar(secret, cabecera + '.' + cuerpo)}"


def verificar(token: str, secret: bytes, ahora: float) -> dict:
    """Devuelve los claims si el token es válido; si no, TokenInvalido."""
    try:
        cabecera, cuerpo, firma = token.split(".")
        if not hmac.compare_digest(firma, _firmar(secret, cabecera + "." + cuerpo)):
            raise TokenInvalido("firma")
        if json.loads(_unb64(cabecera)).get("alg") != "HS256":
            raise TokenInvalido("algoritmo")
        claims = json.loads(_unb64(cuerpo))
        if not isinstance(claims.get("sub"), str) or claims["exp"] <= ahora:
            raise TokenInvalido("vencido")
        return claims
    except TokenInvalido:
        raise
    except (ValueError, KeyError, TypeError, AttributeError):
        raise TokenInvalido("formato")
