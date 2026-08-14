# -*- coding: utf-8 -*-
"""google_calendar.py — Integración y gestión de eventos de Google Calendar."""
import urllib.parse
import webbrowser

def google_calendar(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Consulta o crea eventos en Google Calendar:
    - title / summary: título del evento.
    - date / time: fecha y hora.
    - action: create | open | list
    """
    parameters = parameters or {}
    action = (parameters.get("action") or "open").lower()
    title = parameters.get("title") or parameters.get("summary") or parameters.get("event") or ""
    details = parameters.get("details") or parameters.get("description") or ""

    if action in ["create", "add", "nuevo", "crear"] and title:
        # URL directa para crear evento rápido en Google Calendar
        params = {
            "action": "TEMPLATE",
            "text": title,
            "details": details
        }
        url = f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"
        webbrowser.open(url)
        msg = f"Plantilla de evento '{title}' abierta en Google Calendar."
    else:
        webbrowser.open("https://calendar.google.com")
        msg = "Google Calendar abierto en el navegador."

    if player:
        player.write_log(f"📅 {msg}")
    return msg
