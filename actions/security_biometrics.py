# -*- coding: utf-8 -*-

import os
import json
import time
import threading
import ctypes
import platform
from pathlib import Path

# =========================================================================
# CONFIGURACIÓN Y ESTADO
# =========================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "biometrics_state.json"

# Variables globales para el hilo en segundo plano
_face_thread = None
_stop_face_thread = False

def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {"face_lock_active": False, "voice_auth_active": False}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except:
        return {"face_lock_active": False, "voice_auth_active": False}

def _save_config(data: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")

# =========================================================================
# MOTOR DE BIOMETRÍA FACIAL (HILO EN SEGUNDO PLANO)
# =========================================================================
def _face_monitor_loop(player):
    """
    Vigila la cámara en segundo plano. Si no detecta un rostro en 15 segundos,
    bloquea automáticamente el sistema operativo por seguridad.
    """
    global _stop_face_thread
    
    try:
        import cv2
        import mediapipe as mp
    except ImportError:
        if player: player.write_log("❌ Faltan librerías: pip install opencv-python mediapipe")
        return

    mp_face_detection = mp.solutions.face_detection
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        if player: player.write_log("⚠️ No se pudo acceder a la cámara para el bloqueo facial.")
        return

    missing_frames = 0
    max_missing = 20  # Aprox 10 segundos a 0.5s por ciclo
    
    if player: player.write_log("🛡️ Centinela facial activado. Vigilando tu presencia...")

    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        while not _stop_face_thread:
            ret, frame = cap.read()
            if not ret:
                time.sleep(1)
                continue
            
            # Convertir a RGB para MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(frame_rgb)

            if results.detections:
                # Rostro detectado, reiniciar contador
                missing_frames = 0
            else:
                # No hay rostro
                missing_frames += 1

            # Si pasa demasiado tiempo sin ver un rostro, bloquea la PC
            if missing_frames >= max_missing:
                if player: player.write_log("🔒 Presencia perdida. Bloqueando Windows por seguridad.")
                
                # Comando nativo para bloquear Windows 11
                if platform.system() == "Windows":
                    ctypes.windll.user32.LockWorkStation()
                
                # Esperar un minuto antes de volver a escanear para no saturar
                time.sleep(60)
                missing_frames = 0

            time.sleep(0.5) # Pausa para no consumir mucha CPU

    cap.release()
    if player: player.write_log("🛡️ Centinela facial desactivado.")

def _start_face_monitoring(player=None):
    global _face_thread, _stop_face_thread
    if _face_thread is None or not _face_thread.is_alive():
        _stop_face_thread = False
        _face_thread = threading.Thread(target=_face_monitor_loop, args=(player,), daemon=True)
        _face_thread.start()

def _stop_face_monitoring():
    global _stop_face_thread, _face_thread
    _stop_face_thread = True
    if _face_thread is not None:
        _face_thread.join(timeout=2)
        _face_thread = None

# =========================================================================
# CONTROLADOR PRINCIPAL DE LA ACCIÓN
# =========================================================================
def security_biometrics(parameters: dict, player=None) -> str:
    """
    Gestiona la activación y desactivación de la biometría (facial y voz).
    """
    action = parameters.get("action", "").lower()
    config = _load_config()

    # 1. ACTIVAR BLOQUEO FACIAL
    if action in ["activar_facial", "activa facial", "activar centinela", "vigila mi pc"]:
        if config["face_lock_active"]:
            return "La seguridad facial ya se encuentra activa, señor."
        
        config["face_lock_active"] = True
        _save_config(config)
        _start_face_monitoring(player)
        return "Protocolo de seguridad facial activado. Bloquearé la PC automáticamente si te alejas."

    # 2. DESACTIVAR BLOQUEO FACIAL
    elif action in ["desactivar_facial", "desactiva facial", "apaga la camara de seguridad"]:
        if not config["face_lock_active"]:
            return "El centinela facial ya estaba desactivado."
        
        config["face_lock_active"] = False
        _save_config(config)
        _stop_face_monitoring()
        return "He desactivado la vigilancia facial. Tu PC no se bloqueará si te levantas."

    # 3. ACTIVAR RECONOCIMIENTO DE VOZ ESTRICTO
    elif action in ["activar_voz", "activa seguridad de voz"]:
        config["voice_auth_active"] = True
        _save_config(config)
        if player: player.write_log("🎙️ Seguridad de voz estricta HABILITADA.")
        return "He activado la restricción de voz. De ahora en adelante, validaré tu identidad antes de ejecutar comandos críticos."

    # 4. DESACTIVAR RECONOCIMIENTO DE VOZ
    elif action in ["desactivar_voz", "desactiva seguridad de voz"]:
        config["voice_auth_active"] = False
        _save_config(config)
        if player: player.write_log("🎙️ Seguridad de voz estricta DESHABILITADA.")
        return "Restricciones de voz levantadas. Ejecutaré cualquier orden sin verificar la identidad del hablante."

    # 5. VERIFICACIÓN DE VOZ (Uso interno para otras herramientas de JARVIS)
    elif action == "verificar_identidad":
        if not config.get("voice_auth_active", False):
            return "PERMITIDO" # Si está apagado, permite todo
        
        # Aquí puedes enganchar la lógica de pyannote.audio o verificación.
        # Por ahora, es un simulador estructural para integración de modelos.
        return "DENEGADO_VOZ_NO_RECONOCIDA"

    else:
        return f"No comprendo la instrucción de seguridad: {action}."

# Autoinicio si estaba activo en la sesión anterior
_initial_config = _load_config()
if _initial_config.get("face_lock_active", False):
    _start_face_monitoring()