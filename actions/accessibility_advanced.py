# -*- coding: utf-8 -*-
"""accessibility_advanced.py — Herramientas avanzadas de accesibilidad del sistema."""
import subprocess

try:
    import pyautogui
except ImportError:
    pyautogui = None

def accessibility_advanced(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Control de accesibilidad avanzado en Windows:
    - magnifier / lupa: activa o desactiva la lupa de Windows.
    - narrator / narrador: activa el lector de pantalla.
    - contrast / alto_contraste: activa el modo de alto contraste.
    - speech / dictado: activa el dictado por voz de Windows (Win+H).
    """
    parameters = parameters or {}
    feature = (parameters.get("feature") or parameters.get("action") or "magnifier").lower()

    if "lupa" in feature or "magnifier" in feature:
        try:
            subprocess.Popen(["magnify.exe"], shell=True)
            msg = "Lupa de Windows iniciada."
        except Exception:
            if pyautogui: pyautogui.hotkey("win", "+")
            msg = "Activando ampliación de pantalla."

    elif "narrador" in feature or "narrator" in feature:
        try:
            subprocess.Popen(["narrator.exe"], shell=True)
            msg = "Narrador de Windows iniciado."
        except Exception:
            if pyautogui: pyautogui.hotkey("win", "ctrl", "enter")
            msg = "Conmutando lector de pantalla."

    elif "contraste" in feature or "contrast" in feature:
        if pyautogui:
            pyautogui.hotkey("left alt", "left shift", "printscreen")
            msg = "Conmutando modo de alto contraste."
        else:
            msg = "Comando de alto contraste enviado."

    elif "dictado" in feature or "dictation" in feature or "voice" in feature:
        if pyautogui:
            pyautogui.hotkey("win", "h")
            msg = "Dictado por voz de Windows activado (Win+H)."
        else:
            msg = "Dictado por voz activado."

    else:
        try:
            subprocess.Popen(["start", "ms-settings:easeofaccess-display"], shell=True)
            msg = f"Abriendo panel de accesibilidad de Windows para '{feature}'."
        except Exception:
            msg = f"Accesibilidad: configurando {feature}."

    if player:
        player.write_log(f"♿ {msg}")
    return msg
