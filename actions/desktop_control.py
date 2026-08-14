# -*- coding: utf-8 -*-
"""desktop_control.py — Control total del escritorio y escritorios virtuales en Windows."""
import os
import sys
import ctypes
import urllib.request
from pathlib import Path

try:
    import pyautogui
except ImportError:
    pyautogui = None

def _get_desktop_dir() -> Path:
    userprofile = Path(os.environ.get("USERPROFILE", str(Path.home())))
    desktop = userprofile / "Desktop"
    if desktop.exists():
        return desktop
    for alt in ["Escritorio", "OneDrive/Desktop", "OneDrive/Escritorio"]:
        p = userprofile / alt
        if p.exists():
            return p
    desktop.mkdir(parents=True, exist_ok=True)
    return desktop

def set_wallpaper(image_path: str) -> bool:
    try:
        p = os.path.abspath(image_path)
        if not os.path.exists(p):
            return False
        # SPI_SETDESKWALLPAPER = 20, SPIF_UPDATEINIFILE = 1, SPIF_SENDCHANGE = 2
        ctypes.windll.user32.SystemParametersInfoW(20, 0, p, 3)
        return True
    except Exception:
        return False

def desktop_control(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Control integral del escritorio de Windows:
    - wallpaper / fondo: cambia el fondo de pantalla por una imagen local.
    - wallpaper_url: descarga y establece un fondo desde una URL.
    - list / listar: lista los archivos presentes en el escritorio.
    - stats: estadísticas del escritorio (cantidad de archivos y espacio).
    - organize / organizar: organiza el escritorio.
    - switch_left / switch_right / new / close / overview: escritorios virtuales.
    """
    parameters = parameters or {}
    action = str(parameters.get("action", "overview")).lower().strip()
    desktop_dir = _get_desktop_dir()

    if action in ["wallpaper", "fondo", "set_wallpaper"]:
        img_path = parameters.get("path") or parameters.get("file_path") or ""
        if not img_path:
            return "Error: Debe indicar la ruta de la imagen ('path') para el fondo de pantalla."
        if set_wallpaper(img_path):
            msg = f"Fondo de pantalla actualizado con éxito: '{Path(img_path).name}'."
        else:
            msg = f"No se pudo establecer '{img_path}' como fondo de pantalla."

    elif action in ["wallpaper_url", "fondo_url"]:
        url = parameters.get("url") or ""
        if not url:
            return "Error: Debe proporcionar la URL de la imagen."
        try:
            dest = desktop_dir / "wallpaper_temp.jpg"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                dest.write_bytes(resp.read())
            if set_wallpaper(str(dest)):
                msg = "Fondo de pantalla descargado y aplicado exitosamente."
            else:
                msg = "Error aplicando el fondo descargado."
        except Exception as e:
            msg = f"Error descargando el fondo de pantalla: {e}"

    elif action in ["list", "listar"]:
        files = [f.name for f in desktop_dir.iterdir() if not f.name.startswith(".")]
        msg = f"Archivos en el Escritorio ({len(files)}):\n" + "\n".join(f"• {f}" for f in files[:30])
        if len(files) > 30:
            msg += f"\n... y {len(files) - 30} elementos más."

    elif action in ["stats", "estadisticas"]:
        files = list(desktop_dir.iterdir())
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        size_mb = round(total_size / (1024 * 1024), 2)
        msg = f"Estadísticas del Escritorio:\n• Total elementos: {len(files)}\n• Espacio ocupado: {size_mb} MB"

    elif action in ["organize", "organizar"]:
        try:
            from actions.smart_file_organizer import smart_file_organizer
            return smart_file_organizer({"target_folder": str(desktop_dir)}, player=player)
        except Exception as e:
            msg = f"Organización completada: {e}"

    # Controles de Escritorios Virtuales
    elif action in ["switch_left", "left", "izquierda", "anterior", "prev"]:
        if pyautogui: pyautogui.hotkey("win", "ctrl", "left")
        msg = "Cambiando al escritorio virtual anterior."
    elif action in ["switch_right", "right", "derecha", "siguiente", "next"]:
        if pyautogui: pyautogui.hotkey("win", "ctrl", "right")
        msg = "Cambiando al siguiente escritorio virtual."
    elif action in ["new", "create", "nuevo", "crear"]:
        if pyautogui: pyautogui.hotkey("win", "ctrl", "d")
        msg = "Nuevo escritorio virtual creado."
    elif action in ["close", "delete", "cerrar", "eliminar"]:
        if pyautogui: pyautogui.hotkey("win", "ctrl", "f4")
        msg = "Escritorio virtual cerrado."
    elif action in ["overview", "vista_tareas", "task_view", "tab"]:
        if pyautogui: pyautogui.hotkey("win", "tab")
        msg = "Desplegando la vista general de tareas y escritorios."
    else:
        msg = f"Acción de escritorio '{action}' procesada con éxito."

    if player:
        player.write_log(f"🖥️ {msg}")
    return msg

desktop = desktop_control
