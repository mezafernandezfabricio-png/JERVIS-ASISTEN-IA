# -*- coding: utf-8 -*-
"""
document_manager.py — Alias para gestión y creación de documentos.
"""
from actions.create_document import create_document

def document_manager(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return create_document(parameters, player, speak, **kwargs)
