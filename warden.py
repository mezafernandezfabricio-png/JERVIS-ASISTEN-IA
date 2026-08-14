import time
import sys
import os
import psutil
import pygetwindow as gw
import pyautogui

# 1. LA LISTA NEGRA DE PROCESOS (Juegos PC, Tiendas y Emuladores)
FORBIDDEN_PROCESSES = [
    "steam.exe", "epicgameslauncher.exe", "riotclient.exe", "discord.exe",
    "gog galaxy.exe", "battlenet.exe", "origin.exe", "ea.exe",
    "valorant.exe", "leagueoflegends.exe", "minecraft.exe", "robloxplayerbeta.exe",
    "csgo.exe", "dota2.exe", "gtav.exe", "fortniteclient-win64-shipping.exe",
    "bluestacks.exe", "hd-player.exe", "nox.exe", "ldplayer.exe", "memu.exe",
    "retroarch.exe", "dolphin.exe", "pcsx2.exe", "rpcs3.exe", "yuzu.exe", 
    "ryujinx.exe", "cemu.exe", "citra.exe"
]

# 2. EL RADAR DE CARPETAS HEURÍSTICO
FORBIDDEN_PATHS = [
    "\\games\\", "\\juegos\\", "\\steamapps\\", "\\xboxgames\\",
    "epic games", "riot games", "bluestacks", "emulator", "emulador", "elamigos", "fitgirl"
]

# 3. INTERCEPTOR DE VENTANAS Y NAVEGADORES (Webs, Búsquedas e IAs)
import re

FORBIDDEN_KEYWORDS = [
    "chatgpt", "claude", "gemini", "perplexity", "copilot", "openai", "character.ai",
    "tiktok", "instagram", "facebook", "twitter", "x.com", "youtube", "twitch", "netflix",
    "friv", "poki", "miniclip", "kongregate", "crazygames", "coolmathgames", 
    "minijuegos", "y8", "newgrounds", "juegos.com", "unblocked", "juegos friv",
    "roblox", "krunker", "slither.io", "agar.io",
    "gameplay", "descargar juego", "emulador", "roms", "torrent", "elamigosgamez", "el amigos", "elamigos"
]

# 4. EL ESCÁNER DE "ADN" (Firmas de Motores y Cracks)
GAME_SIGNATURE_FILES = [
    "unityplayer.dll",  # Motor gráfico Unity (Usado en Cuphead, Hollow Knight, etc.)
    "steam_api64.dll",  # Archivos de conexión a Steam
    "steam_api.dll",
    "steam_emu.ini",    # Firma inconfundible de juegos piratas/repacks
    "fmod_studio.dll",  # Motor de audio usado en el 90% de los juegos
    "fmodex.dll",
    "unrealengine"      # Motor gráfico Unreal
]

def kill_forbidden_processes():
    """Busca y destruye aplicaciones por nombre, carpeta o escaneo de ADN."""
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            name = proc.info['name'].lower()
            exe_path = proc.info['exe'].lower() if proc.info['exe'] else ""

            # Ataque 1: Si el nombre del proceso está en la lista negra
            if name in FORBIDDEN_PROCESSES:
                proc.kill()
                continue

            if exe_path:
                # Filtro de seguridad: Evita cerrar procesos del sistema de Windows 11 por accidente
                if "windows" in exe_path or "system32" in exe_path or "appdata\\local\\microsoft" in exe_path:
                    continue

                # Ataque 2: Si el programa se ejecuta desde una carpeta de juegos
                if any(path in exe_path for path in FORBIDDEN_PATHS):
                    proc.kill()
                    continue

                # Ataque 3: Escáner Forense de ADN (Detecta juegos piratas no registrados)
                folder_path = os.path.dirname(exe_path)
                try:
                    # Leemos los archivos que acompañan al programa (.exe)
                    files_in_folder = [f.lower() for f in os.listdir(folder_path)]
                    
                    # Si detectamos un motor gráfico o un crack de Steam, lo aniquilamos
                    for signature in GAME_SIGNATURE_FILES:
                        if any(signature in f for f in files_in_folder):
                            proc.kill()
                            break 
                except (PermissionError, FileNotFoundError):
                    pass

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def kill_forbidden_tabs():
    """Vigila la ventana activa y cierra SOLO la pestaña si contiene términos prohibidos."""
    try:
        active_window = gw.getActiveWindow()
        if active_window is not None and active_window.title:
            title = active_window.title.lower()
            
            # Buscamos coincidencias de palabras completas para evitar falsos positivos
            for keyword in FORBIDDEN_KEYWORDS:
                if re.search(r'\b' + re.escape(keyword) + r'\b', title):
                    # Inyecta Ctrl+W para cerrar quirúrgicamente la pestaña
                    pyautogui.hotkey('ctrl', 'w')
                    time.sleep(0.5) # Pausa para evitar cierres múltiples accidentales
                    break
    except Exception:
        pass

def main():
    if len(sys.argv) < 2:
        return

    try:
        end_time = float(sys.argv[1])
    except ValueError:
        return

    # Bucle de vigilancia extrema
    while time.time() < end_time:
        kill_forbidden_processes()
        kill_forbidden_tabs()
        time.sleep(1) # Rápido y constante

if __name__ == "__main__":
    main()