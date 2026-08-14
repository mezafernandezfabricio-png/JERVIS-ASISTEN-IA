import sys
import os
import subprocess
import time
import pyautogui

def deep_work(parameters: dict, player=None, speak=None) -> str:
    minutos = parameters.get("minutos", 60)
    end_time = time.time() + (minutos * 60)
    
    # DETECCIÓN INTELIGENTE DE ENTORNO
    if getattr(sys, 'frozen', False):
        # MODO PÚBLICO: Estamos en el archivo .exe final. 
        # El ejecutable se invoca a sí mismo, pero con la orden oculta "--warden"
        executable_path = sys.executable
        comando = [executable_path, "--warden", str(end_time)]
    else:
        # MODO DESARROLLO: Estamos en tu PC programando
        venv_pythonw = os.path.join(".venv", "Scripts", "pythonw.exe")
        comando = [venv_pythonw, "warden.py", str(end_time)]
    
    try:
        subprocess.Popen(comando, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        return f"[ERROR] No se pudo invocar al Guardián: {e}"

    # Activar No Molestar en Windows
    pyautogui.hotkey('win', 'n')
    time.sleep(0.5)

    return (
        f"Se ha activado el Protocolo de Trabajo Profundo por {minutos} minutos. "
        "Distracciones bloqueadas a nivel de sistema. A trabajar."
    )