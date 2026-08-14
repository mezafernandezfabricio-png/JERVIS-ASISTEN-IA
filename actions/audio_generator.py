# -*- coding: utf-8 -*-
"""
audio_generator.py — Generador de archivos de audio MP3 con voces neuronales para JARVIS.
Guarda SIEMPRE en el Escritorio del usuario con apertura y reproducción automática.
"""

import os
import sys
import re
import time
import asyncio
from pathlib import Path
from datetime import datetime

def _get_desktop_dir() -> Path:
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
        if onedrive_desktop.exists():
            return onedrive_desktop
        desktop.mkdir(parents=True, exist_ok=True)
    return desktop

def _sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned if cleaned else f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def audio_generator(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Convierte cualquier texto en un archivo de audio MP3 con voces neuronales realistas y lo guarda en el Escritorio.
    Parámetros:
        - text / prompt / contenido: Texto a vocalizar
        - voice / voz: Tipo de voz ('jorge', 'dalia', 'alvaro', 'elena', 'narrador')
        - filename / nombre: Nombre del archivo MP3 (opcional)
        - open_file / abrir: Si debe reproducir el archivo tras crearlo (default True)
    """
    params = parameters or {}
    text = params.get("text") or params.get("prompt") or params.get("contenido") or ""
    voice_type = str(params.get("voice") or params.get("voz") or "jorge").lower()
    filename = params.get("filename") or params.get("nombre") or ""
    open_file = params.get("open_file", params.get("abrir", True))

    if not text:
        return "Debe proporcionar el texto que desea convertir a audio MP3."

    desktop = _get_desktop_dir()

    voices = {
        "jorge": "es-MX-JorgeNeural",
        "dalia": "es-MX-DaliaNeural",
        "alvaro": "es-ES-AlvaroNeural",
        "elena": "es-AR-ElenaNeural",
        "narrador": "es-ES-ManuelNeural",
        "carlos": "es-ES-AlvaroNeural",
        "mexicana": "es-MX-DaliaNeural",
        "argentina": "es-AR-ElenaNeural",
    }
    selected_voice = voices.get(voice_type, "es-MX-JorgeNeural")

    clean_base = _sanitize_filename(filename or text[:18])
    if not clean_base.lower().endswith(".mp3"):
        clean_base = f"{clean_base}.mp3"

    file_path = desktop / clean_base

    if player:
        try: player.write_log(f"🎙️ Generando audio MP3: {file_path.name}...")
        except: pass

    saved = False

    # 1. Intentar mediante la librería directa edge_tts en Python
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, selected_voice)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.submit(asyncio.run, communicate.save(str(file_path))).result(timeout=30)
            else:
                loop.run_until_complete(communicate.save(str(file_path)))
        except Exception:
            asyncio.run(communicate.save(str(file_path)))
            
        if file_path.exists() and file_path.stat().st_size > 0:
            saved = True
    except Exception:
        pass

    # 2. Respaldo mediante gTTS si edge_tts falla
    if not saved:
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang="es", slow=False)
            tts.save(str(file_path))
            if file_path.exists() and file_path.stat().st_size > 0:
                saved = True
        except Exception:
            pass

    if not saved:
        return "No se pudo generar el archivo de audio. Verifique la conexión a internet."

    if open_file and file_path.exists():
        try:
            os.startfile(str(file_path))
        except Exception:
            pass

    return f"¡Archivo de audio MP3 generado con éxito en tu Escritorio!\nArchivo: '{file_path.name}'\nRuta: {file_path}"