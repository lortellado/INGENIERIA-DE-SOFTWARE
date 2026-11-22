"""Chat de consola para la demo: usa la MISMA API que cualquier cliente (token + endpoints)."""
from __future__ import annotations

from .api import Aplicacion


def chat(app: Aplicacion, usuario: str) -> None:
    _, r = app.manejar("POST", "/dev/login", {}, {"usuario": usuario})
    if not r.get("token"):
        print(f"Usuario desconocido: {usuario}. Probá con 'ana' o 'beto'.")
        return
    cab = {"Authorization": f"Bearer {r['token']}"}
    print(f"Asistente de Trotamundos (sesión de {usuario}). Escribí 'salir' para terminar.\n")
    while True:
        try:
            texto = input(f"{usuario}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if texto.lower() in ("salir", "exit"):
            return
        if not texto:
            continue
        estado, resp = app.manejar("POST", "/v1/asistente/mensajes", cab, {"mensaje": texto})
        print(f"\nasistente> {resp.get('respuesta') or resp.get('mensaje') or resp}")
        for alt in resp.get("alternativas", []):
            print(f"   · {alt['texto']}")
        accion = resp.get("accionPendiente")
        if accion:
            if input("¿Confirmás el cambio? [s/n] ").strip().lower().startswith("s"):
                estado, r2 = app.manejar("POST", f"/v1/asistente/acciones/{accion['accionId']}/confirmar", cab)
                print(f"asistente> {r2.get('mensaje') or r2}")
            else:
                app.manejar("POST", f"/v1/asistente/acciones/{accion['accionId']}/cancelar", cab)
                print("asistente> Cambio cancelado, no se modificó nada.")
        print()
