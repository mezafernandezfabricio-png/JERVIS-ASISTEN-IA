# -*- coding: utf-8 -*-

import os
import json
import threading
import time
import gc
import re
from pathlib import Path

# =========================================================================
# CONFIGURACIÓN COMERCIAL PARA EL CLIENTE FINAL
# =========================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "remote_state.json"
API_FILE = BASE_DIR / "config" / "api_keys.json"

_bot_instance = None
_bot_thread = None
_stop_polling = False
_global_player = None

def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {"remote_active": False}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except:
        return {"remote_active": False}

def _save_config(data: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")

def _get_client_credentials():
    try:
        data = json.loads(API_FILE.read_text(encoding="utf-8"))
        token = data.get("telegram_bot_token", "")
        owner_id = str(data.get("telegram_owner_id", "")).strip()
        return token, owner_id
    except:
        return "", ""

def _get_player():
    """Busca la interfaz de JARVIS en la RAM de Windows."""
    global _global_player
    if _global_player:
        return _global_player
    for obj in gc.get_objects():
        if type(obj).__name__ == "JarvisUI":
            _global_player = obj
            return obj
    return None

def _esperar_respuesta_jarvis(player, max_wait_seconds=60):
    """Espera a que la PC base procese y responda."""
    start_time = time.time()
    last_length = 0
    stable_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        current_buffer = getattr(player, "jarvis_response_buffer", "")
        if len(current_buffer) > 0:
            if len(current_buffer) != last_length:
                last_length = len(current_buffer)
                stable_time = time.time()
            elif time.time() - stable_time > 2.5:
                break
        time.sleep(0.5)

    respuesta = getattr(player, "jarvis_response_buffer", "").strip()
    return respuesta if respuesta else "✅ Acción ejecutada silenciosamente en la PC base."

# =========================================================================
# MOTOR LONG-POLLING OMNIPOTENTE (Envío y Recepción de Archivos)
# =========================================================================
def _polling_loop():
    global _bot_instance, _stop_polling
    
    try:
        import telebot
    except ImportError:
        player = _get_player()
        if player: player.write_log("❌ Error: Ejecuta 'pip install pyTelegramBotAPI'")
        return

    token, owner_id = _get_client_credentials()
    
    if not token or not owner_id:
        player = _get_player()
        if player: player.write_log("⚠️ Faltan credenciales de Telegram.")
        return

    _bot_instance = telebot.TeleBot(token)

    @_bot_instance.message_handler(content_types=['text', 'photo', 'document', 'audio', 'video', 'voice'])
    def handle_all_messages(message):
        player = _get_player()
        
        # 1. SEGURIDAD
        sender_id = str(message.chat.id)
        if sender_id != owner_id:
            _bot_instance.reply_to(message, "⛔ ACCESO DENEGADO.")
            return

        if not player or not hasattr(player, 'on_text_command'):
            _bot_instance.reply_to(message, "⚠️ No pude enlazar con la PC. Reinicia JARVIS.")
            return

        is_file = False
        local_path = ""
        comando = ""
        caption = message.caption.strip() if message.caption else ""

        # 2. CELULAR -> PC (Recibir cualquier archivo y pasarlo a JARVIS)
        if message.content_type != 'text':
            status_msg = _bot_instance.reply_to(message, "📥 Transfiriendo datos al núcleo...")
            try:
                file_id = None
                file_name = f"mobile_upload_{int(time.time())}"
                
                if message.content_type == 'photo':
                    file_id = message.photo[-1].file_id
                    file_name += ".jpg"
                elif message.content_type == 'document':
                    file_id = message.document.file_id
                    file_name = message.document.file_name
                elif message.content_type == 'audio':
                    file_id = message.audio.file_id
                    file_name = message.audio.file_name or f"{file_name}.mp3"
                elif message.content_type == 'video':
                    file_id = message.video.file_id
                    file_name = message.video.file_name or f"{file_name}.mp4"
                elif message.content_type == 'voice':
                    file_id = message.voice.file_id
                    file_name += ".ogg"
                
                if file_id:
                    file_info = _bot_instance.get_file(file_id)
                    downloaded_file = _bot_instance.download_file(file_info.file_path)
                    
                    save_dir = BASE_DIR / "downloads" / "telegram"
                    save_dir.mkdir(parents=True, exist_ok=True)
                    local_path = save_dir / file_name
                    
                    with open(local_path, 'wb') as new_file:
                        new_file.write(downloaded_file)
                        
                    is_file = True
                    _bot_instance.edit_message_text(
                        "🧠 Datos recibidos. JARVIS analizando...", 
                        chat_id=message.chat.id, 
                        message_id=status_msg.message_id
                    )
            except Exception as e:
                _bot_instance.edit_message_text(f"❌ Error de transferencia: {e}", chat_id=message.chat.id, message_id=status_msg.message_id)
                return
        else:
            comando = message.text.strip()
            status_msg = _bot_instance.reply_to(message, "⏳ JARVIS procesando orden...")

        # 3. PREPARAR EL CEREBRO EN LA PC
        if hasattr(player, "clear_jarvis_response"):
            player.clear_jarvis_response()
        else:
            player.jarvis_response_buffer = ""

        # 4. INYECTAR LA ORDEN
        if is_file:
            player.current_file = str(local_path)
            
            if caption:
                # Si enviaste una foto con texto, le dice qué hacer exactamente
                player.on_text_command(f"JARVIS, analiza el archivo en {local_path}. Instrucción: {caption}")
            else:
                # Emula que soltaste el archivo en la interfaz
                player.on_text_command(f"[DROPPED_FILE] path={local_path}")
            
            if player: player.write_log(f"📱 Archivo remoto inyectado: {local_path}")
        else:
            comando_para_pc = f"JARVIS, {comando}"
            player.on_text_command(comando_para_pc)
            if player: player.write_log(f"📱 Comando remoto: {comando}")

        # 5. OBTENER RESPUESTA DE LA PC
        respuesta_final = _esperar_respuesta_jarvis(player, max_wait_seconds=120) # 120s por si tarda generando imágenes
        
        try:
            _bot_instance.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text=respuesta_final)
        except Exception:
            _bot_instance.reply_to(message, respuesta_final)

        # =========================================================================
        # 6. PC -> CELULAR (MAGIA BIDIRECCIONAL: EXTRAER Y ENVIAR ARCHIVOS)
        # Busca cualquier ruta de archivo en Windows (C:\..., D:\...) dentro de lo
        # que respondió JARVIS. Si lo encuentra, te manda el archivo por Telegram.
        # =========================================================================
        try:
            # Regex avanzado para capturar rutas de Windows
            rutas_encontradas = re.findall(
                r'([A-Za-z]:[\\/][^:*?"<>|\n\r]+?\.(?:png|jpg|jpeg|gif|pdf|docx|xlsx|txt|csv|mp3|wav|mp4|avi|html))', 
                respuesta_final, 
                re.IGNORECASE
            )
            
            # Limpiamos duplicados
            rutas_unicas = set(rutas_encontradas)
            
            for ruta in rutas_unicas:
                ruta_limpia = ruta.strip('\'" \n\r')
                if os.path.exists(ruta_limpia):
                    ext = ruta_limpia.lower().split('.')[-1]
                    _bot_instance.send_chat_action(message.chat.id, 'upload_document')
                    
                    with open(ruta_limpia, 'rb') as f:
                        if ext in ['png', 'jpg', 'jpeg', 'gif']:
                            _bot_instance.send_photo(message.chat.id, f)
                        elif ext in ['mp3', 'wav']:
                            _bot_instance.send_audio(message.chat.id, f)
                        elif ext in ['mp4', 'avi']:
                            _bot_instance.send_video(message.chat.id, f)
                        else:
                            _bot_instance.send_document(message.chat.id, f)
                    
                    if player: player.write_log(f"📤 Archivo enviado al celular: {ruta_limpia}")
        except Exception as e:
            if player: player.write_log(f"⚠️ Error enviando archivo al móvil: {e}")

    # Arranque de bucle
    player = _get_player()
    if player: player.write_log("🌐 Enlace omnipotente online. Soporte total activado.")
    
    while not _stop_polling:
        try:
            _bot_instance.polling(non_stop=True, interval=1, timeout=20)
        except Exception:
            time.sleep(5)

    _bot_instance.stop_polling()
    player = _get_player()
    if player: player.write_log("🛑 Enlace satelital cerrado.")

