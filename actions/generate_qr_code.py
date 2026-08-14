# -*- coding: utf-8 -*-
"""
generate_qr_code.py — Alias compatible para generación de códigos QR.
"""
from actions.generate_qr import generate_qr

def generate_qr_code(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return generate_qr(parameters, player, speak, **kwargs)
