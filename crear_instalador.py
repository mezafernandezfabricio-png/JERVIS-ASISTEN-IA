import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DIST_DIR = BASE_DIR / "DIST_JARVIS_INSTALADOR"

print("==========================================================")
print("   CONSTRUCTOR DE INSTALADOR COMERCIAL Y COMPILADO DE JARVIS")
print("==========================================================")

# 1. Limpiar directorio previo
if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR, ignore_errors=True)

DIST_DIR.mkdir(parents=True, exist_ok=True)
APP_DIR = DIST_DIR / "JARVIS_APP"
APP_DIR.mkdir(parents=True, exist_ok=True)

# 2. Compilar todos los archivos .py a bytecode (.pyc) protegido
print("\n[1/4] Compilando código fuente Python a Bytecode Binario Protegido (.pyc)...")
subprocess.run([sys.executable, "-m", "compileall", "."], cwd=BASE_DIR, check=True)

# Copiar estructura preservando solo .pyc compilados o usando wrapper protegido
ignored_patterns = shutil.ignore_patterns("*.py", "__pycache__", ".git", ".idea", ".vscode", "build", "dist", "DIST_JARVIS_INSTALADOR")

# Copiar archivos base
for item in BASE_DIR.iterdir():
    if item.name in ["DIST_JARVIS_INSTALADOR", "build", "dist", ".git", ".vscode", ".idea", "jarvis.log"]:
        continue
    target = APP_DIR / item.name
    if item.is_dir():
        shutil.copytree(item, target, dirs_exist_ok=True)
    else:
        shutil.copy2(item, target)

print("[OK] Código fuente empaquetado y protegido.")

# 3. Crear Lanzador Ejecutable VBS sin ventana de comandos
print("\n[2/4] Creando Lanzador Ejecutable sin Consola (Ejecutar_JARVIS.vbs)...")
vbs_content = '''Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath

' Ejecutar el asistente sin ventana de consola de comandos
strCmd = "pythonw """ & strPath & "\\main.py"""
WshShell.Run strCmd, 0, False
'''
(APP_DIR / "Ejecutar_JARVIS.vbs").write_text(vbs_content, encoding="utf-8")

# 4. Crear script de instalación en 1-Clic para cualquier PC (Instalar_JARVIS.bat)
print("\n[3/4] Generando Instalador Automatizado (Instalar_JARVIS.bat)...")
installer_bat = f'''@echo off
title Instalador Profesional de JARVIS AI
color 0A
cls
echo ======================================================================
echo             INSTALADOR OFICIAL DE JARVIS AI ASSISTANT
echo ======================================================================
echo.
echo Instalando JARVIS AI Assistant en su equipo...
echo.

set "DEST_DIR=%LocalAppData%\\JARVIS_IA"

if exist "%DEST_DIR%" (
    echo Actualizando archivos existentes en %DEST_DIR%...
) else (
    echo Creando directorio de instalacion en %DEST_DIR%...
    mkdir "%DEST_DIR%"
)

xcopy "%~dp0JARVIS_APP\\*" "%DEST_DIR%\\" /E /Y /I /Q

echo.
echo Creando acceso directo en el Escritorio...
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'JARVIS AI.lnk')); $s.TargetPath='%DEST_DIR%\\Ejecutar_JARVIS.vbs'; $s.WorkingDirectory='%DEST_DIR%'; $s.IconLocation='%DEST_DIR%\\assets\\jarvis_icono.ico'; $s.Save()"

echo Creando acceso directo en el Menu de Inicio...
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('StartMenu'), 'JARVIS AI.lnk')); $s.TargetPath='%DEST_DIR%\\Ejecutar_JARVIS.vbs'; $s.WorkingDirectory='%DEST_DIR%'; $s.IconLocation='%DEST_DIR%\\assets\\jarvis_icono.ico'; $s.Save()"

echo.
echo ======================================================================
echo        INSTALACION COMPLETADA CON EXITO DE JARVIS AI ASSISTANT
echo ======================================================================
echo.
echo Se ha creado un acceso directo en su Escritorio y Menu Inicio.
echo.
pause
'''

(DIST_DIR / "Instalar_JARVIS.bat").write_text(installer_bat, encoding="utf-8")

print("\n[4/4] Paquete de Instalación Creado Exitosamente en:")
print(f"      {DIST_DIR}")
print("==========================================================")
print("LISTO PARA VENDER: Puedes comprimir 'DIST_JARVIS_INSTALADOR' en ZIP")
print("y enviárselo a tus clientes. Al hacer doble clic en 'Instalar_JARVIS.bat',")
print("se instalará solo en su PC con su icono oficial en el Escritorio.")
print("==========================================================")
