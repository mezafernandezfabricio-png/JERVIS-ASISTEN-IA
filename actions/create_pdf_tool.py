# -*- coding: utf-8 -*-
"""
create_pdf_tool.py — Alias compatible para creación de documentos PDF.
"""
from actions.create_pdf import create_pdf

def create_pdf_tool(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """Generador de documentos PDF en el Escritorio."""
    return create_pdf(parameters, player, speak, **kwargs)
