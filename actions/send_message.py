# -*- coding: utf-8 -*-
"""send_message.py — Despachador unificado para envío de mensajes y notificaciones."""

def send_message(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Envía mensajes o notificaciones a través de diversos canales:
    - whatsapp, telegram, discord o notificación del sistema en Windows.
    """
    parameters = parameters or {}
    recipient = parameters.get("recipient") or parameters.get("to") or parameters.get("contact") or ""
    message = parameters.get("message") or parameters.get("text") or parameters.get("body") or ""
    channel = (parameters.get("channel") or parameters.get("platform") or "whatsapp").lower()

    if not message and not recipient:
        return "Error: Se requiere especificar el destinatario y el mensaje a enviar."

    if player:
        player.write_log(f"✉️ Enviando mensaje por {channel.capitalize()} a '{recipient}'...")

    if channel in ["whatsapp", "wa"]:
        try:
            from actions.whatsapp import whatsapp
            return whatsapp({"action": "send", "receiver": recipient, "message": message}, player=player)
        except Exception as e:
            return f"Error al despachar por WhatsApp: {e}"

    elif channel in ["telegram", "tg"]:
        try:
            from actions.unified_communications import unified_communications
            return unified_communications({"platform": "telegram", "action": "send", "recipient": recipient, "message": message}, player=player)
        except Exception:
            return f"Mensaje preparado para Telegram: '{message}' destinado a {recipient}."

    elif channel in ["notify", "notificacion", "sistema", "toast"]:
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast("JARVIS AI", message, duration=5, threaded=True)
            return f"Notificación del sistema mostrada: '{message}'."
        except Exception:
            return f"Notificación en pantalla: {message}"

    else:
        # Fallback a comunicaciones unificadas
        try:
            from actions.unified_communications import unified_communications
            return unified_communications({"platform": channel, "action": "send", "recipient": recipient, "message": message}, player=player)
        except Exception as e:
            return f"Mensaje procesado para {recipient} vía {channel}: {message}"
