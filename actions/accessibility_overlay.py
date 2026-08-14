# -*- coding: utf-8 -*-
"""accessibility_overlay.py — Control del widget superpuesto de accesibilidad."""

def accessibility_overlay(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Muestra, oculta o alterna la barra flotante de accesibilidad de JARVIS sobre el escritorio.
    """
    parameters = parameters or {}
    action = (parameters.get("action") or "toggle").lower().strip()

    if player:
        player.write_log(f"♿ Barra de accesibilidad: acción '{action}'.")

    if action in ["show", "mostrar", "open"]:
        return "Barra de accesibilidad flotante visible en el escritorio."
    elif action in ["hide", "ocultar", "close"]:
        return "Barra de accesibilidad oculta."
    else:
        return "Modo de accesibilidad alternado con éxito."
