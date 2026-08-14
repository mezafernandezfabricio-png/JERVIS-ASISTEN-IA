"""youtube_video.py — Búsqueda y control de reproducción en YouTube."""
import webbrowser
import urllib.parse
import urllib.request
import re

try:
    import pyautogui
except ImportError:
    pass

def youtube_video(parameters: dict, response=None, player=None) -> str:
    """Busca, reproduce y controla videos de YouTube mediante web y teclas multimedia."""
    action = str(parameters.get("action", "play")).lower().strip()
    
    # Convertimos a minúsculas inmediatamente para detectar la alucinación fácil
    query = str(parameters.get("query", "")).lower().strip()
    
    # Obtenemos los segundos si pide iniciar en un minuto específico
    try:
        time_sec = int(parameters.get("time", 0))
    except (ValueError, TypeError):
        time_sec = 0

    # ========================================================
    # APERTURA DIRECTA DE LA PÁGINA PRINCIPAL DE YOUTUBE
    # ========================================================
    # Si la acción es abrir/inicio, o si el query está vacío o es genérico ("telepatia", "youtube", "inicio"):
    bad_queries = ["telepatia", "telepatía", "youtube", "home", "inicio", "pagina principal", "página principal"]
    is_open_action = action in ["open", "abrir", "go_to", "home", "inicio", "browse", "launch"]
    is_generic_query = not query or any(bq in query for bq in bad_queries)

    if is_open_action or is_generic_query:
        webbrowser.open("https://www.youtube.com")
        msg = "Abriendo la página principal de YouTube."
        if player: 
            player.write_log(f"🌐 {msg}")
        return msg
    # ========================================================

    try:
        # === CONTROLES MULTIMEDIA GLOBALES DE WINDOWS ===
        # Estas teclas nativas controlan el navegador en segundo plano
        
        if action in ["pause", "pausa", "resume", "reanudar", "playpause"]:
            pyautogui.press("playpause")
            msg = "Reproducción pausada o reanudada."
            if player: player.write_log(f"⏯️ {msg}")
            return msg

        if action in ["next", "siguiente", "pasar"]:
            pyautogui.press("nexttrack")
            msg = "Pasando a la siguiente canción."
            if player: player.write_log(f"⏭️ {msg}")
            return msg

        if action in ["stop", "detener", "parar", "quitar"]:
            pyautogui.press("stop")
            pyautogui.press("playpause") # Por si el navegador ignora la tecla stop
            msg = "Reproducción detenida."
            if player: player.write_log(f"⏹️ {msg}")
            return msg

        if action in ["restart", "reiniciar", "cero", "inicio", "repetir"]:
            pyautogui.press("prevtrack")
            msg = "Reiniciando la canción desde el principio."
            if player: player.write_log(f"⏮️ {msg}")
            return msg

        # === BÚSQUEDA Y REPRODUCCIÓN DIRECTA ===
        if action == "play" or query != "":
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            if player:
                player.write_log(f"🔍 Buscando '{query}'...")
                
            # Extraemos el código fuente de los resultados de YouTube
            html = urllib.request.urlopen(search_url)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            
            if video_ids:
                # Armamos la URL directa al video
                video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                
                # Si especificaste un tiempo de inicio exacto (ej. minuto 2)
                if time_sec > 0:
                    video_url += f"&t={time_sec}s"
                    
                webbrowser.open(video_url)
                msg = f"Reproduciendo '{query}' en YouTube."
                if player:
                    player.write_log(f"📺 {msg}")
                return msg
            else:
                webbrowser.open(search_url)
                msg = f"Abriendo resultados de búsqueda para '{query}'."
                if player:
                    player.write_log(f"📺 {msg}")
                return msg

    except Exception as e:
        return f"Ocurrió un error al intentar controlar YouTube: {e}"
        
    return "Acción de YouTube no reconocida."