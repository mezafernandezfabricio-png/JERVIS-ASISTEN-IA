# -*- coding: utf-8 -*-
"""social_media.py — Gestor y publicador en redes sociales (Twitter, Instagram, LinkedIn)."""
import urllib.parse
import webbrowser

def social_media(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Prepara o publica contenido en redes sociales (Twitter/X, LinkedIn, Facebook, Instagram).
    """
    parameters = parameters or {}
    platform = (parameters.get("platform") or parameters.get("network") or "twitter").lower()
    content = parameters.get("content") or parameters.get("text") or parameters.get("message") or ""
    action = (parameters.get("action") or "post").lower()

    if player:
        player.write_log(f"🌐 Preparando publicación en {platform.capitalize()}...")

    if "twitter" in platform or "x" in platform:
        encoded = urllib.parse.quote(content)
        url = f"https://twitter.com/intent/tweet?text={encoded}"
        webbrowser.open(url)
        return f"Ventana de publicación en Twitter/X abierta con el texto preparado."

    elif "linkedin" in platform:
        url = f"https://www.linkedin.com/sharing/share-offsite/?url=https://github.com"
        webbrowser.open(url)
        return f"Acceso a publicación de LinkedIn desplegado."

    elif "instagram" in platform:
        try:
            from actions.universal_social import universal_social
            return universal_social({"app_name": "instagram", "message": content}, player=player)
        except Exception:
            webbrowser.open("https://www.instagram.com")
            return "Abriendo Instagram en el navegador."

    else:
        return f"Contenido para {platform.capitalize()} preparado: '{content[:100]}...'."
