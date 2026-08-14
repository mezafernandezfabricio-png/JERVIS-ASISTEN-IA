# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import shutil
import subprocess
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None


def _scan_winreg_uninstall(software_name: str) -> list[dict]:
    if sys.platform != "win32":
        return []

    import winreg
    targets = []
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    soft_lower = software_name.lower().strip()

    for hive, path in reg_paths:
        try:
            key = winreg.OpenKey(hive, path)
            num_subkeys = winreg.QueryInfoKey(key)[0]

            for i in range(num_subkeys):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)

                    try:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    except Exception:
                        continue

                    if not display_name or soft_lower not in display_name.lower():
                        continue

                    quiet_cmd = None
                    uninstall_cmd = None
                    install_loc = None

                    try:
                        quiet_cmd, _ = winreg.QueryValueEx(subkey, "QuietUninstallString")
                    except Exception:
                        pass

                    try:
                        uninstall_cmd, _ = winreg.QueryValueEx(subkey, "UninstallString")
                    except Exception:
                        pass

                    try:
                        install_loc, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                    except Exception:
                        pass

                    targets.append({
                        "name": display_name,
                        "quiet_cmd": quiet_cmd,
                        "uninstall_cmd": uninstall_cmd,
                        "install_loc": install_loc,
                        "subkey": subkey_name
                    })

                except Exception:
                    continue

        except Exception:
            continue

    return targets


def _execute_uninstall_string(cmd_str: str, display_name: str = "") -> bool:
    if not cmd_str:
        return False

    cmd_str = cmd_str.strip()
    cmd_lower = cmd_str.lower()

    if display_name:
        _kill_processes_matching(display_name)

    try:
        # 1. Google Chrome / Edge / Brave / Chromium setup.exe
        if "setup.exe" in cmd_lower and ("google" in cmd_lower or "chrome" in cmd_lower or "browser" in cmd_lower):
            force_cmd = f'{cmd_str} --force-uninstall --system-level'
            proc = subprocess.run(force_cmd, shell=True, capture_output=True, text=True, timeout=120)
            if proc.returncode in [0, 3010] or not os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
                return True

        # 2. MSIExec
        if "msiexec" in cmd_lower:
            clean_cmd = re.sub(r"/I", "/X", cmd_str, flags=re.IGNORECASE)
            if "/qn" not in clean_cmd.lower() and "/quiet" not in clean_cmd.lower():
                clean_cmd += " /qn /norestart"
            proc = subprocess.run(clean_cmd, shell=True, capture_output=True, text=True, timeout=120)
            return proc.returncode in [0, 1605, 3010]

        # 3. Intentar comando directo del Registro primero
        proc = subprocess.run(cmd_str, shell=True, capture_output=True, text=True, timeout=90)
        if proc.returncode in [0, 3010]:
            return True

        # 4. Intentar con modificadores silenciosos según instalador
        if "unins000" in cmd_lower:
            cmd_run = f'{cmd_str} /VERYSILENT /SUPPRESSMSGBOXES /NORESTART'
        elif "uninstall.exe" in cmd_lower:
            cmd_run = f'{cmd_str} /S'
        else:
            cmd_run = f'{cmd_str} /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /S /quiet'

        proc2 = subprocess.run(cmd_run, shell=True, capture_output=True, text=True, timeout=120)
        return proc2.returncode in [0, 3010]
    except Exception:
        return False


def _kill_processes_matching(name: str):
    if not psutil:
        return
    name_lower = name.lower().strip()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            p_name = (proc.info['name'] or "").lower()
            if name_lower in p_name and "python" not in p_name and "jervis" not in p_name:
                proc.kill()
        except Exception:
            pass


try:
    from actions.open_app import search_pc_index
except ImportError:
    search_pc_index = None


def _find_software_info(software_name: str) -> dict:
    """Busca el programa en el Registro y en los discos para dar su ubicación real."""
    soft_lower = software_name.lower().strip()
    reg_matches = _scan_winreg_uninstall(soft_lower)
    if reg_matches:
        best = reg_matches[0]
        return {
            "name": best.get("name", software_name),
            "location": best.get("install_loc") or "Registro de Windows (Programa Instalado)",
            "type": "program"
        }

    if search_pc_index:
        try:
            res = search_pc_index(soft_lower, limit=3)
            for r in res:
                p = r.get("path", "")
                if p and os.path.exists(p):
                    return {
                        "name": r.get("display_name", software_name),
                        "location": str(p),
                        "type": "portable/file"
                    }
        except Exception:
            pass

    return {
        "name": software_name,
        "location": "Sistema / Disco Principal",
        "type": "program"
    }


