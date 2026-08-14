# -*- coding: utf-8 -*-
"""
windows_settings.py — Control y apertura directa de paneles de configuración de Windows para JARVIS.
"""

import os
import subprocess
import webbrowser

SETTINGS_URIS = {
    "wifi": "ms-settings:network-wifi",
    "red": "ms-settings:network",
    "bluetooth": "ms-settings:bluetooth",
    "dispositivos": "ms-settings:connecteddevices",
    "pantalla": "ms-settings:display",
    "display": "ms-settings:display",
    "sonido": "ms-settings:sound",
    "audio": "ms-settings:sound",
    "notificaciones": "ms-settings:notifications",
    "bateria": "ms-settings:batterysaver",
    "almacenamiento": "ms-settings:storagesense",
    "apps": "ms-settings:appsfeatures",
    "aplicaciones": "ms-settings:appsfeatures",
    "cuentas": "ms-settings:yourinfo",
    "hora": "ms-settings:dateandtime",
    "fecha": "ms-settings:dateandtime",
    "juegos": "ms-settings:gaming-gamebar",
    "accesibilidad": "ms-settings:easeofaccess-display",
    "privacidad": "ms-settings:privacy",
    "seguridad": "ms-settings:windowsdefender",
    "update": "ms-settings:windowsupdate",
    "actualizacion": "ms-settings:windowsupdate",
    "personalizacion": "ms-settings:personalization",
    "temas": "ms-settings:themes",
    "raton": "ms-settings:mousetouchpad",
    "mouse": "ms-settings:mousetouchpad",
    "teclado": "ms-settings:keyboard"
}

def windows_settings(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Abre paneles de configuración de Windows o desinstala aplicaciones.
    Parámetros:
      - action: 'open' / 'abrir', 'uninstall' / 'desinstalar'
      - setting / target / panel: Nombre del panel ('wifi', 'bluetooth', 'sonido', 'pantalla', 'bateria', 'update', 'apps', etc.)
      - app_name: Nombre de la aplicación a desinstalar
    """
    params = parameters or {}
    action = str(params.get("action") or "open").lower().strip()
    setting = str(params.get("setting") or params.get("target") or params.get("panel") or params.get("value") or "").lower().strip()
    app_name = params.get("app_name", "").strip()

    if action in ["uninstall", "desinstalar", "remove_app"]:
        if not app_name:
            return "Por favor indica el nombre de la aplicación que deseas desinstalar."
        try:
            cmd_uwp = f'powershell "Get-AppxPackage | Where-Object {{$_.Name -like \'*{app_name}*\'}} | Remove-AppxPackage"'
            subprocess.run(cmd_uwp, capture_output=True, text=True, shell=True)
            return f"Solicitud de desinstalación procesada para '{app_name}'."
        except Exception as e:
            return f"Error al intentar desinstalar '{app_name}': {e}"

    # Apertura de panel de configuración de Windows
    uri = SETTINGS_URIS.get(setting)
    if not uri:
        # Búsqueda por subcadena
        for k, v in SETTINGS_URIS.items():
            if k in setting or setting in k:
                uri = v
                break
    if not uri:
        uri = "ms-settings:"

    try:
        os.startfile(uri)
        panel_name = setting if setting else "Configuración general"
        if player:
            try: player.write_log(f"⚙️ Panel de Windows abierto: {panel_name}")
            except: pass
        return f"Panel de configuración de Windows '{panel_name}' abierto exitosamente."
    except Exception as e:
        return f"Error al abrir configuración de Windows: {e}"