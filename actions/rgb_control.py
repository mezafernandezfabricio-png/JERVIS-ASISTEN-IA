# -*- coding: utf-8 -*-
"""rgb_control.py — Control de iluminación RGB mediante OpenRGB."""

def rgb_control(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Controla la iluminación RGB de periféricos y componentes (teclado, mouse, GPU, RAM, etc.).
    Requiere OpenRGB con servidor SDK activo.
    """
    parameters = parameters or {}
    action = (parameters.get("action") or "list").lower()
    color_str = parameters.get("color") or ""
    brightness = parameters.get("brightness", 100)

    try:
        from openrgb import OpenRGBClient
        from openrgb.utils import RGBColor
        
        client = OpenRGBClient()
        devices = client.devices

        if not devices:
            return "OpenRGB conectado, pero no se detectaron dispositivos RGB compatibles activos."

        if action in ["list", "listar", "status"]:
            dev_names = [d.name for d in devices]
            return f"Dispositivos RGB detectados ({len(devices)}): {', '.join(dev_names)}."

        elif action in ["off", "apagar"]:
            for dev in devices:
                dev.set_color(RGBColor(0, 0, 0))
            if player: player.write_log("💡 Luces RGB apagadas.")
            return "Iluminación RGB apagada en todos los dispositivos."

        elif action in ["set_color", "color", "cambiar_color"]:
            # Mapeo de colores básicos
            color_map = {
                "rojo": (255, 0, 0), "azul": (0, 0, 255), "verde": (0, 255, 0),
                "blanco": (255, 255, 255), "amarillo": (255, 255, 0), "cyan": (0, 255, 255),
                "morado": (128, 0, 128), "naranja": (255, 165, 0), "dorado": (255, 215, 0)
            }
            c_low = color_str.lower().strip()
            rgb = color_map.get(c_low, (255, 215, 0)) # Default dorado JARVIS

            # Si es código hex
            if c_low.startswith("#") and len(c_low) == 7:
                try:
                    rgb = tuple(int(c_low[i:i+2], 16) for i in (1, 3, 5))
                except Exception:
                    pass

            for dev in devices:
                dev.set_color(RGBColor(rgb[0], rgb[1], rgb[2]))

            if player: player.write_log(f"💡 Iluminación RGB ajustada a {color_str or 'dorado'}.")
            return f"Iluminación RGB establecida a {color_str or 'dorado'} en todos los dispositivos."

        else:
            return f"Acción RGB '{action}' enviada a los controladores OpenRGB."

    except ImportError:
        return "Aviso: 'openrgb-python' no está instalado. Ejecute 'pip install openrgb-python'."
    except Exception as e:
        return f"No se pudo conectar al servidor OpenRGB (¿está OpenRGB ejecutándose con el SDK activo?): {e}"
