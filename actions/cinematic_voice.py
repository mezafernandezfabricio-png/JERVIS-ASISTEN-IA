# -*- coding: utf-8 -*-
"""cinematic_voice.py — Síntesis de voz neural ultra-fluida y sin cortes para JARVIS."""

import os
import re
import json
import queue
import threading
import tempfile
import time
import asyncio
from pathlib import Path

# Ocultar el mensaje de bienvenida de pygame en la terminal
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

_pygame = None
_mixer_initialized = False

def _ensure_mixer():
    global _pygame, _mixer_initialized
    if _mixer_initialized:
        return True
    try:
        import pygame
        _pygame = pygame
        _pygame.mixer.init()
        _mixer_initialized = True
        return True
    except Exception as e:
        print(f"[CinematicVoice] Pygame mixer init warning: {e}")
        return False

_text_queue = queue.Queue()
_audio_queue = queue.Queue()
_worker_started = False

def _get_neural_voice() -> str:
    try:
        cfg_path = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            live_voice = cfg.get("jarvis_voice", "Aoede")
            voice_map = {
                "Aoede": "es-MX-DaliaNeural",
                "Charon": "es-MX-JorgeNeural",
                "Puck": "es-MX-CecilioNeural",
                "Kore": "es-US-PalomaNeural",
                "Fenrir": "es-ES-AlvaroNeural",
                "Leda": "es-ES-ElviraNeural",
                "Orus": "es-MX-JorgeNeural",
                "Zephyr": "es-MX-DaliaNeural",
            }
            return voice_map.get(live_voice, "es-MX-DaliaNeural")
    except Exception:
        pass
    return "es-MX-DaliaNeural"

def _clean_text(text: str) -> str:
    text = str(text or "")
    replacements = {
        "*": "", "#": "", "_": "", "`": "", "|": "", 
        "[": "", "]": "", "{": "", "}": "", "<": "", ">": "",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("...", ".").replace("!!", "!").replace("??", "?")
    return text

def _split_sentences(text: str, max_len: int = 150) -> list[str]:
    text = _clean_text(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for part in parts:
        part = part.strip()
        if not part: continue
        if len(current) + len(part) <= max_len:
            current = f"{current} {part}".strip()
        else:
            if current: chunks.append(current)
            current = part
    if current:
        chunks.append(current)
    return chunks

async def _synthesize_chunk_async(chunk: str, voice: str, output_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(chunk, voice, rate="+3%", volume="+0%")
    await communicate.save(output_path)

def _generation_worker():
    """Hilo de generación neural directa de texto a MP3."""
    while True:
        text = _text_queue.get()
        if text is None:
            break

        try:
            chunks = _split_sentences(text)
            voice_name = _get_neural_voice()

            for idx, chunk in enumerate(chunks):
                if not chunk.endswith((".", "!", "?")):
                    chunk += "."

                temp_file = os.path.join(
                    tempfile.gettempdir(),
                    f"jarvis_voice_{threading.get_ident()}_{time.time()}_{idx}.mp3"
                )

                try:
                    # Síntesis directa usando la librería edge_tts en Python (sin overhead de CLI)
                    asyncio.run(_synthesize_chunk_async(chunk, voice_name, temp_file))
                except Exception as ex:
                    # Fallback CLI si asyncio.run tuviera algún conflicto de loop
                    import subprocess
                    cmd = [
                        "edge-tts",
                        "--voice", voice_name,
                        "--rate", "+3%",
                        "--text", chunk,
                        "--write-media", temp_file
                    ]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)

                if os.path.exists(temp_file):
                    _audio_queue.put(temp_file)

        except Exception as e:
            print(f"[CinematicVoice] Error generando audio: {e}")
        finally:
            _text_queue.task_done()

def _playback_worker():
    """Hilo de reproducción fluida continua sin cortes."""
    while True:
        audio_file = _audio_queue.get()
        if audio_file is None:
            break

        try:
            if _ensure_mixer() and _pygame:
                _pygame.mixer.music.load(audio_file)
                _pygame.mixer.music.play()
                while _pygame.mixer.music.get_busy():
                    _pygame.time.Clock().tick(15)
        except Exception as e:
            print(f"[CinematicVoice] Error reproduciendo audio: {e}")
        finally:
            try:
                if _pygame:
                    _pygame.mixer.music.unload()
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except Exception:
                pass
            _audio_queue.task_done()

def _ensure_workers():
    """Asegura que los procesos de generación y reproducción estén activos."""
    global _worker_started
    if not _worker_started:
        threading.Thread(target=_generation_worker, daemon=True).start()
        threading.Thread(target=_playback_worker, daemon=True).start()
        _worker_started = True

def cinematic_voice(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Voz cinematográfica fluida para JARVIS.
    """
    parameters = parameters or {}
    text = parameters.get("text", "")
    if not text:
        return "No se especificó ningún texto para leer."

    _ensure_workers()
    clean = _clean_text(text)
    _text_queue.put(clean)

    if player:
        player.write_log("🎙️ Voz neural fluida enviada a reproducción.")
    return "Hablando de forma fluida."