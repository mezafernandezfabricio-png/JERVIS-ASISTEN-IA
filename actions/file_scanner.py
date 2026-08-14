# -*- coding: utf-8 -*-

import os
from pathlib import Path
import time

def file_scanner(parameters: dict, player=None) -> str:
    """
    Escanea las carpetas principales del usuario buscando los archivos más recientes 
    de un tipo específico para leérselos.
    """
    file_type = parameters.get("file_type", "all").lower()
    
    if player:
        player.write_log(f"📡 Escaneando archivos recientes de tipo: {file_type}...")
        
    # Diccionario de extensiones por categoría
    extensions = {
        "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
        "document": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx"],
        "archive": [".rar", ".zip", ".7z", ".tar", ".gz"],
        "audio": [".mp3", ".wav", ".ogg", ".flac"]
    }
    
    valid_exts = extensions.get(file_type, [])
    
    home = Path.home()
    search_dirs = [
        home / "Downloads",
        home / "Desktop",
        home / "Documents",
        home / "Pictures",
        home / "Videos",
        home / "OneDrive" / "Escritorio",
        home / "OneDrive" / "Documentos"
    ]
    
    found_files = []
    
    for directory in search_dirs:
        if not directory.exists(): continue
        try:
            for root, dirs, files in os.walk(directory):
                # Limitar a 2 niveles de profundidad para que el escaneo sea instantáneo
                if root.replace(str(directory), "").count(os.sep) > 2:
                    del dirs[:]
                    continue
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if file_type == "all" or ext in valid_exts:
                        path = os.path.join(root, f)
                        mtime = os.path.getmtime(path)
                        found_files.append((f, mtime))
        except Exception:
            pass
            
    # Ordenar los archivos del más nuevo al más antiguo
    found_files.sort(key=lambda x: x[1], reverse=True)
    
    # Tomar solo los 5 más recientes para no aburrir al usuario leyendo una lista gigante
    top_files = found_files[:5] 
    
    if not top_files:
        return f"No encontré ningún archivo reciente de tipo '{file_type}' en tus carpetas."
        
    # Preparar el reporte para que JARVIS lo lea
    result = f"He encontrado estos archivos recientes en tu PC:\n"
    for i, (name, _) in enumerate(top_files):
        # Quitamos la extensión al leer para que suene más humano (ej: "vacaciones" en vez de "vacaciones punto mp4")
        clean_name = os.path.splitext(name)[0]
        result += f"- {clean_name}\n"
        
    result += "\n[INSTRUCCIÓN PARA JARVIS: Lee estos nombres de archivos al usuario de forma conversacional y pregúntale cuál de ellos quiere enviar. ¡No inventes archivos, lee solo los de esta lista!]"
    
    return result