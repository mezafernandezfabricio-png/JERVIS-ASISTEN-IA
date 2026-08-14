# -*- coding: utf-8 -*-
"""
_chrome_launch.py — Alias compatible para lanzador de navegador.
"""
from actions.browser_control import browser_control

def chrome_launch(url: str = "") -> bool:
    try:
        browser_control({"action": "go_to", "url": url})
        return True
    except Exception:
        return False

def _chrome_launch(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return browser_control(parameters, player, speak, **kwargs)
