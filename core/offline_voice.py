# -*- coding: utf-8 -*-
"""core/offline_voice.py — Sintetizador SAPI nativo de Windows para modo offline."""

import threading
import win32com.client

try:
    import pythoncom
except ImportError:
    pythoncom = None

def speak_offline_error(mensaje: str):
    """
    Usa el sintetizador nativo de Windows (SAPI) con voz en español para hablar
    cuando no hay conexión o la API de Gemini Live no está disponible.
    """
    def _speak():
        if pythoncom:
            try:
                pythoncom.CoInitialize()
            except Exception:
                pass
        try:
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = 1  # Velocidad natural y fluida
            speaker.Volume = 100

            # Seleccionar voz en español si está disponible en Windows
            voices = speaker.GetVoices()
            for v in voices:
                desc = v.GetDescription().lower()
                if "spanish" in desc or "español" in desc or "sabina" in desc or "helena" in desc or "raul" in desc:
                    speaker.Voice = v
                    break

            speaker.Speak(mensaje)
        except Exception:
            pass
        finally:
            if pythoncom:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

    threading.Thread(target=_speak, daemon=True).start()