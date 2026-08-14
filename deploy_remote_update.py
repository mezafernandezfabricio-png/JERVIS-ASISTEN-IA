# -*- coding: utf-8 -*-
"""
deploy_remote_update.py — Puente de Actualizaciones Automáticas Remotas de XDS AI Assistant
Compila el nuevo ejecutable, incrementa la versión, genera el manifiesto remoto y publica la actualización.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.resolve()
VERSION_FILE = BASE_DIR / "config" / "version.json"
DIST_RELEASE_CLOUD = BASE_DIR / "DIST_RELEASE_CLOUD"
DIST_INSTALLER_DIR = BASE_DIR / "DIST_INSTALADOR_ASISTENTE_XDS"

def increment_version(v_str: str) -> str:
    parts = v_str.strip().split(".")
    if len(parts) == 3:
        try:
            return f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
        except ValueError:
            pass
    return "1.0.1"

def deploy_update(changelog_text: str = None):
    print("======================================================================")
    print(" [PUENTE DE ACTUALIZACION AUTOMATICA REMOTA - XDS AI ASSISTANT]")
    print("======================================================================")

    # 1. Leer versión actual e incrementar
    local_info = {}
    if VERSION_FILE.exists():
        try:
            local_info = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    current_ver = local_info.get("version", "1.0.0")
    new_ver = increment_version(current_ver)

    if not changelog_text:
        changelog_text = f"• Actualización y optimización del núcleo XDS AI (v{new_ver}).\n• Parches de rendimiento y estabilidad."

    print(f"\n[1/5] Incrementando versión: v{current_ver} ➔ v{new_ver}")
    
    local_info["version"] = new_ver
    local_info["changelog"] = changelog_text
    local_info["release_date"] = subprocess.check_output("powershell Get-Date -Format 'yyyy-MM-dd'", shell=True, text=True).strip()
    VERSION_FILE.write_text(json.dumps(local_info, indent=4, ensure_ascii=False), encoding="utf-8")

    # 2. Compilar ejecutable maestro con PyInstaller
    print("\n[2/5] Compilando ejecutable XDS_AI.exe con PyInstaller...")
    spec_path = BASE_DIR / "JARVIS.spec"
    pyi_cmd = [sys.executable, "-c", f"import sys, PyInstaller.__main__; sys._pyi_isolated_subprocess = True; PyInstaller.__main__.run(['--noconfirm', r'{spec_path}'])"]
    subprocess.run(pyi_cmd, cwd=BASE_DIR, check=True)

    dist_exe = BASE_DIR / "dist" / "XDS_AI" / "XDS_AI.exe"
    if not dist_exe.exists():
        print(f"[ERROR] No se encontró el ejecutable en {dist_exe}")
        sys.exit(1)

    # Firmar binario interno
    if (BASE_DIR / "sign_executable.py").exists():
        print("Firmando digitalmente ejecutable interno...")
        subprocess.run([sys.executable, str(BASE_DIR / "sign_executable.py"), str(dist_exe)], cwd=BASE_DIR)

    # 3. Preparar directorio de distribución en la nube (DIST_RELEASE_CLOUD)
    print("\n[3/5] Preparando paquete de actualización para distribución en la nube...")
    DIST_RELEASE_CLOUD.mkdir(parents=True, exist_ok=True)

    # Crear zip de parche de actualización
    zip_release = DIST_RELEASE_CLOUD / "update_patch.zip"
    if zip_release.exists():
        zip_release.unlink()

    shutil.copy2(dist_exe, DIST_RELEASE_CLOUD / "XDS_AI.exe")

    # Manifiesto remoto de actualización
    manifest_remote = {
        "app_name": "XDS AI Assistant",
        "version": new_ver,
        "release_date": local_info["release_date"],
        "update_url": local_info.get("update_url", "https://raw.githubusercontent.com/mezafernandezfabricio-png/JERVIS-ASISTEN-IA/main/DIST_RELEASE_CLOUD/version.json"),
        "exe_url": "https://raw.githubusercontent.com/mezafernandezfabricio-png/JERVIS-ASISTEN-IA/main/DIST_RELEASE_CLOUD/XDS_AI.exe",
        "changelog": changelog_text
    }
    (DIST_RELEASE_CLOUD / "version.json").write_text(json.dumps(manifest_remote, indent=4, ensure_ascii=False), encoding="utf-8")

    # 4. Re-compilar instalador oficial Inno Setup
    print("\n[4/5] Generando nuevo Instalador Oficial en Español (Instalar_XDS_Oficial.exe)...")
    iscc_exe = r"C:\Users\JOSE\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
    if os.path.exists(iscc_exe) and (BASE_DIR / "Generar_Instalador.iss").exists():
        subprocess.run([iscc_exe, str(BASE_DIR / "Generar_Instalador.iss")], capture_output=True, text=True)

    # 5. Publicación Git / Servidor (si está configurado)
    print("\n[5/5] Sincronizando parche con el canal de distribución remota...")
    if (BASE_DIR / ".git").exists():
        try:
            subprocess.run(["git", "add", "."], cwd=BASE_DIR)
            subprocess.run(["git", "commit", "-m", f"Release v{new_ver}: {changelog_text[:50]}"], cwd=BASE_DIR)
            subprocess.run(["git", "push"], cwd=BASE_DIR)
            print("[OK] Cambios subidos a GitHub automáticamente.")
        except Exception as ex:
            print(f"[INFO] Git push omitido: {ex}")

    print("\n======================================================================")
    print(f" [OK] ACTUALIZACION v{new_ver} PUBLICADA CON EXITO!")
    print("======================================================================")
    print(f"Todas las computadoras donde este instalado XDS AI recibiran")
    print(f"la version {new_ver} de forma automatica con las siguientes novedades:\n")
    print(f"Notas: {changelog_text}")
    print("======================================================================")

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    deploy_update(msg)
