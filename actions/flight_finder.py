# -*- coding: utf-8 -*-
"""flight_finder.py — Búsqueda de vuelos y comparativa de pasajes aéreos."""
import urllib.parse
import webbrowser

def flight_finder(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Busca vuelos disponibles entre dos ciudades usando Google Flights o Skyscanner:
    - origin: ciudad o código de aeropuerto de origen.
    - destination: ciudad o código de aeropuerto de destino.
    - date: fecha de salida (opcional).
    """
    parameters = parameters or {}
    origin = parameters.get("origin") or parameters.get("origen") or ""
    destination = parameters.get("destination") or parameters.get("destino") or ""
    date_str = parameters.get("date") or parameters.get("fecha") or ""

    if not destination:
        url = "https://www.google.com/travel/flights"
        msg = "Abriendo Google Flights para búsqueda de vuelos."
    else:
        query_text = f"vuelos de {origin} a {destination} {date_str}".strip()
        url = f"https://www.google.com/travel/flights?q={urllib.parse.quote(query_text)}"
        msg = f"Búsqueda de vuelos de '{origin or 'tu ubicación'}' a '{destination}' desplegada en Google Flights."

    webbrowser.open(url)
    if player:
        player.write_log(f"✈️ {msg}")
    return msg
