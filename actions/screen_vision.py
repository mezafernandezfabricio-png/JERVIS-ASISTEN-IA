# -*- coding: utf-8 -*-
import os
import json
import io
from pathlib import Path
from datetime import datetime
from PIL import ImageGrab, Image

API_FILE = Path("config/api_keys.json")

def _get_gemini_api_key() -> str:
    try:
        data = json.loads(API_FILE.read_text(encoding="utf-8"))
        return data.get("gemini_api_key", "")
    except Exception:
        return ""

def _screenshots_dir() -> Path:
    userprofile = os.environ.get("USERPROFILE", str(Path.home()))
    folder = Path(userprofile) / "Pictures" / "Screenshots"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def _safe_name(name: str) -> str:
    name = str(name or "Captura_JARVIS").strip()
    clean = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    return clean.replace(" ", "_") or "Captura_JARVIS"

def _clean_text(text: str) -> str:
    return str(text or "").replace("*", "").replace("#", "").replace("_", "").strip()

def _should_save_from_query(query: str) -> bool:
    q = str(query or "").lower()
    save_words = ["guardar", "guarda", "toma", "tomar", "captura", "capture", "screenshot", "save"]
    analyze_words = ["analiza", "analizar", "qué ves", "que ves", "describe", "describir"]
    return any(w in q for w in save_words) and not any(w in q for w in analyze_words)

def _capture_image(parameters: dict):
    action = str(parameters.get("action", "analyze")).lower().strip()
    
    x = parameters.get("x")
    y = parameters.get("y")
    width = parameters.get("width")
    height = parameters.get("height")

    is_region = action in ["region", "captura_region", "specific", "especifica", "captura_especifica", "save_region", "guardar_region"]

    if is_region and None not in (x, y, width, height):
        bbox = (int(float(x)), int(float(y)), int(float(x)) + int(float(width)), int(float(y)) + int(float(height)))
        img = ImageGrab.grab(bbox=bbox, all_screens=True)
        capture_type = "especifica"
    else:
        img = ImageGrab.grab(all_screens=True)
        capture_type = "completa"

    return img, capture_type

def _save_capture(img, capture_type: str, filename: str = "") -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe = _safe_name(filename or "Captura_JARVIS")
    file_name = f"{safe}_{capture_type}_{timestamp}.png"
    filepath = _screenshots_dir() / file_name
    img.save(filepath, format="PNG")
    return filepath

def _analyze_with_ai(img, query: str, player=None) -> str:
    from google import genai
    from google.genai import types

    api_key = _get_gemini_api_key()
    if not api_key:
        return "Error: No se encontró la clave de Gemini en config/api_keys.json."

    if not query:
        query = "Describe todo lo que ves en mi pantalla con un nivel de detalle extremo."

    if player:
        player.write_log("👁️ Escaneando la pantalla a resolución nativa completa...")

    try:
        img_ai = img.copy()

        # Usar resolución nativa completa con compresión de alta calidad
        buffer = io.BytesIO()
        img_ai.save(buffer, format="JPEG", quality=95)
        image_bytes = buffer.getvalue()

        client = genai.Client(api_key=api_key)
        
        prompt_maestro = (
            "Actúa como un experto en análisis visual de interfaces de usuario y sistemas operativos. "
            f"El usuario te pregunta: '{query}'. "
            "Realiza un análisis completo y exhaustivo de todo lo que hay en la pantalla: "
            "1. Ventanas y aplicaciones activas o visibles (Navegador, VS Code, Explorador, Juegos, etc.). "
            "2. Contenido web en pantalla (si hay Google, lee las búsquedas y resultados principales; si es YouTube, lee los títulos de videos principales; si hay artículos o PDFs, resume los textos clave). "
            "3. Pestañas abiertas, botones principales, barra de tareas e iconos visibles. "
            "4. Describe el estado general y el contexto exacto de lo que está haciendo el usuario. "
            "Responde en español conversacional, estructurado, natural y fluido."
        )

        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt_maestro),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/jpeg",
                                data=image_bytes
                            )
                        )
                    ]
                )
            ]
        )
        return _clean_text(resp.text)

    except Exception as e:
        return f"Error al analizar la pantalla con Gemini: {str(e)}"

def screen_vision(parameters: dict, player=None) -> str:
    action = str(parameters.get("action", "analyze")).lower().strip()
    query = parameters.get("query") or parameters.get("text") or parameters.get("question") or ""
    filename = parameters.get("filename") or parameters.get("name") or parameters.get("title") or "Captura_JARVIS"

    if _should_save_from_query(query) or parameters.get("save") is True or action in ["captura", "screenshot", "full", "completa", "tomar_captura"]:
        action = "save"

    if action in ["analizar", "describe", "describir", "qué_ves", "que_ves"]:
        action = "analyze"

    if action in ["analyze_region", "analizar_region"]:
        action = "region_analyze"

    try:
        if action == "region_analyze":
            capture_params = dict(parameters)
            capture_params["action"] = "region"
        else:
            capture_params = parameters

        img, capture_type = _capture_image(capture_params)
    except Exception as e:
        return f"Error al intentar capturar la pantalla: {e}"

    if action in ["save", "guardar", "region", "captura_region", "specific", "especifica", "captura_especifica", "save_region", "guardar_region"]:
        try:
            filepath = _save_capture(img, capture_type, filename)
            msg = f"He tomado la captura {capture_type}. Está guardada como '{filepath.name}' en Imágenes/Screenshots."
            if player:
                player.write_log(f"📸 {msg}")
            return msg
        except Exception as e:
            return f"Error al intentar guardar la captura de pantalla: {e}"

    return _analyze_with_ai(img, query, player)