# -*- coding: utf-8 -*-

import os
import time
import subprocess
import webbrowser
import urllib.parse
import json
from pathlib import Path

try:
    import pyautogui
    import pyperclip
    import pygetwindow as gw
except ImportError:
    pyautogui = None
    pyperclip = None
    gw = None

# ==========================================
# BASE DE DATOS DE USUARIOS DE TIKTOK
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
TIKTOK_DB_FILE = BASE_DIR / "config" / "tiktok_users.json"

def load_tiktok_users():
    if TIKTOK_DB_FILE.exists():
        try:
            return json.loads(TIKTOK_DB_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_tiktok_users(data):
    try:
        TIKTOK_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        TIKTOK_DB_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
    except Exception:
        pass

# ==========================================
# BUSCADOR INTELIGENTE DE VIDEOS
# ==========================================
def find_file_smart(filename):
    clean_name = filename.replace('"', '').replace("'", "").strip()
    if os.path.exists(clean_name): return os.path.abspath(clean_name)
        
    name_only = os.path.splitext(os.path.basename(clean_name))[0].lower()
    stop_words = ["el", "la", "los", "las", "un", "una", "archivo", "foto", "documento", "video", "de", "imagen", "carpeta", "rar", "zip"]
    clean_words = [w for w in name_only.split() if w not in stop_words and len(w) > 2]
    
    home = Path.home()
    search_dirs = [
        home / "Downloads", home / "Desktop", home / "Documents", home / "Pictures", home / "Videos",
        home / "OneDrive" / "Escritorio", home / "OneDrive" / "Documentos"
    ]
    
    most_recent_time = 0
    best_match = None
    
    for directory in search_dirs:
        if not directory.exists(): continue
        try:
            for root, dirs, files in os.walk(directory):
                if root.replace(str(directory), "").count(os.sep) > 3:
                    del dirs[:]
                    continue
                for f in files:
                    f_lower = f.lower()
                    f_no_ext = os.path.splitext(f_lower)[0]
                    
                    match_found = False
                    if name_only == f_no_ext or name_only in f_no_ext: match_found = True
                    elif len(clean_words) > 0 and all(word in f_no_ext for word in clean_words): match_found = True
                            
                    if match_found:
                        file_path = os.path.join(root, f)
                        file_time = os.path.getmtime(file_path)
                        if file_time > most_recent_time:
                            most_recent_time = file_time
                            best_match = file_path
        except Exception:
            pass
            
    return best_match

# ==========================================
# CONTROL DE PESTAÑAS Y ENFOQUE (NO MÁS PESTAÑAS NUEVAS)
# ==========================================
def focus_tiktok():
    """Busca la ventana de TikTok y la trae al frente."""
    if not gw: return False
    try:
        for win in gw.getAllWindows():
            if "tiktok" in win.title.lower() or "navegador" in win.title.lower() or "chrome" in win.title.lower() or "opera" in win.title.lower():
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.3)
                return True
    except Exception:
        pass
    return False

def navigate_in_current_tab(url):
    """Navega usando la pestaña actual para no llenar el navegador de pestañas basura."""
    focused = focus_tiktok()
    if focused:
        pyautogui.hotkey('ctrl', 'l') # Selecciona la barra de direcciones
        time.sleep(0.5)
        pyperclip.copy(url)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
    else:
        webbrowser.open(url) # Solo abre una nueva si el navegador estaba cerrado

