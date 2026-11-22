"""Uso:
    python -m trotamundos_asistente chat [--usuario ana] [--falla-modelo]
    python -m trotamundos_asistente servidor [--puerto 8080] [--falla-modelo]
"""
from __future__ import annotations

import argparse

from .adaptadores import ModeloQueFalla
from .api import Aplicacion
from .cli import chat
from .servidor import crear_servidor


def main() -> None:
    p = argparse.ArgumentParser(prog="trotamundos_asistente")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("chat", help="chat de consola")
    c.add_argument("--usuario", default="ana")
    s = sub.add_parser("servidor", help="API REST en http://127.0.0.1:PUERTO")
    s.add_argument("--puerto", type=int, default=8080)
    for q in (c, s):
        q.add_argument("--falla-modelo", action="store_true", help="simula la caída del modelo (QA-15)")
    a = p.parse_args()

    app = Aplicacion(modelo=ModeloQueFalla("error") if a.falla_modelo else None)
    if a.cmd == "chat":
        chat(app, a.usuario)
        return
    srv = crear_servidor(app, puerto=a.puerto)
    print(f"Escuchando en http://127.0.0.1:{a.puerto}  (usuarios de prueba: ana, beto; Ctrl+C para salir)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
