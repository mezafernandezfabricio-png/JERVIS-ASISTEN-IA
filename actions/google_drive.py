# -*- coding: utf-8 -*-
"""google_drive.py — Acceso y búsqueda en Google Drive."""
import urllib.parse
import webbrowser

def google_drive(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Abre o busca archivos y carpetas en Google Drive:
    - query / search: término de búsqueda en Drive.
    """
    parameters = parameters or {}
    query = parameters.get("query") or parameters.get("search") or ""

    if query:
        url = f"https://drive.google.com/drive/search?q={urllib.parse.quote(query)}"
        msg = f"Búsqueda de '{query}' abierta en Google Drive."
    else:
        url = "https://drive.google.com/drive/my-drive"
        msg = "Google Drive abierto en el navegador."

    webbrowser.open(url)
    if player:
        player.write_log(f"📁 {msg}")
    return msg