# ==========================================
# AGENTE DE TIKTOK INFALIBLE
# ==========================================
def tiktok_analyzer(parameters: dict, player=None) -> str:
    if not pyautogui:
        return "Faltan librerías. Ejecuta en terminal: pip install pyautogui pyperclip pygetwindow"

    action = parameters.get("action", "").lower()
    contact = parameters.get("contact", "")
    text = parameters.get("text", "")
    file_path = parameters.get("file_path", "")

    if player:
        player.write_log(f"🎵 Ejecutando acción '{action}' en TikTok...")

    try:
        # ==========================================
        # 1. GESTIÓN DINÁMICA DE PERFILES
        # ==========================================
        if action == "set_profile":
            if not contact: return "Dime cuál es tu usuario para guardarlo."
            clean_username = contact.replace("@", "").strip()
            db = load_tiktok_users()
            db["current_user"] = clean_username
            save_tiktok_users(db)
            return f"He guardado tu usuario como @{clean_username}. Ahora cuando me pidas ir a tu perfil, sabré que eres tú."

        # ==========================================
        # 2. CONTROLES DE REPRODUCCIÓN (Click Central Infalible)
        # ==========================================
        elif action in ["scroll_down", "scroll_up", "play_pause", "mute", "video_profile"]:
            focus_tiktok()
            screen_w, screen_h = pyautogui.size()
            center_x, center_y = screen_w / 2, screen_h / 2
            
            if action == "scroll_down":
                pyautogui.press('down')
                return "Deslizando al siguiente video."
            elif action == "scroll_up":
                pyautogui.press('up')
                return "Regresando al video anterior."
            elif action == "play_pause":
                # CLIC EXACTO EN EL CENTRO PARA PAUSAR/REPRODUCIR SIN FALLOS
                pyautogui.click(center_x, center_y)
                return "Reproducción pausada o reanudada."
            elif action == "mute":
                pyautogui.press('m') 
                return "Audio silenciado/activado."
            elif action == "video_profile":
                pyautogui.press('enter')
                return "Abriendo el perfil del creador."
            
        # ==========================================
        # 3. NAVEGACIÓN EN LA MISMA PESTAÑA
        # ==========================================
        elif action == "search":
            if not text: return "Dime qué quieres buscar."
            safe_query = urllib.parse.quote(text)
            navigate_in_current_tab(f"https://www.tiktok.com/search?q={safe_query}")
            return f"Buscando videos sobre '{text}'."
            
        elif action == "view_profile":
            db = load_tiktok_users()
            my_user = db.get("current_user", "")
            if my_user:
                navigate_in_current_tab(f"https://www.tiktok.com/@{my_user}")
                return f"Abriendo tu perfil personal (@{my_user})."
            else:
                return "Aún no me has dicho cuál es tu usuario. Dime: 'Jarvis, mi usuario de TikTok es @tu_nombre'."
            
        elif action == "view_activity":
            navigate_in_current_tab("https://www.tiktok.com/messages")
            return "Abriendo tu bandeja de mensajes."

        # ==========================================
        # 4. COMUNICACIÓN
        # ==========================================
        elif action == "send_message":
            if not contact: return "Debes decirme a quién enviarle el mensaje."
            navigate_in_current_tab("https://www.tiktok.com/messages")
            time.sleep(7)
            pyautogui.press('tab', presses=3, interval=0.1)
            pyautogui.write(contact)
            time.sleep(2.5)
            pyautogui.press('down')
            pyautogui.press('enter')
            time.sleep(1.5)
            if text:
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                pyautogui.press('enter')
            return f"Mensaje enviado a {contact}."

        # ==========================================
        # 5. SUBIDA 100% AUTOMATIZADA (TikTok Studio)
        # ==========================================
        elif action == "post_video":
            abs_path = find_file_smart(file_path)
            if not abs_path: return f"Error: No encontré el video '{file_path}' en tu PC."
            
            navigate_in_current_tab("https://www.tiktok.com/creator-center/upload")
            if player: player.write_log("⚠️ Preparando automatización de subida. No toques el mouse...")
            
            # Esperar a que cargue el Studio
            time.sleep(10) 
            
            # 1. Hacer clic en el centro de la pantalla (Donde está el botón "Seleccionar Archivo")
            screen_w, screen_h = pyautogui.size()
            pyautogui.click(screen_w / 2, screen_h / 2)
            time.sleep(2.5) # Esperar a que aparezca la ventana blanca de Windows
            
            # 2. Pegar la ruta del archivo y presionar Enter
            pyperclip.copy(abs_path)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)
            pyautogui.press('enter')
            
            # 3. Escribir descripción si existe
            if text: 
                time.sleep(8) # Dar tiempo a que el video cargue en la web
                pyautogui.press('tab', presses=4, interval=0.2) 
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                
            return "Video subido con éxito a TikTok Studio. Revisa los detalles y dale a Publicar."

        return f"Acción '{action}' no reconocida para TikTok."

    except Exception as e:
        if player: player.write_log(f"❌ Error en TikTok Analyzer: {str(e)}")
        return f"Error crítico al controlar TikTok: {str(e)}"