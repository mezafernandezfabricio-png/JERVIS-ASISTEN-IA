# -*- coding: utf-8 -*-
"""
web_navigation.py — Alias compatible para navegación web.
"""
from actions.browser_control import browser_control

def web_navigation(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return browser_control(parameters, player, speak, **kwargs)