def _uninstall_via_windows_settings(software_name: str) -> bool:
    """Abre el panel nativo 'Aplicaciones > Aplicaciones instaladas' de Windows, busca el programa y ejecuta la desinstalación."""
    try:
        if sys.platform != "win32":
            return False

        import pyautogui
        import pygetwindow as gw

        # 1. Abrir la pantalla exacta de Aplicaciones Instaladas de Windows (ms-settings:installed-apps)
        subprocess.Popen("start ms-settings:installed-apps", shell=True)
        time.sleep(1.8)

        # 2. Buscar y enfocar la ventana de Configuración
        settings_win = None
        for win in gw.getAllWindows():
            if "configuración" in win.title.lower() or "settings" in win.title.lower() or "aplicaciones" in win.title.lower():
                settings_win = win
                break

        if settings_win:
            try:
                if settings_win.isMinimized:
                    settings_win.restore()
                settings_win.activate()
                time.sleep(0.3)
            except Exception:
                pass

        # 3. Filtrar el programa en el buscador de la ventana de Windows
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.2)
        pyautogui.write(software_name, interval=0.03)
        time.sleep(1.0)

        # 4. Interactuar con el menú de los 3 puntos (...) y confirmar la desinstalación
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.4)

        pyautogui.press('down')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.5)

        pyautogui.press('enter')
        time.sleep(0.5)
        pyautogui.press('space')
        return True
    except Exception as e:
        print(f"[SoftwareUninstaller] Error en desinstalador de Windows Settings: {e}")
        return False


def _launch_uninstaller_interactive_cmd(uninstall_cmd: str, display_name: str) -> bool:
    """Abre el ejecutable de desinstalación oficial del programa a través de CMD desplegándolo en pantalla."""
    try:
        if not uninstall_cmd:
            return False

        # Si el ejecutable no tiene comillas y contiene espacios, envolver el ejecutable en comillas
        clean_cmd = uninstall_cmd.strip()
        
        # Ejecutar por consola CMD abriendo el asistente de desinstalación en pantalla
        full_cmd = f'start "{display_name}" {clean_cmd}'
        subprocess.Popen(f'cmd.exe /c {full_cmd}', shell=True)
        return True
    except Exception as e:
        print(f"[SoftwareUninstaller] Error lanzando desinstalador vía CMD: {e}")
        return False


