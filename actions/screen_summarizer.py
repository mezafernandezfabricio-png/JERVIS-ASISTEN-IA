import time
import pyautogui
import pyperclip

def screen_summarizer(parameters: dict, player=None, speak=None) -> str:
    """
    Ejecuta Ctrl+A y Ctrl+C para extraer el texto de la pantalla activa,
    restaura el portapapeles del usuario y devuelve el texto para ser resumido.
    """
    # 1. Guardar el portapapeles actual para no borrar lo que ya tenías copiado
    old_clipboard = pyperclip.paste()

    # 2. Seleccionar todo y copiar
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)  # Pequeño respiro para que el SO reaccione
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)  # Tiempo de gracia para que el texto cargue en la memoria

    # 3. Extraer el texto copiado
    copied_text = pyperclip.paste()

    # 4. Quitar la selección azul de la pantalla (presionando flecha derecha)
    pyautogui.press('right')

    # 5. Restaurar el portapapeles original silenciosamente
    pyperclip.copy(old_clipboard)

    # 6. Validar si logramos extraer algo útil
    if not copied_text or len(copied_text.strip()) < 10:
        return "[SISTEMA] No se pudo extraer texto. Dile al usuario que asegure que la ventana actual permite selección de texto."

    # 7. Límite de seguridad para no ahogar el contexto (50,000 caracteres)
    if len(copied_text) > 50000:
        copied_text = copied_text[:50000] + "\n... [TEXTO TRUNCADO POR LÍMITE]"

    # 8. Retornar el texto con la directiva psicológica ("Jedi Mind Trick") para JARVIS
    return (
        f"TEXTO EXTRAÍDO DE LA PANTALLA:\n\"\"\"\n{copied_text}\n\"\"\"\n\n"
        "INSTRUCCIÓN OBLIGATORIA: Resume este texto de forma conversacional, directa y fluida. "
        "Ve directo al grano, ignorando menús o texto basura de la página web. "
        "Empieza tu respuesta diciendo exactamente: 'Básicamente, este artículo dice que...' "
        "o 'Básicamente, lo que tienes en pantalla es...'"
    )