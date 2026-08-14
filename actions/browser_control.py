# -*- coding: utf-8 -*-
"""
browser_control.py — Control total de navegación web para JARVIS.
Navega en ventanas abiertas o abre automáticamente el navegador si no hay ninguno abierto.
"""

import time
import os
import webbrowser
import subprocess
from pathlib import Path

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

def browser_control(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Controla la navegación web activa (Chrome, Edge, Firefox, Brave, Opera).
    Parámetros:
        - action: 'go_to', 'open', 'search', 'new_tab', 'close_tab', 'scroll', 'back', 'forward', 'refresh'
        - url: URL o dirección web a abrir
        - query: Término de búsqueda
        - direction: 'down' (default) o 'up'
    """
    params = parameters or {}
    action = str(params.get("action") or "go_to").lower().strip()
    url = params.get("url") or ""
    query = params.get("query") or ""
    direction = str(params.get("direction") or "down").lower()

    if action in ["search", "buscar"] and not url and query:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    if not url and action in ["go_to", "open", "abrir"]:
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        else:
            url = "https://www.google.com"

    # Buscar ventana de navegador activa
    target_window = None
    if gw:
        browser_keywords = ["chrome", "edge", "firefox", "brave", "opera", "vivaldi"]
        for win in gw.getAllWindows():
            if win.title.strip():
                for kw in browser_keywords:
                    if kw in win.title.lower():
                        target_window = win
                        break
            if target_window:
                break

    # Si no hay navegador abierto y se pide abrir o navegar, abrir el navegador del sistema
    if not target_window:
        if url:
            try:
                webbrowser.open(url)
                if player:
                    try: player.write_log(f"🌐 Navegador abierto con: {url}")
                    except: pass
                return f"Navegador web iniciado con éxito navegando a: {url}"
            except Exception as e:
                return f"Error abriendo navegador: {e}"
        else:
            webbrowser.open("https://www.google.com")
            return "Navegador web abierto con éxito."

    try:
        # Enfocar ventana existente
        try:
            if target_window.isMinimized:
                target_window.restore()
            target_window.activate()
            time.sleep(0.12)
        except Exception:
            pass

        if action in ["go_to", "open", "abrir", "search", "buscar"]:
            if url:
                if pyautogui:
                    pyautogui.hotkey('ctrl', 'l')
                    time.sleep(0.04)
                    pyautogui.write(url, interval=0.003)
                    pyautogui.press('enter')
                else:
                    webbrowser.open(url)
                return f"Navegando a {url} en la ventana '{target_window.title}'."
            return "No se indicó URL o búsqueda."

        elif action in ["new_tab", "nueva_pestana"]:
            if pyautogui:
                pyautogui.hotkey('ctrl', 't')
                time.sleep(0.1)
                if url:
                    pyautogui.write(url, interval=0.003)
                    pyautogui.press('enter')
            else:
                webbrowser.open(url or "https://www.google.com")
            return f"Nueva pestaña abierta{' con ' + url if url else ''}."

        elif action in ["close_tab", "cerrar_pestana"]:
            if pyautogui: pyautogui.hotkey('ctrl', 'w')
            return "Pestaña cerrada."

        elif action in ["refresh", "recargar", "reload"]:
            if pyautogui: pyautogui.hotkey('ctrl', 'r')
            return "Pestaña recargada."

        elif action in ["back", "atras"]:
            if pyautogui: pyautogui.hotkey('alt', 'left')
            return "Navegando hacia atrás."

        elif action in ["forward", "adelante"]:
            if pyautogui: pyautogui.hotkey('alt', 'right')
            return "Navegando hacia adelante."

        elif action in ["scroll", "desplazar"]:
            if pyautogui:
                if direction in ["down", "abajo"]:
                    pyautogui.press('pgdn')
                else:
                    pyautogui.press('pgup')
            return f"Desplazamiento hacia {direction} completado."

        else:
            if url:
                webbrowser.open(url)
                return f"Navegando a {url}."
            return f"Acción '{action}' ejecutada en el navegador."

    except Exception as e:
        if url:
            webbrowser.open(url)
            return f"Navegador abierto en: {url}"
        return f"Error controlando el navegador: {e}"

def web_navigation(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return browser_control(parameters, player, speak, **kwargs)

def _chrome_launch(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return browser_control(parameters, player, speak, **kwargs)
