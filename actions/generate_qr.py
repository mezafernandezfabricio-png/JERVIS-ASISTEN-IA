# -*- coding: utf-8 -*-
"""
generate_qr.py — Generador infalible de códigos QR en alta resolución para JARVIS.
Guarda SIEMPRE en el Escritorio del usuario con apertura automática del archivo de imagen.
"""

import os
import sys
import re
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

def _get_desktop_dir() -> Path:
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
        if onedrive_desktop.exists():
            return onedrive_desktop
        desktop.mkdir(parents=True, exist_ok=True)
    return desktop

def _sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned if cleaned else f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def generate_qr(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Genera un código QR en alta calidad a partir de un texto, enlace o contacto y lo guarda en el Escritorio.
    Parámetros:
        - text / data / url / content: Texto o enlace a codificar
        - filename / nombre_archivo: Nombre del archivo de imagen (opcional)
        - open_file / abrir: Si debe abrir la imagen tras generarla (default True)
    """
    params = parameters or {}
    text = params.get("text") or params.get("data") or params.get("url") or params.get("content") or params.get("link") or ""
    filename = params.get("filename") or params.get("nombre_archivo") or params.get("title") or "codigo_qr"
    open_file = params.get("open_file", params.get("abrir", True))

    if not text:
        return "Debe proporcionar el texto, URL o información para generar el código QR."

    clean_name = _sanitize_filename(filename)
    if not clean_name.lower().endswith(".png"):
        clean_name = f"{clean_name}.png"

    desktop = _get_desktop_dir()
    file_path = desktop / clean_name

    saved = False

    # 1. Intentar con librería local qrcode
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=12,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(str(file_path))
        saved = True
    except Exception:
        pass

    # 2. Respaldo por API de generación rápida en línea
    if not saved:
        try:
            encoded_text = urllib.parse.quote(str(text))
            qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={encoded_text}"
            req = urllib.request.Request(qr_api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response, open(file_path, 'wb') as out_f:
                out_f.write(response.read())
            saved = True
        except Exception:
            pass

    if not saved:
        return "No se pudo generar el código QR en este momento. Verifique la conexión a internet."

    if player:
        try: player.write_log(f"📱 Código QR generado: {file_path.name}")
        except: pass

    if open_file and file_path.exists():
        try: os.startfile(str(file_path))
        except: pass

    return f"Código QR generado con éxito en tu Escritorio: '{file_path.name}' (Ruta: {file_path})"

def generate_qr_code(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return generate_qr(parameters, player, speak, **kwargs)

def generate_qr_tool(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return generate_qr(parameters, player, speak, **kwargs)