# -*- coding: utf-8 -*-

import time
import subprocess


def _run_powershell(command: str, timeout: int = 10):
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True,
        timeout=timeout
    )


def _run_cmd(command: str, timeout: int = 10):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def _find_window(window_name: str = ""):
    try:
        import pygetwindow as gw
    except ImportError:
        return None, "Falta pygetwindow. Instala con: pip install pygetwindow"

    windows = [w for w in gw.getAllWindows() if w.title and w.title.strip()]

    if not windows:
        return None, "No encontré ventanas abiertas."

    if window_name:
        q = window_name.lower().strip()
        for w in windows:
            if q in w.title.lower():
                return w, None

    try:
        active = gw.getActiveWindow()
        if active:
            return active, None
    except Exception:
        pass

    return windows[0], None


def _set_volume(target: int):
    from ctypes import cast, POINTER
    from comtypes import CoInitialize, CoUninitialize
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    target = max(0, min(100, int(target)))

    CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
    volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
    volume_ctrl.SetMasterVolumeLevelScalar(target / 100.0, None)
    CoUninitialize()

    return target


def _get_volume() -> int:
    from ctypes import cast, POINTER
    from comtypes import CoInitialize, CoUninitialize
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
    volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
    current = int(round(volume_ctrl.GetMasterVolumeLevelScalar() * 100))
    CoUninitialize()

    return current


def _set_brightness(target: int) -> bool:
    target = max(0, min(100, int(target)))

    commands = [
        f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{target})',
        f'Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods | Invoke-CimMethod -MethodName WmiSetBrightness -Arguments @{{Timeout=1; Brightness={target}}}'
    ]

    for cmd in commands:
        try:
            _run_powershell(cmd, timeout=5)
            return True
        except Exception:
            continue

    return False


def _get_brightness() -> int:
    commands = [
        '(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness',
        '(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness).CurrentBrightness'
    ]

    for cmd in commands:
        try:
            result = _run_powershell(cmd, timeout=5)
            value = result.stdout.strip()
            if value.isdigit():
                return int(value)
        except Exception:
            continue

    return 50


def _wifi_adapter_name() -> str:
    cmd = """
    $a = Get-NetAdapter | Where-Object {
        $_.Name -match 'Wi-Fi|WiFi|Wireless|WLAN|Inalámbrica|Inalambrica'
    } | Select-Object -First 1 -ExpandProperty Name
    if ($a) { $a }
    """
    try:
        result = _run_powershell(cmd, timeout=8)
        return result.stdout.strip()
    except Exception:
        return ""


def _set_wifi(enable: bool) -> str:
    name = _wifi_adapter_name()

    if not name:
        return "No encontré adaptador WiFi en esta PC."

    action = "Enable-NetAdapter" if enable else "Disable-NetAdapter"
    cmd = f'{action} -Name "{name}" -Confirm:$false'

    result = _run_powershell(cmd, timeout=10)

    if result.returncode == 0:
        return f"He {'encendido' if enable else 'apagado'} el WiFi."

    return f"No pude cambiar el WiFi. Ejecuta JARVIS como administrador. Detalle: {result.stderr.strip()}"


def _set_bluetooth(enable: bool) -> str:
    state = "Enable" if enable else "Disable"

    cmd = f"""
    $devices = Get-PnpDevice -Class Bluetooth -ErrorAction SilentlyContinue
    if (!$devices) {{
        Write-Output "NO_BLUETOOTH"
        exit
    }}
    foreach ($d in $devices) {{
        if ($d.InstanceId) {{
            try {{
                {state}-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
            }} catch {{}}
        }}
    }}
    Write-Output "OK"
    """

    result = _run_powershell(cmd, timeout=15)

    if "NO_BLUETOOTH" in result.stdout:
        return "No encontré Bluetooth en esta PC."

    if "OK" in result.stdout:
        return f"He {'encendido' if enable else 'apagado'} el Bluetooth."

    return f"No pude cambiar el Bluetooth. Ejecuta JARVIS como administrador. Detalle: {result.stderr.strip()}"


def _set_power_plan(plan: str) -> str:
    plans = {
        "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
        "equilibrado": "381b4222-f694-41f0-9685-ff5bb260df2e",
        "power_saver": "a1841308-3541-4fab-bc81-f71556f20b4a",
        "ahorro": "a1841308-3541-4fab-bc81-f71556f20b4a",
        "ahorro_energia": "a1841308-3541-4fab-bc81-f71556f20b4a",
        "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "alto_rendimiento": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
    }

    guid = plans.get(plan)

    if not guid:
        return "Plan de energía no reconocido."

    result = _run_cmd(f"powercfg /setactive {guid}", timeout=8)

    if result.returncode == 0:
        return f"He activado el plan de energía: {plan}."

    return f"No pude cambiar el plan de energía: {result.stderr.strip()}"


