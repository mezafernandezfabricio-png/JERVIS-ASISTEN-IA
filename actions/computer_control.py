import time

def computer_control(parameters: dict, player=None) -> str:
    """Toma control del teclado o ratón para ejecutar acciones físicas en la PC."""
    action = parameters.get("action", "").lower()
    text = parameters.get("text", "")
    
    try:
        # ---------------------------------------------------------
        # ACCIÓN 1: ESCRIBIR LETRA POR LETRA (Estilo Humano)
        # ---------------------------------------------------------
        if action in ["type", "smart_type", "escribir"]:
            if not text:
                return "No me proporcionaste el texto para escribir."
            
            try:
                import keyboard
            except ImportError:
                return "Falta el controlador de teclado avanzado. Ejecuta: pip install keyboard"
            
            if player:
                player.write_log("⌨️ Redactando texto en el documento...")
                
            # Hacemos una pausa de 1 segundo antes de empezar a escribir.
            # Esto es vital para darte tiempo de soltar el botón del micrófono o ratón.
            time.sleep(1.0)
            
            # El parámetro 'delay=0.03' dicta la velocidad. (0.03s entre teclas es un humano rápido).
            keyboard.write(text, delay=0.03)
            
            return "He terminado de redactar el texto, señor."
            
        # ---------------------------------------------------------
        # ACCIÓN 2: PEGAR DE GOLPE (Para bloques de texto gigantes)
        # ---------------------------------------------------------
        elif action in ["paste", "pegar"]:
            if not text:
                return "No me diste texto para pegar."
            try:
                import pyperclip
                import pyautogui
            except ImportError:
                return "Ejecuta en consola: pip install pyperclip pyautogui"
            
            pyperclip.copy(text)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'v')
            
            if player:
                player.write_log("📋 Texto pegado de manera instantánea.")
            return "He pegado el texto en tu documento."
            
        # ---------------------------------------------------------
        # ACCIÓN 3: ATAJOS DE TECLADO Y CLICS SIMPLES
        # ---------------------------------------------------------
        elif action in ["hotkey", "press"]:
            keys = parameters.get("keys") or parameters.get("key")
            if not keys:
                return "No me especificaste qué tecla presionar."
            
            try:
                import pyautogui
                teclas = keys.replace(" ", "").split("+")
                pyautogui.hotkey(*teclas)
                return f"He presionado el atajo '{keys}'."
            except ImportError:
                return "Falta la librería pyautogui."
                
        else:
            return f"Acción de control '{action}' finalizada."

    except Exception as e:
        return f"Ocurrió un error en mis actuadores mecánicos: {e}"
    
    import cv2
import time

def front_camera_vision(parameters: dict, player=None) -> str:
    """
    Enciende la cámara frontal/webcam, toma una foto y la analiza con IA.
    """
    action = parameters.get("action", "analyze").lower()
    query = parameters.get("query") or parameters.get("text") or parameters.get("question") or ""

    if not query:
        query = "Analiza con detalle lo que estoy mostrando frente a la cámara."

    api_key = _get_api_key()
    if not api_key:
        return "Error: No se encontró una clave de OpenRouter en config/api_keys.json."

    if player:
        player.write_log("📷 Encendiendo cámara frontal...")

    try:
        cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            return "No pude acceder a la cámara. Verifica que esté conectada o que otra app no la esté usando."

        time.sleep(1)

        ret, frame = cam.read()
        cam.release()

        if not ret:
            return "No pude capturar imagen desde la cámara."

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

    except Exception as e:
        return f"Error al usar la cámara: {e}"

    try:
        img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        b64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        return f"Error al procesar la imagen de la cámara: {e}"

    prompt_maestro = (
        f"Actúa como un analista visual experto. "
        f"Esta imagen viene de mi cámara frontal o webcam. "
        f"El usuario pide: '{query}'. "
        f"Analiza todo lo visible con detalle: objetos, textos, personas, gestos, colores, posición, contexto y posibles instrucciones. "
        f"Responde directo, natural, sin markdown, sin asteriscos y sin formato raro."
    )

    payload = {
        "model": "google/gemini-2.5-flash",
        "max_tokens": 2000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_maestro},
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

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/jarvis-beta",
        "X-Title": "JARVIS AI Assistant",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=40) as response:
            response_data = json.loads(response.read().decode("utf-8"))

        if "choices" in response_data and len(response_data["choices"]) > 0:
            texto = response_data["choices"][0]["message"]["content"]
            return texto.replace("*", "").replace("#", "").replace("_", "")

        return "Error: Respuesta inesperada del sistema visual."

    except urllib.error.HTTPError as e:
        return f"Error de conexión visual con cámara (HTTP {e.code})."
    except Exception as e:
        return f"Error al conectar con los servidores de visión: {str(e)}"