"""Servidor HTTP (solo biblioteca estándar) que expone la Aplicacion."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .api import Aplicacion

MAX_CUERPO = 16 * 1024


def crear_servidor(app: Aplicacion, host: str = "127.0.0.1", puerto: int = 8080) -> ThreadingHTTPServer:
    class Manejador(BaseHTTPRequestHandler):
        def _atender(self):
            largo = int(self.headers.get("Content-Length") or 0)
            if largo > MAX_CUERPO:
                return self._responder(413, {"error": "cuerpo_demasiado_grande"})
            cuerpo = self.rfile.read(largo) if largo else None
            estado, resp = app.manejar(self.command, self.path, dict(self.headers), cuerpo)
            self._responder(estado, resp)

        def _responder(self, estado, resp):
            datos = b"" if estado == 204 else json.dumps(resp, ensure_ascii=False).encode()
            self.send_response(estado)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(datos)))
            if estado == 429 and "retryAfter" in resp:
                self.send_header("Retry-After", str(resp["retryAfter"]))
            self.end_headers()
            self.wfile.write(datos)

        do_GET = do_POST = _atender

        def log_message(self, *args):  # silencioso
            pass

    return ThreadingHTTPServer((host, puerto), Manejador)
