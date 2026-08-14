# -*- coding: utf-8 -*-
"""google_maps.py — Búsqueda de ubicaciones, rutas y navegación en Google Maps."""
import urllib.parse
import webbrowser

def google_maps(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Busca lugares, direcciones o traza rutas en Google Maps:
    - query / location: busca un lugar o dirección específica.
    - origin + destination: calcula y despliega la ruta entre dos puntos.
    """
    parameters = parameters or {}
    location = parameters.get("location") or parameters.get("query") or parameters.get("place") or ""
    origin = parameters.get("origin") or parameters.get("desde") or ""
    destination = parameters.get("destination") or parameters.get("hasta") or ""

    if origin and destination:
        url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(origin)}&destination={urllib.parse.quote(destination)}"
        msg = f"Ruta trazada en Google Maps desde '{origin}' hasta '{destination}'."
    elif location:
        url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(location)}"
        msg = f"Búsqueda de '{location}' desplegada en Google Maps."
    else:
        url = "https://www.google.com/maps"
        msg = "Abriendo Google Maps."

    webbrowser.open(url)
    if player:
        player.write_log(f"🗺️ {msg}")
    return msg
