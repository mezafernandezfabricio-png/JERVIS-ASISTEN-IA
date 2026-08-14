# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
API_FILE = BASE_DIR / "config" / "api_keys.json"

def _get_api_config() -> dict:
    try:
        if API_FILE.exists():
            return json.loads(API_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def turn_on_camera_and_describe(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """Captura un fotograma de la cámara web y describe detalladamente lo que ve usando visión por IA."""
    parameters = parameters or {}
    query = parameters.get("text") or parameters.get("prompt") or parameters.get("query") or "¿Qué estoy viendo en la cámara?"

    if player:
        player.write_log("📷 Accediendo al sensor de cámara para análisis visual...")

    try:
        import cv2
    except ImportError:
        return "Error: OpenCV no está instalado. Ejecute 'pip install opencv-python'."

    cfg = _get_api_config()
    camera_idx = cfg.get("camera_index", 0)
    api_key = cfg.get("gemini_api_key", "")

    if not api_key:
        return "Error: No se encontró la API Key de Gemini en config/api_keys.json."

    cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(camera_idx)
    if not cap.isOpened():
        return f"Error: No se pudo abrir la cámara en el índice {camera_idx}. Verifique la conexión del dispositivo."

    try:
        # Descartar primeros fotogramas para autoexposición
        for _ in range(5):
            cap.read()
        ret, frame = cap.read()
    finally:
        cap.release()

    if not ret or frame is None:
        return "Error: No se pudo capturar un fotograma nítido de la cámara."

    try:
        from google import genai
        from google.genai import types

        # Codificar a JPEG
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        image_bytes = buffer.tobytes()

        client = genai.Client(api_key=api_key)
        prompt = (
            f"Actúa como el módulo de visión artificial de JARVIS. El usuario pregunta: '{query}'. "
            "Describe con claridad lo que observas frente a la cámara (personas, objetos, entorno, texto visible). "
            "Responde en español natural, conciso y fluido. No uses markdown ni listas con asteriscos."
        )

        parts = [
            types.Part(text=prompt),
            types.Part(inline_data=types.Blob(data=image_bytes, mime_type="image/jpeg"))
        ]

        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[types.Content(parts=parts)]
        )

        result_text = resp.text.strip()
        if player:
            player.write_log("📷 Análisis de cámara completado.")
        return result_text

    except Exception as e:
        return f"Error procesando la imagen con Gemini Vision: {e}"