def software_uninstaller(parameters: dict, player=None, speak=None) -> str:
    accion = str(parameters.get("accion") or parameters.get("action") or "desinstalar").lower().strip()
    programas_param = parameters.get("programas") or parameters.get("software") or parameters.get("target") or []
    confirm_val = parameters.get("confirm") or parameters.get("confirmar")

    is_confirmed = False
    if confirm_val is True:
        is_confirmed = True
    elif confirm_val is not None:
        c_str = str(confirm_val).lower().strip()
        negative_words = ["false", "no", "cancela", "cancelar", "abortar", "none", "0"]
        if c_str and not any(neg == c_str for neg in negative_words):
            is_confirmed = True

    if isinstance(programas_param, str):
        programas = [programas_param]
    else:
        programas = list(programas_param)

    if not programas and accion in ["desinstalar", "uninstall"]:
        return "No especificaste qué programa o aplicación debo desinstalar."

    if accion in ["cancelar", "cancel"]:
        return "Operación de desinstalación cancelada."

    software_str = str(programas[0]).strip().strip('"').strip("'") if programas else ""
    if not software_str:
        return "Indica el nombre del programa a desinstalar."

    info = _find_software_info(software_str)
    prog_name = info["name"]
    prog_loc = info["location"]

    # SI NO SE HA CONFIRMADO TODAVÍA: Pedir confirmación con el nombre y ubicación exacta
    if not is_confirmed:
        msg = f"CONFIRMACION_REQUERIDA: He localizado el programa '{prog_name}' (Ubicación: '{prog_loc}'). ¿Estás seguro de que deseas desinstalarlo por completo? Por favor responde 'sí' para proceder o 'no' para cancelar."
        if player:
            player.write_log(f"❓ {msg}")
        return msg

    # SI SE CONFIRMÓ: Lanzar el desinstalador por CMD en pantalla
    if player:
        player.write_log(f"🗑️ Confirmado. Abriendo ejecutable de desinstalación por CMD para '{prog_name}'...")

    desinstalado = False
    resultados = []

    # 1. Abrir por CMD el ejecutable de desinstalación oficial del programa en pantalla
    reg_matches = _scan_winreg_uninstall(software_str)
    if reg_matches:
        for target in reg_matches:
            cmd_to_run = target.get("uninstall_cmd") or target.get("quiet_cmd")
            if cmd_to_run:
                if _launch_uninstaller_interactive_cmd(cmd_to_run, target.get("name")):
                    resultados.append(f"✅ Se abrió por CMD el ejecutable de desinstalación de '{target.get('name')}' en tu pantalla.")
                    desinstalado = True
                    break

    # 2. Desinstalación visual desde 'Aplicaciones > Aplicaciones instaladas' de Windows
    if not desinstalado:
        if _uninstall_via_windows_settings(software_str):
            resultados.append(f"✅ Se abrió el panel nativo de Aplicaciones Instaladas de Windows para desinstalar '{prog_name}'.")
            desinstalado = True

    # 2. Winget (Nativo de Windows 10/11)
    if not desinstalado:
        winget_queries = [software_str, f'"{software_str}"', prog_name]
        if "chrome" in software_str.lower():
            winget_queries.insert(0, "Google.Chrome")

        for q in winget_queries:
            try:
                cmd = ["winget", "uninstall", "--id" if "." in q else "--name", q, "--silent", "--accept-source-agreements"]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
                salida = proc.stdout.lower()
                if proc.returncode == 0 or "eliminado" in salida or "uninstalled" in salida:
                    resultados.append(f"✅ '{prog_name}' fue desinstalado correctamente vía Winget.")
                    desinstalado = True
                    break
            except Exception:
                pass

    # 3. Chocolatey Fallback
    if not desinstalado:
        try:
            proc_choco = subprocess.run(
                ["choco", "uninstall", software_str, "-y"],
                capture_output=True, text=True, timeout=45, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            if proc_choco.returncode == 0 and "successfully uninstalled" in proc_choco.stdout.lower():
                resultados.append(f"✅ '{prog_name}' desinstalado vía Chocolatey.")
                desinstalado = True
        except Exception:
            pass

    # 4. Erradicación limpia de carpetas de instalación de la app
    if len(software_str) >= 2:
        _kill_processes_matching(software_str)

        drives = ["C:\\", "D:\\", "E:\\", "F:\\"]
        rutas_posibles = []
        for d in drives:
            rutas_posibles.extend([
                os.path.join(d, "Program Files"),
                os.path.join(d, "Program Files (x86)"),
                os.path.join(d, "Games"),
                os.path.join(d, "Juegos")
            ])
        user_local = os.environ.get("LocalAppData")
        if user_local:
            rutas_posibles.append(os.path.join(user_local, "Programs"))
            rutas_posibles.append(user_local)
        user_roaming = os.environ.get("AppData")
        if user_roaming:
            rutas_posibles.append(user_roaming)

        for base_dir in rutas_posibles:
            if os.path.exists(base_dir):
                try:
                    with os.scandir(base_dir) as entries:
                        for entry in entries:
                            if entry.is_dir() and software_str.lower() in entry.name.lower():
                                target_dir = entry.path
                                if not any(protected in target_dir.lower() for protected in ["system32", "windows", "desktop", "documents"]):
                                    shutil.rmtree(target_dir, ignore_errors=True)
                                    resultados.append(f"🔥 '{prog_name}' fue borrado limpiamente desde su carpeta ({target_dir}).")
                                    desinstalado = True
                except Exception:
                    continue

    if not desinstalado:
        resultados.append(f"✅ Se completó la rutina de desinstalación para '{prog_name}'.")

    reporte = "\n".join(resultados)
    if player:
        player.write_log(f"📋 {reporte}")

    return f"DESINSTALACIÓN COMPLETADA:\n{reporte}"