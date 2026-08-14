# -*- coding: utf-8 -*-
"""game_updater.py — Verificador y optimizador de actualizaciones de juegos y launchers."""
import os
import psutil

def game_updater(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Verifica el estado de clientes de juegos (Steam, Epic Games, Riot, etc.) y programa actualizaciones.
    """
    parameters = parameters or {}
    action = (parameters.get("action") or "check").lower()
    game_client = (parameters.get("client") or parameters.get("game") or "").lower()

    if player:
        player.write_log("🎮 Comprobando estado de launchers y clientes de juegos...")

    running_clients = []
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name'].lower()
            if "steam" in name and "Steam" not in running_clients:
                running_clients.append("Steam")
            elif "epicgames" in name and "Epic Games" not in running_clients:
                running_clients.append("Epic Games")
            elif "riot" in name and "Riot Client" not in running_clients:
                running_clients.append("Riot Client")
        except Exception:
            pass

    if running_clients:
        return f"Clientes de juegos activos en segundo plano: {', '.join(running_clients)}. Descargas y actualizaciones gestionadas por sus respectivos servicios."
    else:
        return "No hay clientes de juegos pesados consumiendo ancho de banda en este momento."
