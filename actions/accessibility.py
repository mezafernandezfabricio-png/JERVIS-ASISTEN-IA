# -*- coding: utf-8 -*-

import os
import subprocess
import pyperclip
import pyautogui
import time

def accessibility(parameters: dict, player=None) -> str:
    """
    Control de Accesibilidad del Sistema: Volumen, Lectura de texto, Energía.
    """
    action = parameters.get("action", "").lower()
    value = parameters.get("value", "") # Opcional: nivel de volumen o brillo

    try:
        # --- CONTROL DE VOLUMEN ---
        if action == "volume_up":
            # SendKeys 175 = Volume Up
            subprocess.run(["powershell", "-Command", "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"])
            return "Subiendo volumen."
        
        elif action == "volume_down":
            # SendKeys 174 = Volume Down
            subprocess.run(["powershell", "-Command", "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"])
            return "Bajando volumen."
            
        elif action == "mute":
            # SendKeys 173 = Mute
            subprocess.run(["powershell", "-Command", "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"])
            return "Silenciando sistema."

        # --- LECTURA DE CONTENIDO (Accesibilidad Cognitiva) ---
        elif action == "read_clipboard":
            content = pyperclip.paste()
            if not content:
                return "El portapapeles está vacío."
            return f"He leído lo siguiente del portapapeles: {content[:200]}..."

        # --- GESTIÓN DE ENERGÍA / PANTALLA ---
        elif action == "screen_off":
            # Apagar pantalla sin suspender
            subprocess.run(["powershell", "-Command", "(SendMessage 65535 274 61808 2)"])
            return "Apagando pantalla."
            
        elif action == "lock_pc":
            # Bloquear Windows
            subprocess.run("rundll32.exe user32.dll,LockWorkStation")
            return "Bloqueando equipo."

        return f"Acción '{action}' no definida en el módulo de accesibilidad."

    except Exception as e:
        return f"Error en la herramienta de accesibilidad: {str(e)}"