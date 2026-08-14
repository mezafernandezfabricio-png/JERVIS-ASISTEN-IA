# -*- coding: utf-8 -*-
import cv2
import sys
import numpy as np
try:
    import mediapipe as mp
except ImportError:
    mp = None
try:
    import pyautogui
    pyautogui.FAILSAFE = False
except ImportError:
    pyautogui = None

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

class VisionControlWorker(QThread):
    # Señal que transmite el cuadro procesado de la cámara a la UI de forma segura
    frame_ready = pyqtSignal(QPixmap)

    def __init__(self, mode="preview"):
        super().__init__()
        self.mode = mode  # Modos válidos: "preview" (solo ver feed) o "mouse_gesture" (controlador)
        self._running = True
        
        # Parámetros para suavizado del movimiento del mouse (Filtro de media móvil)
        self.prev_x, self.prev_y = 0, 0
        self.smoothing = 0.25  # Factor de interpolación lineal (menor = más suave pero más retraso)
        self.is_dragging = False

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            print("[VISION] Error: No se pudo acceder a la cámara web.")
            return

        # Inicialización de MediaPipe Hands si el modo requiere gestos cinéticos
        hands = None
        if mp and self.mode == "mouse_gesture":
            hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            screen_w, screen_h = pyautogui.size() if pyautogui else (1920, 1080)

        while self._running:
            ret, frame = cap.read()
            if not ret:
                continue

            # Voltear el cuadro horizontalmente para un efecto espejo natural
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape

            # Procesamiento de gestos cinéticos
            if hands and self.mode == "mouse_gesture" and pyautogui:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Dibujar el esqueleto de la mano en el frame de previsualización
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                        )

                        # Coordenadas de puntos clave
                        thumb_tip = hand_landmarks.landmark[4]
                        index_tip = hand_landmarks.landmark[8]
                        middle_tip = hand_landmarks.landmark[12]

                        # 1. Movimiento del puntero: Rastrea el extremo del dedo índice (#8)
                        # Creamos un margen de seguridad del 15% en los bordes para alcanzar esquinas con facilidad
                        margin = 0.15
                        ix = np.interp(index_tip.x, [margin, 1.0 - margin], [0, screen_w])
                        iy = np.interp(index_tip.y, [margin, 1.0 - margin], [0, screen_h])

                        # Aplicar filtro de suavizado para eliminar temblores de la mano
                        curr_x = self.prev_x + (ix - self.prev_x) * self.smoothing
                        curr_y = self.prev_y + (iy - self.prev_y) * self.smoothing
                        
                        pyautogui.moveTo(int(curr_x), int(curr_y))
                        self.prev_x, self.prev_y = curr_x, curr_y

                        # 2. Detección de Pinch (Clic/Arrastrar): Distancia entre pulgar (#4) e índice (#8)
                        p1 = np.array([thumb_tip.x * w, thumb_tip.y * h])
                        p2 = np.array([index_tip.x * w, index_tip.y * h])
                        distance_click = np.linalg.norm(p1 - p2)

                        # Si la distancia es menor a 35 píxeles, se interpreta como presión
                        if distance_click < 35:
                            if not self.is_dragging:
                                pyautogui.mouseDown()
                                self.is_dragging = True
                                # Dibujar indicador visual en pantalla (Círculo de acción de clic)
                                cv2.circle(frame, (int(index_tip.x * w), int(index_tip.y * h)), 15, (0, 255, 0), -1)
                        else:
                            if self.is_dragging:
                                pyautogui.mouseUp()
                                self.is_dragging = False

            # Convertir el cuadro OpenCv (BGR) a formato compatible con QImage/QPixmap (RGB)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_img = QImage(rgb_image.data, w, h, w * c, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # Emitir el frame hacia la ventana principal de Qt
            self.frame_ready.emit(pixmap)

        if hands:
            hands.close()
        cap.release()

    def stop(self):
        self._running = False
        if self.is_dragging and pyautogui:
            pyautogui.mouseUp()
        self.wait()

def vision_control(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """Control de visión por computadora y gestos cinéticos."""
    parameters = parameters or {}
    mode = (parameters.get("mode") or parameters.get("action") or "preview").lower()
    if player and hasattr(player, "_toggle_mouse_kinetic") and mode in ["mouse", "gesture", "gestos"]:
        player._toggle_mouse_kinetic()
        return "Control por gestos de visión artificial alternado."
    elif player and hasattr(player, "_toggle_camera_preview"):
        player._toggle_camera_preview()
        return "Visor de cámara alternado."
    return f"Módulo de visión artificial operativo en modo '{mode}'."