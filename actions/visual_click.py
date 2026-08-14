# -*- coding: utf-8 -*-

import json
import io
import re
import time
import ctypes
import platform
from pathlib import Path

# Activar concienciación de DPI de Windows para leer píxeles físicos reales
if platform.system() == "Windows":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # PerMonitorV2
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

BASE_DIR = Path(__file__).resolve().parent.parent
API_FILE = BASE_DIR / "config" / "api_keys.json"


def _get_gemini_api_key() -> str:
    try:
        if not API_FILE.exists():
            return ""
        data = json.loads(API_FILE.read_text(encoding="utf-8"))
        return data.get("gemini_api_key", "")
    except Exception:
        return ""


def _extract_json_coords(text: str):
    raw = str(text or "").strip()
    match = re.search(r'\{.*?\}', raw, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if all(k in data for k in ("xmin", "xmax", "ymin", "ymax")):
                if not data.get("found", True):
                    return 0.0, 0.0

                xmin = float(data["xmin"])
                xmax = float(data["xmax"])
                ymin = float(data["ymin"])
                ymax = float(data["ymax"])

                if xmin == 0 and xmax == 0 and ymin == 0 and ymax == 0:
                    return 0.0, 0.0

                center_x = (xmin + xmax) / 2.0
                center_y = (ymin + ymax) / 2.0
                return center_x, center_y
        except Exception:
            pass
    return None


def _get_active_monitor(sct):
    try:
        import pyautogui
        mouse_x, mouse_y = pyautogui.position()
    except Exception:
        mouse_x, mouse_y = 0, 0

    if len(sct.monitors) <= 1:
        return sct.monitors[0]

    for i in range(1, len(sct.monitors)):
        m = sct.monitors[i]
        if (m["left"] <= mouse_x < m["left"] + m["width"] and
                m["top"] <= mouse_y < m["top"] + m["height"]):
            return m

    return sct.monitors[1]


def _capture_screen():
    from PIL import ImageGrab

    try:
        img = ImageGrab.grab(all_screens=True)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        monitor_info = {
            "left": 0,
            "top": 0,
            "width": img.width,
            "height": img.height
        }
        return buffer.getvalue(), monitor_info, img.width, img.height
    except Exception:
        import mss
        from PIL import Image
        with mss.mss() as sct:
            monitor = _get_active_monitor(sct)
            shot = sct.grab(monitor)
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)

            return buffer.getvalue(), monitor, img.width, img.height


def _set_cursor_and_click(target_x: int, target_y: int, clicks: int = 1, button: str = "left", duration: float = 0.35):
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.05

        # 1. Movimiento visible y fluido del cursor hacia las coordenadas objetivo
        pyautogui.moveTo(int(target_x), int(target_y), duration=duration)
        time.sleep(0.12)

        if platform.system() == "Windows":
            try:
                ctypes.windll.user32.SetCursorPos(int(target_x), int(target_y))
                time.sleep(0.05)
            except Exception:
                pass

        # 2. Clic físico con el ratón
        pyautogui.click(clicks=clicks, button=button)
        return True
    except Exception:
        return False


def visual_click(parameters: dict, player=None) -> str:
    element_desc = (
        parameters.get("element_description")
        or parameters.get("action_text")
        or parameters.get("description")
        or parameters.get("target")
        or parameters.get("text")
        or ""
    )

    x = parameters.get("x")
    y = parameters.get("y")

    clicks = int(parameters.get("clicks", 1))
    button = str(parameters.get("button", "left")).lower()
    duration = float(parameters.get("duration", 0.35))

    if not element_desc and (x is None or y is None):
        return "No especificaste qué elemento o coordenada cliquear."

    # Clic directo por coordenadas si fueron provistas
    if x is not None and y is not None:
        try:
            real_x = int(float(x))
            real_y = int(float(y))
            _set_cursor_and_click(real_x, real_y, clicks=clicks, button=button, duration=duration)
            return f"Clic ejecutado en coordenadas fijas X={real_x}, Y={real_y}."
        except Exception as e:
            return f"Error en clic de coordenadas fijas: {e}"

    api_key = _get_gemini_api_key()
    if not api_key:
        return "Error: No se encontró la clave de Gemini en config/api_keys.json."

    if player:
        player.write_log(f"🎯 Localizando en pantalla para mover cursor: '{element_desc}'...")

    try:
        image_bytes, monitor_info, img_w, img_h = _capture_screen()
    except Exception as e:
        return f"Error al capturar la pantalla para el clic: {e}"

    prompt = f"""
Eres un sistema experto de visión artificial de alta precisión para control del mouse.
La imagen proporcionada es la captura de pantalla nativa completa del monitor del usuario.

Objetivo: ENCONTRAR "{element_desc}"

REGLAS DE LOCALIZACIÓN Y POSICIONAMIENTO:
1. Si el usuario pide "primer resultado", "primera opción", "primer enlace" en Google, navegador o búsqueda:
   - Encuentra y encierra la caja del TÍTULO o ENLACE AZUL principal del primer resultado en la lista.
2. Si el usuario pide "segundo resultado", "tercer resultado", etc.:
   - Ubica el título del resultado correspondiente en la lista.
3. Si el usuario pide "primer video" o "primera opción" en YouTube:
   - Encuentra la miniatura o el título del primer video mostrado.
4. Si el usuario especifica un botón, icono, imagen, pestaña o campo de texto:
   - Encuentra el centro exacto del elemento indicado.

CUADRÍCULA NORMALIZADA (0 a 1000):
- xmin, xmax: 0 (borde izquierdo) a 1000 (borde derecho).
- ymin, ymax: 0 (borde superior) a 1000 (borde inferior).

Responde ÚNICAMENTE con un bloque JSON válido con este formato:
{{
  "found": true,
  "xmin": 250,
  "ymin": 180,
  "xmax": 520,
  "ymax": 210
}}

Si el elemento NO se encuentra en pantalla, devuelve:
{{
  "found": false,
  "xmin": 0, "ymin": 0, "xmax": 0, "ymax": 0
}}

No agregues markdown adicional ni explicaciones.
"""

    from google import genai
    from google.genai import types

    try:
        client = genai.Client(api_key=api_key)

        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/jpeg",
                                data=image_bytes
                            )
                        )
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=150
            )
        )

        raw_text = resp.text.strip()
        coords = _extract_json_coords(raw_text)

        if not coords:
            return f"No se pudo determinar las coordenadas de '{element_desc}'. Respuesta: {raw_text}"

        x_1000, y_1000 = coords
        if x_1000 == 0.0 and y_1000 == 0.0:
            return f"No encontré visible en pantalla el elemento: '{element_desc}'."

        import pyautogui
        scr_w, scr_h = pyautogui.size()

        # Mapeo directo a las coordenadas lógicas de pyautogui
        monitor_left = monitor_info.get("left", 0)
        monitor_top = monitor_info.get("top", 0)

        real_x = monitor_left + int((x_1000 / 1000.0) * scr_w)
        real_y = monitor_top + int((y_1000 / 1000.0) * scr_h)

        real_x = max(0, min(scr_w - 1, real_x))
        real_y = max(0, min(scr_h - 1, real_y))

        _set_cursor_and_click(real_x, real_y, clicks=clicks, button=button, duration=duration)

        if player:
            player.write_log(f"🖱️ Cursor movido y clic ejecutado en X={real_x}, Y={real_y} ('{element_desc}').")

        return f"Moví el cursor y hice clic exactamente en '{element_desc}'."

    except Exception as e:
        return f"Error procesando la visión de clic con Gemini: {e}"