# -*- coding: utf-8 -*-
"""knowledge_base.py — Base de conocimiento local y memoria semántica de JARVIS."""
import json
from pathlib import Path
from memory.memory_manager import load_memory, remember

def knowledge_base(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Consulta o almacena información en la base de conocimientos local de JARVIS.
    """
    parameters = parameters or {}
    action = (parameters.get("action") or "search").lower()
    query = parameters.get("query") or parameters.get("key") or ""
    value = parameters.get("value") or parameters.get("content") or ""
    category = parameters.get("category", "notes")

    mem = load_memory()

    if action in ["store", "save", "guardar", "remember"]:
        if not query or not value:
            return "Error: Para guardar en la base de conocimiento se requiere 'key' y 'value'."
        remember(category, query, value)
        if player: player.write_log(f"🧠 Guardado en base de conocimiento: [{category}] {query}")
        return f"Información guardada con éxito en la base de conocimiento: '{query}'."

    else:
        # Search
        results = []
        q_low = query.lower()
        for cat, items in mem.items():
            if isinstance(items, dict):
                for k, v in items.items():
                    val_str = str(v.get("value", v) if isinstance(v, dict) else v)
                    if not q_low or q_low in k.lower() or q_low in val_str.lower():
                        results.append(f"• [{cat.upper()}] {k}: {val_str}")

        if results:
            return f"Resultados en Base de Conocimiento ({len(results)}):\n" + "\n".join(results[:15])
        return f"No se encontró información relevante para '{query}' en la base de conocimiento local."
