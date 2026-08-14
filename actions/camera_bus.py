# -*- coding: utf-8 -*-

import json
import base64
import urllib.request
import urllib.error
import time
from pathlib import Path


API_FILE = Path("config/api_keys.json")


def _get_api_key() -> str:
    try:
        data = json.loads(API_FILE.read_text(encoding="utf-8"))
        return data.get("openrouter_api_key", "")
    except Exception:
        return ""


def _capture_best_frame(camera_index: int = 0, frames: int = 25):
    import cv2
    from PIL import Image

    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise Exception(
            "No pude acceder a la cámara. Activa el permiso de cámara en Windows y cierra Zoom, Meet, OBS, Discord o WhatsApp."
        )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

    time.sleep(0.8)

    best_frame = None
    best_score = -1

    for _ in range(frames):
        ret, frame = cap.read()

        if not ret or frame is None:
            time.sleep(0.04)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = gray.mean()

        score = sharpness - abs(brightness - 130)

        if score > best_score:
            best_score = score
            best_frame = frame.copy()

        time.sleep(0.04)

    cap.release()

    if best_frame is None:
        raise Exception("La cámara abrió, pero no capturó una imagen válida.")

    frame_rgb = cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame_rgb)

    image.thumbnail((1600, 1200), Image.Resampling.LANCZOS)

    return image


def _image_to_base64(image) -> str:
    import io

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=94)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def camera_bus(parameters: dict, player=None) -> str:
    """
    Activa la cámara, captura el objeto en la mano y lo analiza con IA multimodal.
    """

    query = (
        parameters.get("query")
        or parameters.get("text")
        or parameters.get("question")
        or "¿Qué tengo en la mano? Dame una descripción exacta y precisa del objeto."
    )

    camera_index = int(parameters.get("camera_index", 0))
    frames = int(parameters.get("frames", 25))

    api_key = _get_api_key()

    if not api_key:
        return "Error: No encontré openrouter_api_key en config/api_keys.json."

    try:
        import cv2
        from PIL import Image
    except ImportError:
        return "Faltan dependencias. Instala: pip install opencv-python pillow"

    if player:
        player.write_log("📷 Encendiendo cámara para analizar el objeto en tu mano...")

    try:
        image = _capture_best_frame(camera_index=camera_index, frames=frames)
        b64_image = _image_to_base64(image)

    except Exception as e:
        return (
            "No pude usar la cámara. Revisa esto: Configuración de Windows, Privacidad y seguridad, Cámara. "
            "Activa acceso a la cámara y permite aplicaciones de escritorio. "
            "También cierra Zoom, Meet, OBS, Discord, WhatsApp o cualquier app que use la cámara. "
            f"Detalle técnico: {e}"
        )

    prompt = f"""
Actúa como un experto en identificación visual de objetos, productos y materiales.

El usuario pregunta:
{query}

Analiza principalmente lo que la persona sostiene en la mano.

Tu respuesta debe ser muy precisa, pero sin inventar datos que no se vean.

Incluye:
Qué objeto es.
Marca o modelo si se puede leer o reconocer claramente.
Color exacto o aproximado.
Materiales visibles.
Forma, tamaño aproximado y detalles físicos.
Texto visible, logos, etiquetas, símbolos o números.
Estado del objeto: nuevo, usado, dañado, sucio, roto, incompleto o bien conservado.
Posible función o uso.
Especificaciones deducibles visualmente.
Advertencias si algo no se puede confirmar.
Recomendación práctica según el objeto.

Reglas:
No inventes marca, modelo o especificaciones si no son visibles.
Si el objeto está borroso, parcialmente tapado o mal iluminado, dilo.
Responde en español natural.
Usa frases cortas.
No uses markdown.
No uses asteriscos.
Termina cada oración correctamente.
"""

    payload = {
        "model": "google/gemini-2.5-flash",
        "max_tokens": 1400,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/jarvis-beta",
        "X-Title": "JARVIS Camera Object Vision",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        if player:
            player.write_log("🧠 Analizando objeto con IA visual...")

        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))

        if "choices" not in data or not data["choices"]:
            return "La IA no devolvió una respuesta válida."

        answer = data["choices"][0]["message"]["content"]

        answer = (
            answer.replace("*", "")
            .replace("#", "")
            .replace("_", "")
            .strip()
        )

        try:
            image.close()
        except Exception:
            pass

        if player:
            player.write_log("✅ Análisis del objeto completado.")

        return answer

    except urllib.error.HTTPError as e:
        return f"Error HTTP {e.code} conectando con OpenRouter. Revisa tu API key o saldo."

    except Exception as e:
        return f"Error analizando el objeto con IA: {e}"