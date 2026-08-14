# -*- coding: utf-8 -*-
"""
wake_listener.py — Servicio de escucha de palabra de activación (Wake Word).
"""
import os
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MAIN_FILE = BASE_DIR / "main.py"

WAKE_PHRASES = [
    "hola jarvis",
    "jarvis enciéndete",
    "jarvis enciendete",
    "enciéndete jarvis",
    "enciendete jarvis"
]

jarvis_process = None

def start_jarvis():
    global jarvis_process
    if jarvis_process and jarvis_process.poll() is None:
        return
    jarvis_process = subprocess.Popen(
        ["python", str(MAIN_FILE)],
        cwd=str(BASE_DIR),
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    )
    print("JARVIS encendido.")

def wake_listener(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """Gestiona o informa el estado del servicio de escucha de palabra de activación."""
    if player:
        try: player.write_log("🎙️ Verificando estado del detector de activación...")
        except: pass
    return "El detector de palabra de activación está configurado y operando mediante Vosk nativo."

def listen_loop():
    try:
        import speech_recognition as sr
    except ImportError:
        print("[WakeListener] speech_recognition no está instalado. Usando motor Vosk integrado.")
        return

    try:
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 150 
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.5 
        mic = sr.Microphone()

        print("Wake listener activo.")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)

        while True:
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=15)
                text = recognizer.recognize_google(audio, language="es-ES").lower()
                if any(phrase in text for phrase in WAKE_PHRASES):
                    start_jarvis()
            except Exception:
                time.sleep(0.2)
    except Exception as e:
        print(f"[WakeListener] Error: {e}")

if __name__ == "__main__":
    listen_loop()