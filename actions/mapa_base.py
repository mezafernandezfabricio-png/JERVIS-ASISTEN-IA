# -*- coding: utf-8 -*-
"""
mapa_base.py — Alias compatible para visualización de mapas.
"""
from actions.google_maps import google_maps

def mapa_base(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return google_maps(parameters, player, speak, **kwargs)