def computer_settings(parameters: dict, response=None, player=None) -> str:
    action = str(parameters.get("action", "")).lower().strip()
    value = str(parameters.get("value", "")).lower().strip()

    window_name = (
        parameters.get("window")
        or parameters.get("window_title")
        or parameters.get("app_name")
        or parameters.get("target")
        or ""
    )

    window_name = str(window_name).strip()

    try:
        import pyautogui
    except ImportError:
        return "Falta pyautogui. Instala con: pip install pyautogui"

    if action in ["close", "cerrar", "cerrar_app", "close_app", "exit", "salir"]:
        win, err = _find_window(window_name)
        if err:
            return err

        try:
            title = win.title
            win.activate()
            time.sleep(0.2)
            win.close()
            msg = f"He cerrado la ventana: {title}."
            if player:
                player.write_log(f"❌ {msg}")
            return msg
        except Exception:
            pyautogui.hotkey("alt", "f4")
            return "He enviado Alt + F4 para cerrar la ventana activa."

    if action in ["minimize", "minimizar", "segundo_plano", "background", "poner_en_segundo_plano"]:
        win, err = _find_window(window_name)
        if err:
            return err
        try:
            title = win.title
            win.minimize()
            return f"He minimizado la ventana: {title}."
        except Exception as e:
            return f"No pude minimizar la ventana: {e}"

    if action in ["maximize", "maximizar", "full_window", "agrandar"]:
        win, err = _find_window(window_name)
        if err:
            return err
        try:
            title = win.title
            win.activate()
            time.sleep(0.2)
            win.maximize()
            return f"He maximizado la ventana: {title}."
        except Exception as e:
            return f"No pude maximizar la ventana: {e}"

    if action in ["fullscreen", "pantalla_completa", "full_screen", "pantalla completa"]:
        win, err = _find_window(window_name)
        if err:
            return err
        try:
            title = win.title
            win.activate()
            time.sleep(0.2)
            pyautogui.press("f11")
            return f"He puesto en pantalla completa: {title}."
        except Exception as e:
            return f"No pude poner pantalla completa: {e}"

    if action in ["restore", "restaurar", "normal"]:
        win, err = _find_window(window_name)
        if err:
            return err
        try:
            title = win.title
            win.restore()
            win.activate()
            return f"He restaurado la ventana: {title}."
        except Exception as e:
            return f"No pude restaurar la ventana: {e}"

    if action in ["volume", "volumen", "set_volume", "subir_volumen", "bajar_volumen", "silenciar"]:
        try:
            if value.isdigit():
                target = _set_volume(int(value))
                return f"He ajustado el volumen al {target}%."

            current = _get_volume()

            if action == "subir_volumen" or "subir" in value or "up" in value or "alzar" in value:
                target = _set_volume(current + 10)
                return f"He subido el volumen al {target}%."

            if action == "bajar_volumen" or "bajar" in value or "down" in value:
                target = _set_volume(current - 10)
                return f"He bajado el volumen al {target}%."

            if action == "silenciar" or "mute" in value or "silenciar" in value:
                pyautogui.press("volumemute")
                return "He silenciado el volumen."

            return f"El volumen actual está en {current}%."

        except Exception:
            if "subir" in value or "up" in value or "alzar" in value:
                pyautogui.press("volumeup", presses=5)
                return "He subido el volumen."
            if "bajar" in value or "down" in value:
                pyautogui.press("volumedown", presses=5)
                return "He bajado el volumen."
            if "mute" in value or "silenciar" in value:
                pyautogui.press("volumemute")
                return "He silenciado el volumen."
            return "No pude controlar el volumen."

    if action in ["brightness", "brillo", "set_brightness", "subir_brillo", "bajar_brillo"]:
        if value.isdigit():
            target = int(value)
            if _set_brightness(target):
                return f"He ajustado el brillo al {max(0, min(100, target))}%."
            return "No pude ajustar el brillo. Este equipo puede no soportar control de brillo."

        current = _get_brightness()

        if action == "subir_brillo" or "subir" in value or "up" in value or "alzar" in value:
            target = max(0, min(100, current + 10))
            if _set_brightness(target):
                return f"He subido el brillo al {target}%."
            return "No pude subir el brillo."

        if action == "bajar_brillo" or "bajar" in value or "down" in value:
            target = max(0, min(100, current - 10))
            if _set_brightness(target):
                return f"He bajado el brillo al {target}%."
            return "No pude bajar el brillo."

        return f"El brillo actual está en {current}%."

    if action in ["wifi_on", "encender_wifi", "activar_wifi"]:
        return _set_wifi(True)

    if action in ["wifi_off", "apagar_wifi", "desactivar_wifi"]:
        return _set_wifi(False)

    if action in ["bluetooth_on", "encender_bluetooth", "activar_bluetooth", "encender_bluutoo"]:
        return _set_bluetooth(True)

    if action in ["bluetooth_off", "apagar_bluetooth", "desactivar_bluetooth", "apagar_bluutoo"]:
        return _set_bluetooth(False)

    if action in ["airplane", "modo_avion", "modo_avión", "airplane_mode"]:
        pyautogui.hotkey("win", "a")
        time.sleep(0.4)
        return "He abierto el panel rápido para controlar el modo avión."

    if action in ["power_saver", "ahorro_energia", "ahorro_de_energia", "modo_ahorro"]:
        return _set_power_plan("ahorro")

    if action in ["balanced", "equilibrado"]:
        return _set_power_plan("equilibrado")

    if action in ["high_performance", "alto_rendimiento", "maximo_rendimiento"]:
        return _set_power_plan("alto_rendimiento")

    if action in ["lock", "bloquear"]:
        pyautogui.hotkey("win", "l")
        return "He bloqueado la pantalla."

    if action in ["sleep", "suspender"]:
        _run_cmd("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "He enviado la PC a suspensión."

    # BLOQUE MODIFICADO: Se ha eliminado el código que ejecutaba el apagado/reinicio
    if action in ["shutdown", "apagar_pc"]:
        return "La función de apagar la PC ha sido deshabilitada de forma permanente por motivos de seguridad."

    if action in ["restart", "reiniciar_pc"]:
        return "La función de reiniciar la PC ha sido deshabilitada de forma permanente por motivos de seguridad."

    # Se actualizaron también las instrucciones sugeridas al final del archivo
    return (
        "Acción no reconocida. Puedes usar cerrar, minimizar, pantalla completa, "
        "volumen, brillo, WiFi, Bluetooth, modo avión, ahorro de energía, suspender o bloquear."
    )