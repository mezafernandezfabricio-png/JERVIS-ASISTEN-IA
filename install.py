# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import time
import subprocess
from pathlib import Path


def print_banner():
    cyan = "\033[36m"
    green = "\033[32m"
    reset = "\033[0m"

    os.system("")

    print(f"{cyan}======================================================================={reset}")
    print(f"{cyan}      __  ___   ____   _    __  ____   _____                           {reset}")
    print(f"{cyan}     / / /   | / __ \\ / /  / / / __ \\ / ___/                           {reset}")
    print(f"{cyan} __  / / / /| |/ /_/ // /  / / / /_/ / \\__ \\                            {reset}")
    print(f"{cyan}/ /_/ / / ___ // _, _// /__/ /  / _, _/ ___/ /                            {reset}")
    print(f"{cyan}\\____/ /_/  |_|/_/ |_|/____/_/  /_/ |_|/____/                             {reset}")
    print()
    print(f"{green}                  SISTEMA DE INSTALACIÓN INTELIGENTE                   {reset}")
    print(f"{cyan}======================================================================={reset}")
    print()


def run_cmd(cmd, check=True):
    return subprocess.run(cmd, check=check)


def run_shell(cmd, check=True):
    return subprocess.run(cmd, shell=True, check=check)


def main():
    print_banner()
    print("Este asistente preparará JARVIS para funcionar correctamente.")
    print()
    print(" [1] Comenzar instalación limpia")
    print(" [2] Salir")
    print()

    try:
        opt = input("Selecciona una opción (1-2): ").strip()
    except Exception:
        opt = "2"

    if opt != "1":
        print("Saliendo del instalador...")
        time.sleep(1)
        sys.exit(0)

    os.system("cls")
    print_banner()
    print("[FASE 1/6] Verificando sistema...")
    print(f"[OK] Python detectado: {sys.version.split()[0]}")

    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
            except Exception:
                pass

    for f in os.listdir("."):
        if f in ["jarvis.log", "JARVIS_Beta_Installer.exe"]:
            try:
                os.remove(f)
            except Exception:
                pass

    print("[OK] Limpieza inicial completada.")
    time.sleep(1)

    os.system("cls")
    print_banner()
    print("[FASE 2/6] Configurando entorno virtual...")

    if not os.path.exists(".venv"):
        try:
            run_cmd([sys.executable, "-m", "venv", ".venv"])
            print("[OK] Entorno virtual creado.")
        except Exception as e:
            print(f"[ERROR] No se pudo crear .venv: {e}")
            input("Presiona Enter para salir...")
            sys.exit(1)
    else:
        print("[OK] Entorno virtual existente detectado.")

    venv_python = os.path.join(".venv", "Scripts", "python.exe")

    if not os.path.exists(venv_python):
        venv_python = sys.executable

    time.sleep(1)

    os.system("cls")
    print_banner()
    print("[FASE 3/6] Instalando dependencias...")
    print("Esto puede tardar varios minutos.")
    print()

    try:
        run_cmd([venv_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

        if not os.path.exists("requirements.txt"):
            print("[ERROR] No encontré requirements.txt en la raíz del proyecto.")
            input("Presiona Enter para salir...")
            sys.exit(1)

        run_cmd([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])

        print("[OK] Dependencias principales instaladas.")

    except Exception as e:
        print(f"[ERROR] Falló la instalación de requirements.txt: {e}")
        input("Presiona Enter para salir...")
        sys.exit(1)

    print()
    print("[INFO] Instalando soporte Playwright...")
    try:
        run_cmd([venv_python, "-m", "playwright", "install"], check=False)
        print("[OK] Playwright instalado o verificado.")
    except Exception:
        print("[ADVERTENCIA] No se pudo completar playwright install.")

    print()
    print("[INFO] Verificando PyAudio...")
    try:
        run_cmd([venv_python, "-m", "pip", "install", "pyaudio"], check=True)
        print("[OK] PyAudio instalado.")
    except Exception:
        print("[ADVERTENCIA] No se pudo instalar PyAudio automáticamente.")
        print("Si el wake listener falla, prueba manualmente:")
        print("python -m pip install pipwin")
        print("pipwin install pyaudio")

    print()
    print("[INFO] Verificando pywin32...")
    try:
        run_cmd([venv_python, "-m", "pip", "install", "pywin32"], check=False)
        run_cmd([venv_python, "-m", "pywin32_postinstall", "-install"], check=False)
        print("[OK] pywin32 verificado.")
    except Exception:
        print("[ADVERTENCIA] pywin32 no pudo configurarse automáticamente.")

    print()
    print("[INFO] Verificando soporte de extracción RAR/7z...")
    try:
        run_cmd([venv_python, "-m", "pip", "install", "pyunpack", "patool"], check=False)
        print("[OK] pyunpack y patool verificados.")
    except Exception:
        print("[ADVERTENCIA] No se pudo instalar pyunpack/patool.")

    time.sleep(1)

    os.system("cls")
    print_banner()
    print("[FASE 4/6] Configuración inicial...")

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    api_keys_path = config_dir / "api_keys.json"
    api_keys_template = config_dir / "api_keys.example.json"
    rules_path = config_dir / "rules.json"
    pc_index_path = config_dir / "pc_index.json"
    goals_path = config_dir / "goals.json"
    user_profile_path = config_dir / "user_profile.json"

    if not api_keys_template.exists():
        default_template = {
            "gemini_api_key": "PON_AQUI_TU_API_KEY",
            "openrouter_api_key": "PON_AQUI_TU_API_KEY",
            "os_system": "windows",
            "camera_index": 0,
            "mic_device": 0,
            "spk_device": 0,
            "chrome_google_profile": "Default",
            "chrome_exe_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "timezone": "America/Lima",
            "language": "es-ES",
            "thinking_sound": True,
            "jarvis_voice": "Aoede",
            "spotify_client_id": "",
            "spotify_client_secret": "",
            "spotify_redirect_uri": "http://127.0.0.1:8888/callback",
            "tmdb_api_key": "",
            "jarvis_theme": "gold",
            "gpu_acceleration": False
        }

        api_keys_template.write_text(
            json.dumps(default_template, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
        print("[OK] api_keys.example.json creado.")

    if not api_keys_path.exists():
        shutil.copy2(api_keys_template, api_keys_path)
        print("[OK] api_keys.json creado desde plantilla.")
    else:
        print("[OK] api_keys.json existente detectado.")

    if not rules_path.exists():
        rules_path.write_text("[]", encoding="utf-8")
        print("[OK] rules.json creado como lista vacía.")
    else:
        print("[OK] rules.json existente detectado.")

    if not pc_index_path.exists():
        pc_index_path.write_text("[]", encoding="utf-8")
        print("[OK] pc_index.json creado.")

    if not goals_path.exists():
        goals_path.write_text("[]", encoding="utf-8")
        print("[OK] goals.json creado.")

    if not user_profile_path.exists():
        default_profile = {
            "name": "Sir",
            "habits": {},
            "preferences": {}
        }
        user_profile_path.write_text(
            json.dumps(default_profile, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
        print("[OK] user_profile.json creado.")

    time.sleep(1)

    os.system("cls")
    print_banner()
    print("[FASE 5/6] Verificando programas externos recomendados...")

    external_notes = []

    if shutil.which("7z") is None and not Path("C:\\Program Files\\7-Zip\\7z.exe").exists():
        external_notes.append("7-Zip recomendado para extraer RAR y 7z.")

    if shutil.which("ollama") is None:
        external_notes.append("Ollama opcional para modo offline.")

    if external_notes:
        print("[ADVERTENCIAS]")
        for note in external_notes:
            print("-", note)
    else:
        print("[OK] Programas externos básicos detectados.")

    time.sleep(1)

    os.system("cls")
    print_banner()
    print("[FASE 6/6] Creando acceso directo...")

    try:
        current_dir = os.getcwd()
        icon_path = os.path.join(current_dir, "assets", "jarvis_icono.ico")
        target_vbs = os.path.join(current_dir, "Iniciar JARVIS.vbs")

        if not os.path.exists(target_vbs):
            vbs_content = f'''
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{current_dir}"
WshShell.Run ".venv\\Scripts\\pythonw.exe main.py", 0, False
'''
            with open(target_vbs, "w", encoding="utf-8") as f:
                f.write(vbs_content.strip())

            print("[OK] Iniciar JARVIS.vbs creado.")

        ps_cmd = (
            "$s=(New-Object -ComObject WScript.Shell).CreateShortcut("
            "([System.Environment]::GetFolderPath('Desktop')+'\\JARVIS AI.lnk'));"
            f"$s.TargetPath='{target_vbs}';"
            f"$s.WorkingDirectory='{current_dir}';"
            f"$s.IconLocation='{icon_path}';"
            "$s.Description='Lanzador de JARVIS AI';"
            "$s.Save()"
        )

        run_cmd(["powershell", "-NoProfile", "-Command", ps_cmd], check=False)

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        lnk_path = os.path.join(desktop, "JARVIS AI.lnk")

        if os.path.exists(lnk_path):
            try:
                with open(lnk_path, "rb") as f:
                    data = bytearray(f.read())

                data[21] = data[21] | 0x20

                with open(lnk_path, "wb") as f:
                    f.write(data)

                print("[OK] Acceso directo creado con permisos de administrador.")
            except Exception:
                print("[OK] Acceso directo creado.")
        else:
            print("[ADVERTENCIA] No pude confirmar el acceso directo.")

    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo crear acceso directo: {e}")

    os.system("cls")
    print_banner()
    print("=======================================================================")
    print("     INSTALACIÓN COMPLETADA")
    print("=======================================================================")
    print()
    print("JARVIS está casi listo.")
    print("Revisa config/api_keys.json y coloca tus API Keys.")
    print()
    print("Para funciones avanzadas recuerda:")
    print("- Ejecutar como administrador para WiFi, Bluetooth y energía.")
    print("- Instalar 7-Zip para RAR y 7z.")
    print("- Activar permisos de cámara y micrófono en Windows.")
    print()
    print(" [1] Iniciar JARVIS ahora")
    print(" [2] Salir")
    print()

    try:
        launch_opt = input("Selecciona una opción (1-2): ").strip()
    except Exception:
        launch_opt = "2"

    if launch_opt == "1":
        try:
            os.startfile("Iniciar JARVIS.vbs")
        except Exception:
            subprocess.Popen(["wscript.exe", "Iniciar JARVIS.vbs"])

    print("Gracias por usar JARVIS.")
    time.sleep(2)


if __name__ == "__main__":
    main()