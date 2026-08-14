# -*- coding: utf-8 -*-
"""
desktop.py — Alias compatible para control del escritorio.
"""
from actions.desktop_control import desktop_control

def desktop(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return desktop_control(parameters, player, speak, **kwargs)