def _start_server():
    global _bot_thread, _stop_polling
    if _bot_thread is not None and _bot_thread.is_alive():
        return "El enlace remoto ya estaba activo, señor."

    _stop_polling = False
    _bot_thread = threading.Thread(target=_polling_loop, daemon=True)
    _bot_thread.start()
    return "He activado tu conexión remota segura."

def _stop_server():
    global _bot_thread, _stop_polling
    if _bot_thread is None or not _bot_thread.is_alive():
        return "El servidor remoto ya estaba apagado."
        
    _stop_polling = True
    if _bot_instance:
        _bot_instance.stop_bot()
        
    _bot_thread.join(timeout=3)
    _bot_thread = None
    return "Conexiones remotas cerradas."

def remote_assistant(parameters: dict, player=None) -> str:
    global _global_player
    if player: _global_player = player
        
    action = parameters.get("action", "").lower()
    config = _load_config()

    if action in ["activar", "encender", "start"]:
        config["remote_active"] = True
        _save_config(config)
        return _start_server()

    elif action in ["desactivar", "apagar", "stop"]:
        config["remote_active"] = False
        _save_config(config)
        return _stop_server()

    return f"No comprendo la instrucción remota: {action}."

_initial_config = _load_config()
if _initial_config.get("remote_active", False):
    _start_server()