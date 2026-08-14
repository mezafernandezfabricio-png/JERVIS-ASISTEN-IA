# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from pathlib import Path

# =========================================================================
# CONFIGURACIÓN DEL UPDATER
# =========================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Si usas GitHub Releases, coloca aquí la URL directa de descarga de tu .exe
# Ejemplo: "https://github.com/Jose/JARVIS-IA/releases/latest/download/JARVIS.exe"
GITHUB_URL = "https://github.com/TU_USUARIO/TU_REPO/releases/latest/download/JARVIS.exe"


def system_updater(parameters: dict, player=None) -> str:
    """
    Sistema de Auto-Actualización y Auto-Recompilación (OTA & Local).
    Se apoya en scripts BATCH temporales para evadir el bloqueo de archivos de Windows.
    """
    action = parameters.get("action", "local").lower()
    
    # Detectar si estamos corriendo el .py directamente o el .exe compilado
    is_exe = getattr(sys, 'frozen', False)
    exe_name = os.path.basename(sys.executable) if is_exe else "JARVIS.exe"

    if action == "local":
        if player:
            player.write_log("⚙️ Iniciando auto-recompilación local del núcleo...")
            
        bat_path = BASE_DIR / "recompile_jarvis.bat"
        
        # Script BATCH que se ejecutará independientemente
        bat_content = f"""@echo off
title JARVIS Recompiler
echo [JARVIS] Iniciando proceso de mutacion de codigo...
echo [JARVIS] Esperando a que el nucleo principal se apague (3 segundos)...
timeout /t 3 /nobreak > NUL
taskkill /f /im "{exe_name}" > NUL 2>&1

echo [JARVIS] Recompilando el ejecutable con PyInstaller...
:: Llama a PyInstaller utilizando tu archivo .spec existente para mantener el ícono y configuración
python -m PyInstaller --noconfirm JARVIS.spec

if exist "dist\\{exe_name}" (
    echo [JARVIS] Recompilacion exitosa. Trasladando nuevo cerebro...
    move /y "dist\\{exe_name}" "{exe_name}"
    echo [JARVIS] Despertando sistema...
    start "" "{exe_name}"
) else (
    echo [JARVIS] ERROR CRITICO: Fallo al compilar. Revisa los logs.
    pause
)
:: El script se auto-elimina al terminar
del "%~f0"
"""
        bat_path.write_text(bat_content, encoding="utf-8")
        
        # Lanzar el proceso de forma totalmente independiente
        subprocess.Popen([str(bat_path)], shell=True, cwd=BASE_DIR)
        
        # Matar a JARVIS inmediatamente para que el .bat pueda sobrescribir el .exe
        sys.exit(0)


    elif action == "github":
        if player:
            player.write_log("🌐 Iniciando protocolo de actualización OTA desde la nube...")
            
        bat_path = BASE_DIR / "update_ota.bat"
        
        bat_content = f"""@echo off
title JARVIS OTA Updater
echo [JARVIS] Conectando con los servidores satelitales (GitHub)...
timeout /t 3 /nobreak > NUL
taskkill /f /im "{exe_name}" > NUL 2>&1

echo [JARVIS] Descargando nueva version...
curl -L -o JARVIS_new.exe "{GITHUB_URL}"

if exist JARVIS_new.exe (
    echo [JARVIS] Parche descargado. Instalando...
    move /y JARVIS_new.exe "{exe_name}"
    echo [JARVIS] Actualizacion completada. Reiniciando...
    start "" "{exe_name}"
) else (
    echo [JARVIS] ERROR: No se pudo descargar el archivo. Verifica tu conexion y la URL.
    pause
)
del "%~f0"
"""
        bat_path.write_text(bat_content, encoding="utf-8")
        
        subprocess.Popen([str(bat_path)], shell=True, cwd=BASE_DIR)
        sys.exit(0)

    else:
        return f"Protocolo de actualización '{action}' desconocido."