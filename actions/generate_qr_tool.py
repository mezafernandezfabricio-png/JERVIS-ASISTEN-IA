# -*- coding: utf-8 -*-
"""
generate_qr_tool.py — Alias compatible para herramienta generadora de códigos QR.
"""
from actions.generate_qr import generate_qr

def generate_qr_tool(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return generate_qr(parameters, player, speak, **kwargs)