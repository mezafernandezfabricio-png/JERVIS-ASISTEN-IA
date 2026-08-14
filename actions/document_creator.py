# -*- coding: utf-8 -*-
"""
document_creator.py — Alias para creación de documentos en el Escritorio.
"""
from actions.create_document import create_document

def document_creator(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return create_document(parameters, player, speak, **kwargs)