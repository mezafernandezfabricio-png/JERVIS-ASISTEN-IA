# -*- coding: utf-8 -*-
"""gmail_control.py — Gestión y redacción rápida en Gmail."""
import urllib.parse
import webbrowser

def gmail_control(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Control y redacción de correos en Gmail:
    - to: destinatario
    - subject: asunto
    - body: cuerpo del mensaje
    - search: búsqueda en la bandeja de entrada
    """
    parameters = parameters or {}
    to = parameters.get("to") or parameters.get("recipient") or ""
    subject = parameters.get("subject") or parameters.get("asunto") or ""
    body = parameters.get("body") or parameters.get("message") or ""
    search = parameters.get("search") or parameters.get("query") or ""

    if to or subject or body:
        params = {
            "view": "cm",
            "fs": "1",
            "to": to,
            "su": subject,
            "body": body
        }
        url = f"https://mail.google.com/mail/?{urllib.parse.urlencode(params)}"
        msg = f"Ventana de redacción de Gmail abierta para '{to or 'destinatario'}' con el asunto '{subject}'."
    elif search:
        url = f"https://mail.google.com/mail/u/0/#search/{urllib.parse.quote(search)}"
        msg = f"Búsqueda de correos en Gmail: '{search}'."
    else:
        url = "https://mail.google.com"
        msg = "Bandeja de entrada de Gmail abierta."

    webbrowser.open(url)
    if player:
        player.write_log(f"✉️ {msg}")
    return msg
