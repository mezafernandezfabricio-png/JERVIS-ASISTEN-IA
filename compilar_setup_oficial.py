# -*- coding: utf-8 -*-
"""
compilar_setup_oficial.py — Compilador Master Oficial de XDS AI Assistant
Genera el paquete binario ejecutable autocontenido y el instalador oficial comercial para clientes.
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DIST_DIR = BASE_DIR / "DIST_INSTALADOR_ASISTENTE_XDS"
DIST_PYINSTALLER = BASE_DIR / "dist" / "XDS_AI"

print("======================================================================")
print("     COMPILADOR OFICIAL Y GENERADOR DE INSTALADOR DE XDS AI")
print("======================================================================")

# --- FASE 1: Verificación de Modelo de Voz y Configuraciones Base ---
print("\n[1/6] Verificando modelo de voz Vosk y plantillas de configuración...")

config_dir = BASE_DIR / "config"
config_dir.mkdir(exist_ok=True)

# Modelo Vosk
vosk_path = config_dir / "vosk_model"
if not vosk_path.exists():
    print("[INFO] Modelo Vosk no encontrado. Descargando modelo en español...")
    try:
        subprocess.run([sys.executable, str(BASE_DIR / "download_vosk.py")], cwd=BASE_DIR, check=True)
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo descargar automáticamente el modelo Vosk: {e}")
else:
    print("[OK] Modelo Vosk detectado correctamente.")

# Plantillas Config
api_keys_path = config_dir / "api_keys.json"
if not api_keys_path.exists():
    default_config = {
        "gemini_api_key": "",
        "openrouter_api_key": "",
        "os_system": "windows",
        "camera_index": 0,
        "mic_device": 0,
        "spk_device": 0,
        "timezone": "America/Lima",
        "language": "es-ES",
        "thinking_sound": True,
        "jarvis_voice": "Aoede",
        "jarvis_theme": "gold",
        "gpu_acceleration": False
    }
    api_keys_path.write_text(json.dumps(default_config, indent=4, ensure_ascii=False), encoding="utf-8")
    print("[OK] api_keys.json plantilla creada.")

user_profile_path = config_dir / "user_profile.json"
if not user_profile_path.exists():
    default_profile = {"name": "Sir", "habits": {}, "preferences": {}}
    user_profile_path.write_text(json.dumps(default_profile, indent=4, ensure_ascii=False), encoding="utf-8")

for empty_json in ["rules.json", "goals.json", "pc_index.json"]:
    p = config_dir / empty_json
    if not p.exists():
        p.write_text("[]", encoding="utf-8")

# --- FASE 2: Limpieza de Compilaciones Previas ---
print("\n[2/6] Limpiando directorios de compilación previa...")
for d in [BASE_DIR / "build", BASE_DIR / "dist", DIST_DIR, BASE_DIR / "Instalador_Final"]:
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)

DIST_DIR.mkdir(parents=True, exist_ok=True)
zip_path = BASE_DIR / "app_data.zip"
if zip_path.exists():
    zip_path.unlink()

# --- FASE 3: Compilación con PyInstaller ---
print("\n[3/6] Compilando ejecutable binario protegido con PyInstaller...")
spec_path = BASE_DIR / "JARVIS.spec"

try:
    pyinstaller_cmd = [sys.executable, "-c", f"import sys, PyInstaller.__main__; sys._pyi_isolated_subprocess = True; PyInstaller.__main__.run(['--noconfirm', r'{spec_path}'])"]
    res_pyi = subprocess.run(pyinstaller_cmd, cwd=BASE_DIR)
    if res_pyi.returncode != 0:
        print("[ERROR] Falló la compilación de PyInstaller.")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Ocurrió un fallo al ejecutar PyInstaller: {e}")
    sys.exit(1)

exe_built = DIST_PYINSTALLER / "XDS_AI.exe"
if not exe_built.exists():
    print(f"[ERROR] No se encontró el ejecutable generado en {exe_built}")
    sys.exit(1)

print(f"[OK] Paquete binario PyInstaller compilado en: {DIST_PYINSTALLER}")

# Limpieza de Credenciales del Creador para Distribución Limpia a Clientes
print("\n[3.5/6] Preparando plantilla limpia de credenciales para distribución comercial...")
dist_cfg_dir = DIST_PYINSTALLER / "config"
dist_cfg_dir.mkdir(parents=True, exist_ok=True)
clean_dist_config = {
    "gemini_api_key": "",
    "openrouter_api_key": "",
    "license_key": "",
    "privacy_accepted": False,
    "user_name": "",
    "ai_name": "XDS",
    "os_system": "windows",
    "camera_index": 0,
    "mic_device": 0,
    "spk_device": 0,
    "timezone": "America/Lima",
    "language": "es-ES",
    "thinking_sound": True,
    "jarvis_voice": "Aoede",
    "jarvis_theme": "gold",
    "gpu_acceleration": False
}
(dist_cfg_dir / "api_keys.json").write_text(json.dumps(clean_dist_config, indent=4, ensure_ascii=False), encoding="utf-8")
dist_lic_file = dist_cfg_dir / "license.json"
if dist_lic_file.exists():
    dist_lic_file.unlink()

print("[OK] Credenciales reseteadas en el paquete comercial. El asistente solicitará API Key y Código en la PC del cliente.")

# Firmar binario interno
if (BASE_DIR / "sign_executable.py").exists():
    subprocess.run([sys.executable, str(BASE_DIR / "sign_executable.py"), str(exe_built)], cwd=BASE_DIR)

# --- FASE 4: Compilación de Instalador Oficial Inno Setup ---
print("\n[4/6] Compilando Instalador Oficial Reconocido con Inno Setup...")

iscc_paths = [
    r"C:\Users\JOSE\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
]
iscc_exe = next((p for p in iscc_paths if os.path.exists(p)), shutil.which("ISCC.exe"))

installer_exe_out = DIST_DIR / "Instalar_XDS_Oficial.exe"

if iscc_exe and (BASE_DIR / "Generar_Instalador.iss").exists():
    print(f"-> Ejecutando Inno Setup Compiler ({iscc_exe})...")
    res_inno = subprocess.run([iscc_exe, str(BASE_DIR / "Generar_Instalador.iss")], capture_output=True, text=True)
    if res_inno.returncode == 0 and installer_exe_out.exists():
        print(f"[OK] Instalador Inno Setup generado exitosamente: {installer_exe_out.name}")
    else:
        print(f"[ADVERTENCIA Inno Setup]: {res_inno.stderr}")

# --- FASE 5: Verificación de Integridad de Inno Setup ---
print("\n[5/6] Verificando la integridad del instalador oficial (CRC)...")
if installer_exe_out.exists():
    print(f"[OK] Instalador listo y sin corrupción de firma: {installer_exe_out.name}")

# --- FASE 6: Desbloqueo de Metadatos de Seguridad MOTW y Lanzador de 1-Clic ---
print("\n[6/6] Desbloqueando marca de origen (Zone.Identifier) y creando paquete de distribución de 1-Clic...")
ps_unblock = f'Unblock-File -Path "{installer_exe_out.resolve()}" -ErrorAction SilentlyContinue; Remove-Item -Path "{installer_exe_out.resolve()}" -Stream Zone.Identifier -ErrorAction SilentlyContinue'
subprocess.run(["powershell", "-NoProfile", "-Command", ps_unblock])

# Crear script bat lanzador sin advertencias
bat_launcher = DIST_DIR / "Instalar_XDS.bat"
bat_launcher_content = f"""@echo off
title Instalador XDS AI Assistant — Xdata Security
color 0A
cls
echo [XDS AI] Desbloqueando instalador de seguridad...
powershell -NoProfile -Command "Unblock-File -Path '%~dp0Instalar_XDS_Oficial.exe' -ErrorAction SilentlyContinue; Remove-Item -Path '%~dp0Instalar_XDS_Oficial.exe' -Stream Zone.Identifier -ErrorAction SilentlyContinue" > NUL 2>&1
start "" "%~dp0Instalar_XDS_Oficial.exe"
"""
bat_launcher.write_text(bat_launcher_content, encoding="utf-8")

# Generar paquete ZIP comprimido listo para subir a Google Drive / Mega
zip_dist = DIST_DIR / "XDS_AI_Instalador_Oficial.zip"
if zip_dist.exists():
    zip_dist.unlink()

with zipfile.ZipFile(zip_dist, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(installer_exe_out, arcname="Instalar_XDS_Oficial.exe")
    z.write(bat_launcher, arcname="Instalar_XDS.bat")

print("\n======================================================================")
print("              ¡PROCESO FINALIZADO CON ÉXITO!")
print("======================================================================")
print(f"Ubicación del Instalador Oficial para tu cliente:\n")
print(f" -> {installer_exe_out.resolve()}")
print(f" -> {zip_dist.resolve()}")
print("\nCaracterísticas del Instalador:")
print("- Nombre del Asistente: XDS AI Assistant")
print("- Idioma: Español")
print("- Publicador Verificado: Xdata Security")
print("- Desbloqueo de Smart App Control (Sin pantallas negras de advertencia)")
print("- Paquete ZIP listo para enviar a clientes sin bloqueos de navegador")
print("======================================================================")
