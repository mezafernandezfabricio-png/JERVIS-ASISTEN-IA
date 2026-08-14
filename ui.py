# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import os
import json
import psutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QProgressBar,
    QDialog, QMessageBox, QComboBox, QCheckBox, QScrollArea,
    QTextEdit, QTabWidget, QFormLayout
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, pyqtSlot, QObject, QTimer, QThread
from PyQt6.QtGui import QFont, QIcon, QMouseEvent, QTextCursor, QImage, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

try:
    import qtawesome as qta
    HAS_QTA = True
except ImportError:
    HAS_QTA = False

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False


_BA_TZ = timezone(timedelta(hours=-5))


THEMES = {
    "gold": {
        "PRI": "#FFFFFF", 
        "PRI_DIM": "#ffffff",
        "BG": "#0f0a02",
        "PANEL": "rgba(20, 15, 6, 0.62)",
        "BORDER": "rgba(255, 255, 255, 0.38)",
        "TEXT": "#ffffff"
    },
    "cyan": {
        "PRI": "#00d4ff",
        "PRI_DIM": "#005f77",
        "BG": "#050c14",
        "PANEL": "rgba(10, 22, 32, 0.62)",
        "BORDER": "rgba(0, 212, 255, 0.38)",
        "TEXT": "#7aeeff"
    },
    "green": {
        "PRI": "#00ff88",
        "PRI_DIM": "#006633",
        "BG": "#040e08",
        "PANEL": "rgba(8, 26, 16, 0.62)",
        "BORDER": "rgba(0, 255, 136, 0.38)",
        "TEXT": "#7affcc"
    },
    "purple": {
        "PRI": "#a855f7",
        "PRI_DIM": "#5b21b6",
        "BG": "#07030f",
        "PANEL": "rgba(15, 6, 24, 0.62)",
        "BORDER": "rgba(168, 85, 247, 0.38)",
        "TEXT": "#c084fc"
    },
    "white": {
        "PRI": "#e2e8f0",
        "PRI_DIM": "#64748b",
        "BG": "#050a14",
        "PANEL": "rgba(12, 22, 38, 0.62)",
        "BORDER": "rgba(226, 232, 240, 0.38)",
        "TEXT": "#cbd5e1"
    }
}


C_PRI = "#FFFFFF"
C_PRI_DIM = "#78350f"
C_BG = "#0f0a02"
C_PANEL = "rgba(20, 15, 6, 0.62)"
C_BORDER = "rgba(255, 255, 255, 0.38)"
C_TEXT = "#ffffff"
RED = "#ff3b30"


def apply_theme_tokens(theme_name: str):
    global C_PRI, C_PRI_DIM, C_BG, C_PANEL, C_BORDER, C_TEXT
    t = THEMES.get(str(theme_name).lower(), THEMES["gold"])
    C_PRI = t["PRI"]
    C_PRI_DIM = t["PRI_DIM"]
    C_BG = t["BG"]
    C_PANEL = t["PANEL"]
    C_BORDER = t["BORDER"]
    C_TEXT = t["TEXT"]


try:
    from memory.config_manager import load_api_keys
    apply_theme_tokens(load_api_keys().get("jarvis_theme", "white"))
except Exception:
    apply_theme_tokens("white")


class WebBridge(QObject):
    def __init__(self, orb):
        super().__init__()
        self.orb = orb

    @pyqtSlot()
    def toggle_mute(self):
        if self.orb.ui:
            self.orb.ui._win._toggle_mute()

    @pyqtSlot()
    def request_theme(self):
        QTimer.singleShot(0, self.orb.sync_theme)


class CustomParticleOrb(QWidget):
    audio_signal = pyqtSignal(float)
    state_signal = pyqtSignal(str)
    theme_signal = pyqtSignal()

    def __init__(self, ui, parent=None):
        super().__init__(parent)
        self.ui = ui
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView(self)
        self.web_view.setAcceptDrops(False)
        
        self.web_view.setStyleSheet("""
            QWebEngineView {
                background: transparent;
                border: none;
            }
        """)
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)

        try:
            from PyQt6.QtWebEngineCore import QWebEngineSettings
            settings = self.web_view.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, False)
        except Exception:
            pass

        self.channel = QWebChannel()
        self.bridge = WebBridge(self)
        self.channel.registerObject("pyBridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        sphere_path = Path(__file__).parent / "assets" / "sphere.html"
        self.web_view.setUrl(QUrl.fromLocalFile(str(sphere_path.absolute())))

        layout.addWidget(self.web_view)

        self.audio_signal.connect(self._safe_set_audio)
        self.state_signal.connect(self._safe_set_state)
        self.theme_signal.connect(self._safe_sync_theme)
        self.web_view.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self, ok):
        if ok:
            self.sync_theme()
            self.set_state("MUTED" if self.ui.muted else "LISTENING")
            self._clean_orb_reflections()

    def _clean_orb_reflections(self):
        js = """
        try {
            document.body.style.background = "transparent";
            document.documentElement.style.background = "transparent";
            document.querySelectorAll("*").forEach(el => {
                const s = window.getComputedStyle(el);
                const id = (el.id || "").toLowerCase();
                const cls = (el.className || "").toString().toLowerCase();
                if (
                    id.includes("reflection") ||
                    cls.includes("reflection") ||
                    id.includes("flare") ||
                    cls.includes("flare") ||
                    id.includes("glow-side") ||
                    cls.includes("glow-side") ||
                    cls.includes("side")
                ) {
                    el.style.display = "none";
                    el.style.opacity = "0";
                    el.style.visibility = "hidden";
                }
                el.style.boxShadow = "none";
                el.style.filter = "none";
            });
        } catch(e) {}
        """
        self.web_view.page().runJavaScript(js)

    def sync_theme(self):
        self.theme_signal.emit()

    def set_audio(self, level: float):
        self.audio_signal.emit(level)

    def set_state(self, state: str):
        self.state_signal.emit(state)

    def _safe_sync_theme(self):
        colors = {
            "PRI": C_PRI,
            "PRI_DIM": C_PRI_DIM,
            "TEXT": C_TEXT,
            "BG": C_BG
        }
        js_code = f"""
        if (window.setThemeColors) window.setThemeColors({json.dumps(colors)});
        document.body.style.background = "transparent";
        """
        self.web_view.page().runJavaScript(js_code)
        self._clean_orb_reflections()

    def _safe_set_audio(self, level: float):
        self.web_view.page().runJavaScript(f"if (window.updateVolume) window.updateVolume({level});")

    def _safe_set_state(self, state: str):
        self.web_view.page().runJavaScript(f"if (window.updateState) window.updateState('{state}');")


class ChatInputWidget(QWidget):
    def __init__(self, ui, parent=None):
        super().__init__(parent)
        self.ui = ui
        self.setObjectName("ChatInputWidget")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Escribe un comando o suelta un archivo aquí...")
        self.btn_send = QPushButton("ENVIAR")

        if HAS_QTA:
            self.btn_send.setIcon(qta.icon("fa5s.paper-plane", color="black"))

        self.btn_send.setFixedWidth(110)

        layout.addWidget(self.input)
        layout.addWidget(self.btn_send)

        self.btn_send.clicked.connect(self.send_text)
        self.input.returnPressed.connect(self.send_text)

        self.update_style()

    def send_text(self):
        text = self.input.text().strip()
        if not text:
            return

        self.input.clear()
        self.ui.full_chat_history.append({"role": "user", "text": text})

        try:
            self.ui.clear_jarvis_response()
            self.ui.stream_jarvis_chunk(f"{self.ui.user_name}: " + text)
        except Exception:
            pass

        if self.ui.on_text_command:
            self.ui.on_text_command(text)

    def update_style(self):
        self.setStyleSheet(f"""
            QWidget#ChatInputWidget {{
                background: rgba(0,0,0,0.32);
                border: 1.4px solid {C_BORDER};
                border-radius: 14px;
            }}
            QLineEdit {{
                background: rgba(0,0,0,0.42);
                border: 1px solid {C_BORDER};
                border-radius: 10px;
                padding: 10px 14px;
                color: white;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {C_PRI};
            }}
            QPushButton {{
                background: {C_PRI};
                color: black;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: white;
            }}
        """)


class HistoryDialog(QDialog):
    def __init__(self, ui, parent=None):
        super().__init__(parent)
        self.ui = ui
        self.setWindowTitle("Registro de Sesión")
        self.resize(650, 550)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        title = QLabel(f"Registro de Conversación ({self.ui.ai_name})")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {C_PRI};")
        main_layout.addWidget(title)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        main_layout.addWidget(self.text_area)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.btn_close = QPushButton("Cerrar Historial")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.accept)
        bottom_layout.addWidget(self.btn_close)
        main_layout.addLayout(bottom_layout)
        
        self.update_style()
        self.load_history()

    def load_history(self):
        html = "<div style='font-family: \"Segoe UI\", sans-serif; font-size: 14px;'>"
        
        if not self.ui.full_chat_history and not self.ui.jarvis_response_buffer:
            html += f"<p style='color: #94a3b8; text-align: center; margin-top: 50px;'>El registro de sesión está vacío.</p>"
        else:
            for item in self.ui.full_chat_history:
                role = item['role']
                text = item['text']
                if role == "user":
                    html += f"<p style='color: #38bdf8; margin: 10px 0;'><b>{self.ui.user_name}:</b><br>{text}</p>"
                elif role == "jarvis":
                    html += f"<p style='color: {C_PRI}; margin: 10px 0;'><b>{self.ui.ai_name}:</b><br>{text}</p>"
                elif role == "sys":
                    html += f"<p style='color: #94a3b8; font-style: italic; margin: 5px 0;'>[Sistema: {text}]</p>"
            
            curr = self.ui.jarvis_response_buffer
            if curr and not curr.startswith(self.ui.user_name):
                html += f"<p style='color: {C_PRI}; margin: 10px 0;'><b>{self.ui.ai_name} (Escribiendo...):</b><br>{curr}</p>"
        
        html += "</div>"
        self.text_area.setHtml(html)
        self.text_area.moveCursor(QTextCursor.MoveOperation.End)

    def update_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #030811; 
                border: 1px solid {C_PRI};
                border-radius: 10px;
            }}
            QTextEdit {{
                background: rgba(0, 0, 0, 0.4);
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }}
            QTextEdit QScrollBar:vertical {{
                background: #060b14;
                width: 8px;
                margin: 0px;
            }}
            QTextEdit QScrollBar::handle:vertical {{
                background: {C_PRI_DIM};
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: #f1f5f9;
                color: black;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: white;
            }}
        """)


class DeviceSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Centro de Mando")
        self.resize(650, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        title = QLabel("Ajustes del Sistema")
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {C_PRI};")
        main_layout.addWidget(title)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- TAB 1: Motores de IA y Nombres ---
        tab_ai = QWidget()
        lay_ai = QFormLayout(tab_ai)
        lay_ai.setSpacing(15)
        lay_ai.setContentsMargins(15, 20, 15, 15)

        self.inp_user_name = QLineEdit()
        lay_ai.addRow("Tu Nombre:", self.inp_user_name)

        self.inp_ai_name = QLineEdit()
        lay_ai.addRow("Nombre de la IA:", self.inp_ai_name)
        
        self.inp_gemini = QLineEdit()
        self.inp_gemini.setEchoMode(QLineEdit.EchoMode.Password)
        lay_ai.addRow("Gemini API Key:", self.inp_gemini)
        
        self.inp_openrouter = QLineEdit()
        self.inp_openrouter.setEchoMode(QLineEdit.EchoMode.Password)
        lay_ai.addRow("OpenRouter API Key:", self.inp_openrouter)
        
        self.tabs.addTab(tab_ai, "Nombres e IA")
        
        # --- TAB 2: Interfaz y Voz ---
        tab_ui = QWidget()
        lay_ui = QFormLayout(tab_ui)
        lay_ui.setSpacing(15)
        lay_ui.setContentsMargins(15, 20, 15, 15)
        
        self.cmb_theme = QComboBox()
        for k in THEMES.keys():
            self.cmb_theme.addItem(k.upper(), k)
        lay_ui.addRow("Tema Visual:", self.cmb_theme)
        
        self.cmb_voice = QComboBox()
        self.cmb_voice.addItem("Aoede - Femenina (Cálida / Asistente Natural)", "Aoede")
        self.cmb_voice.addItem("Charon - Masculina (Profunda / JARVIS Clásico)", "Charon")
        self.cmb_voice.addItem("Puck - Masculina (Dinámica / Juvenil)", "Puck")
        self.cmb_voice.addItem("Kore - Femenina (Suave / Relajante)", "Kore")
        self.cmb_voice.addItem("Fenrir - Masculina (Grave / Firme)", "Fenrir")
        self.cmb_voice.addItem("Leda - Femenina (Clara / Articulada)", "Leda")
        self.cmb_voice.addItem("Orus - Masculina (Directa / Equilibrada)", "Orus")
        self.cmb_voice.addItem("Zephyr - Femenina (Moderna / Vivaz)", "Zephyr")
        lay_ui.addRow("Voz de la IA:", self.cmb_voice)
        
        self.tabs.addTab(tab_ui, "Apariencia y Voz")
        
        # --- TAB 3: Sistema y Hardware ---
        tab_hw = QWidget()
        lay_hw = QFormLayout(tab_hw)
        lay_hw.setSpacing(15)
        lay_hw.setContentsMargins(15, 20, 15, 15)
        
        self.cmb_mic = QComboBox()
        self.cmb_mic.addItem("Micrófono Predeterminado del Sistema", "default")
        
        self.cmb_speaker = QComboBox()
        self.cmb_speaker.addItem("Altavoces Predeterminados del Sistema", "default")

        try:
            import sounddevice as sd
            devs = sd.query_devices()
            for idx, d in enumerate(devs):
                d_name = d.get('name', f'Dispositivo {idx}')
                if d.get('max_input_channels', 0) > 0:
                    self.cmb_mic.addItem(f"{idx}: {d_name}", idx)
                if d.get('max_output_channels', 0) > 0:
                    self.cmb_speaker.addItem(f"{idx}: {d_name}", idx)
        except Exception:
            pass

        lay_hw.addRow("Micrófono:", self.cmb_mic)
        lay_hw.addRow("Altavoces:", self.cmb_speaker)
        
        self.chk_gpu = QCheckBox("Habilitar Aceleración GPU (WebGL y UI)")
        lay_hw.addRow("", self.chk_gpu)
        
        self.tabs.addTab(tab_hw, "Hardware")
        
        # --- TAB 4: Conectividad ---
        tab_net = QWidget()
        lay_net = QFormLayout(tab_net)
        lay_net.setSpacing(15)
        lay_net.setContentsMargins(15, 20, 15, 15)
        
        lbl_tg = QLabel("Telegram Remote Control")
        lbl_tg.setStyleSheet("font-weight:bold; color:#38bdf8; font-size: 14px;")
        lay_net.addRow(lbl_tg)
        
        self.inp_telegram_token = QLineEdit()
        self.inp_telegram_token.setEchoMode(QLineEdit.EchoMode.Password)
        lay_net.addRow("Bot Token:", self.inp_telegram_token)
        
        self.inp_telegram_owner = QLineEdit()
        lay_net.addRow("Owner ID:", self.inp_telegram_owner)
        
        lbl_sp = QLabel("Spotify Integration")
        lbl_sp.setStyleSheet("font-weight:bold; color:#1db954; margin-top: 15px; font-size: 14px;")
        lay_net.addRow(lbl_sp)
        
        self.inp_spotify_id = QLineEdit()
        lay_net.addRow("Client ID:", self.inp_spotify_id)
        
        self.inp_spotify_secret = QLineEdit()
        self.inp_spotify_secret.setEchoMode(QLineEdit.EchoMode.Password)
        lay_net.addRow("Client Secret:", self.inp_spotify_secret)
        
        self.inp_spotify_uri = QLineEdit()
        self.inp_spotify_uri.setText("http://127.0.0.1:8888/callback")
        lay_net.addRow("Redirect URI:", self.inp_spotify_uri)
        
        self.tabs.addTab(tab_net, "Conectividad")
        
        # Botón Guardar Inferior
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.btn_save = QPushButton("Guardar Cambios")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setFixedSize(160, 40)
        self.btn_save.clicked.connect(self.save)
        bottom_layout.addWidget(self.btn_save)
        
        main_layout.addLayout(bottom_layout)
        
        self.load_settings()
        self.update_style()

    def load_settings(self):
        try:
            from memory.config_manager import load_api_keys
            cfg = load_api_keys()
            self.inp_user_name.setText(cfg.get("user_name", "Señor"))
            self.inp_ai_name.setText(cfg.get("ai_name", "JARVIS"))
            self.inp_gemini.setText(cfg.get("gemini_api_key", ""))
            self.inp_openrouter.setText(cfg.get("openrouter_api_key", ""))
            self.chk_gpu.setChecked(cfg.get("gpu_acceleration", False))
            
            self.inp_telegram_token.setText(cfg.get("telegram_bot_token", ""))
            self.inp_telegram_owner.setText(cfg.get("telegram_owner_id", ""))
            self.inp_spotify_id.setText(cfg.get("spotify_client_id", ""))
            self.inp_spotify_secret.setText(cfg.get("spotify_client_secret", ""))
            self.inp_spotify_uri.setText(cfg.get("spotify_redirect_uri", "http://127.0.0.1:8888/callback"))
            
            theme = cfg.get("jarvis_theme", "white")
            idx = self.cmb_theme.findData(theme)
            if idx >= 0:
                self.cmb_theme.setCurrentIndex(idx)
                
            voice = cfg.get("jarvis_voice", "Aoede")
            idx_voice = self.cmb_voice.findData(voice)
            if idx_voice >= 0:
                self.cmb_voice.setCurrentIndex(idx_voice)

            mic_dev = cfg.get("mic_device", "default")
            idx_mic = self.cmb_mic.findData(mic_dev)
            if idx_mic >= 0:
                self.cmb_mic.setCurrentIndex(idx_mic)

            spk_dev = cfg.get("spk_device", "default")
            idx_spk = self.cmb_speaker.findData(spk_dev)
            if idx_spk >= 0:
                self.cmb_speaker.setCurrentIndex(idx_spk)
        except Exception:
            pass

    def save(self):
        try:
            from memory.config_manager import load_api_keys, save_api_keys
            from memory.memory_manager import update_memory 
            
            cfg = load_api_keys()
            cfg["user_name"] = self.inp_user_name.text().strip() or "Señor"
            cfg["ai_name"] = self.inp_ai_name.text().strip() or "JARVIS"
            cfg["gemini_api_key"] = self.inp_gemini.text().strip()
            cfg["openrouter_api_key"] = self.inp_openrouter.text().strip()
            
            cfg["jarvis_theme"] = self.cmb_theme.currentData()
            cfg["jarvis_voice"] = self.cmb_voice.currentData()
            cfg["mic_device"] = self.cmb_mic.currentData()
            cfg["spk_device"] = self.cmb_speaker.currentData()
            cfg["gpu_acceleration"] = self.chk_gpu.isChecked()
            
            cfg["telegram_bot_token"] = self.inp_telegram_token.text().strip()
            cfg["telegram_owner_id"] = self.inp_telegram_owner.text().strip()
            cfg["spotify_client_id"] = self.inp_spotify_id.text().strip()
            cfg["spotify_client_secret"] = self.inp_spotify_secret.text().strip()
            cfg["spotify_redirect_uri"] = self.inp_spotify_uri.text().strip()
            
            save_api_keys(cfg)
            apply_theme_tokens(cfg["jarvis_theme"])
            
            # --- Sobrescribir la memoria a largo plazo al instante ---
            try:
                update_memory({"identity": {"name": {"value": cfg["user_name"]}}})
            except Exception:
                pass
            # ----------------------------------------------------------------
            
            parent = self.parent()
            if parent:
                parent.update_theme_styles()
                if hasattr(parent, 'ui'):
                    parent.ui.load_names()
                    # Mágicamente actualizamos el título superior
                    ai_name_spaced = " ".join(list(parent.ui.ai_name)).upper()
                    parent.lbl_brand.setText(ai_name_spaced)
                
            QMessageBox.information(self, "Ajustes Guardados", "Configuración guardada correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def update_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #030811; 
                border: 1px solid {C_PRI};
                border-radius: 10px;
            }}
            QTabWidget::pane {{
                border: 1px solid #1e293b;
                border-radius: 8px;
                background: transparent;
            }}
            QTabBar::tab {{
                background: #0f172a;
                color: #94a3b8;
                padding: 10px 25px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid transparent;
                margin-right: 2px;
                font-weight: bold;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background: {C_PRI};
                color: #000000;
            }}
            QTabBar::tab:hover:!selected {{
                background: #1e293b;
                color: white;
            }}
            QLabel {{
                color: #e2e8f0;
                font-weight: bold;
                font-size: 13px;
                background: transparent;
            }}
            QLineEdit, QComboBox {{
                background: #060b14;
                border: 1px solid #1e293b;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {C_PRI};
            }}
            QCheckBox {{
                color: #e2e8f0;
                font-weight: bold;
                font-size: 13px;
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {C_PRI};
                border: 1px solid {C_PRI};
            }}
            QPushButton#btn_save {{
                background-color: #f1f5f9;
                color: black;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }}
            QPushButton#btn_save:hover {{
                background-color: white;
            }}
        """)
        self.btn_save.setObjectName("btn_save")


class VisionControlWorker(QThread):
    frame_ready = pyqtSignal(QPixmap)

    def __init__(self, mode="preview"):
        super().__init__()
        self.mode = mode  
        self._running = True
        self.prev_x, self.prev_y = 0, 0
        self.smoothing = 0.25  
        self.is_dragging = False

    def run(self):
        if not HAS_CV2:
            return
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            return

        hands = None
        if HAS_MEDIAPIPE and self.mode == "mouse_gesture":
            hands = mp.solutions.hands.Hands(
                static_image_mode=False, max_num_hands=1,
                min_detection_confidence=0.7, min_tracking_confidence=0.7
            )
            screen_w, screen_h = pyautogui.size() if HAS_PYAUTOGUI else (1920, 1080)

        while self._running:
            ret, frame = cap.read()
            if not ret: continue

            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape

            if hands and self.mode == "mouse_gesture" and HAS_PYAUTOGUI:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                        thumb_tip = hand_landmarks.landmark[4]
                        index_tip = hand_landmarks.landmark[8]

                        margin = 0.15
                        ix = np.interp(index_tip.x, [margin, 1.0 - margin], [0, screen_w])
                        iy = np.interp(index_tip.y, [margin, 1.0 - margin], [0, screen_h])

                        curr_x = self.prev_x + (ix - self.prev_x) * self.smoothing
                        curr_y = self.prev_y + (iy - self.prev_y) * self.smoothing
                        
                        pyautogui.moveTo(int(curr_x), int(curr_y))
                        self.prev_x, self.prev_y = curr_x, curr_y

                        p1 = np.array([thumb_tip.x * w, thumb_tip.y * h])
                        p2 = np.array([index_tip.x * w, index_tip.y * h])
                        if np.linalg.norm(p1 - p2) < 35:
                            if not self.is_dragging:
                                pyautogui.mouseDown()
                                self.is_dragging = True
                                cv2.circle(frame, (int(index_tip.x * w), int(index_tip.y * h)), 15, (0, 255, 0), -1)
                        else:
                            if self.is_dragging:
                                pyautogui.mouseUp()
                                self.is_dragging = False

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_img = QImage(rgb_image.data, w, h, w * c, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.frame_ready.emit(pixmap)

        if hands: hands.close()
        cap.release()

    def stop(self):
        self._running = False
        if self.is_dragging and HAS_PYAUTOGUI: pyautogui.mouseUp()
        self.wait()


class ImagePreviewDialog(QDialog):
    def __init__(self, image_path: str, prompt_text: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS - Generación de Imagen IA")
        self.resize(750, 750)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel(f"🎨 {prompt_text or os.path.basename(image_path)}")
        title.setWordWrap(True)
        title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {C_PRI}; background: transparent;")
        layout.addWidget(title)

        self.lbl_img = QLabel()
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_img.setStyleSheet("border: 1px solid rgba(255,255,255,0.25); border-radius: 14px; background: #030712;")

        pix = QPixmap(image_path)
        if not pix.isNull():
            self.lbl_img.setPixmap(pix.scaled(710, 620, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        layout.addWidget(self.lbl_img)

        bottom = QHBoxLayout()
        btn_open = QPushButton("📁 Abrir Ubicación")
        btn_close = QPushButton("✖️ Cerrar")

        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_open.clicked.connect(lambda: subprocess.Popen(f'explorer /select,"{image_path}"', shell=True))
        btn_close.clicked.connect(self.accept)

        bottom.addStretch()
        bottom.addWidget(btn_open)
        bottom.addWidget(btn_close)
        layout.addLayout(bottom)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #060b16;
                border: 2px solid {C_PRI};
                border-radius: 16px;
            }}
            QPushButton {{
                background-color: {C_PRI};
                color: black;
                font-weight: bold;
                padding: 10px 18px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: white;
            }}
        """)


class MainWindow(QMainWindow):
    _shutdown_sig = pyqtSignal()
    _update_text_sig = pyqtSignal(str)   
    _clear_text_sig = pyqtSignal()       
    _show_image_sig = pyqtSignal(str, str)
    _relock_license_sig = pyqtSignal(str)

    def __init__(self, ui, face_path=""):
        super().__init__()
        self.ui = ui
        self.ui._win = self
        self._show_image_sig.connect(self._safe_show_image_dialog)

        self.resize(800, 650)
        self.setMinimumSize(500, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAcceptDrops(True)

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)

        icon_path = Path(__file__).parent / "assets" / "jarvis_icono.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.header_container = QWidget(self.central_widget)
        header_bar = QHBoxLayout(self.header_container)
        header_bar.setContentsMargins(15, 8, 15, 8)

        ai_name_spaced = " ".join(list(self.ui.ai_name)).upper()
        self.lbl_brand = QLabel(ai_name_spaced)
        font = QFont("Century Gothic", 16, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 8)
        self.lbl_brand.setFont(font)
        header_bar.addWidget(self.lbl_brand)
        header_bar.addStretch()

        self.btn_mic_toggle = QPushButton()
        self.btn_camera_preview = QPushButton()
        
        self.camera_view_active = False

        if HAS_QTA:
            self.btn_mic_toggle.setIcon(qta.icon("fa5s.microphone", color="#FFFFFF"))
            self.btn_camera_preview.setIcon(qta.icon("fa5s.video", color="#64748b"))
        else:
            self.btn_mic_toggle.setText("🎤")
            self.btn_camera_preview.setText("📷")

        self.btn_mic_toggle.clicked.connect(self._toggle_mute)
        self.btn_camera_preview.clicked.connect(self._toggle_camera_preview)

        header_bar.addWidget(self.btn_mic_toggle)
        header_bar.addWidget(self.btn_camera_preview)

        self.btn_history = QPushButton()
        self.btn_settings = QPushButton()
        self.btn_play = QPushButton()
        self.btn_play.hide() 
        self.btn_min = QPushButton()
        self.btn_close = QPushButton()

        if HAS_QTA:
            self.btn_history.setIcon(qta.icon("fa5s.history", color=C_PRI_DIM))
        else:
            self.btn_history.setText("⏱")
            self.btn_play.setText("🔊")

        self.head_buttons = [
            (self.btn_history, "fa5s.history", self._open_history),
            (self.btn_settings, "fa5s.cog", self._open_settings),
            (self.btn_min, "fa5s.window-minimize", self.showMinimized),
            (self.btn_close, "fa5s.times", self.close)
        ]

        for btn, icon, cb in self.head_buttons:
            btn.setFixedSize(30, 30)
            btn.clicked.connect(cb)
            header_bar.addWidget(btn)

        self.orb = CustomParticleOrb(self.ui, self.central_widget)
        self.orb.lower()

        self.lbl_camera_view = QLabel(self.central_widget)
        self.lbl_camera_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_camera_view.setStyleSheet("QLabel { background: rgba(0, 0, 0, 0.75); border: 2px dashed #FFFFFF; border-radius: 14px; }")
        self.lbl_camera_view.hide()
        self.vision_worker = None

        self.txt_console = QTextEdit(self.central_widget)
        self.txt_console.setReadOnly(True)
        self.txt_console.setFrameShape(QTextEdit.Shape.NoFrame)
        self.txt_console.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.chat_input = ChatInputWidget(self.ui, self.central_widget)

        self._force_close = False
        self.tray_icon = None
        self._setup_tray_icon()

        self.update_theme_styles()
        self._drag_pos = None
        
        self._shutdown_sig.connect(self._handle_shutdown)
        self._update_text_sig.connect(self._safe_update_text)
        self._clear_text_sig.connect(self._safe_clear_text)
        self._relock_license_sig.connect(self._handle_relock_license)

    def _handle_relock_license(self, reason: str):
        try:
            self._force_close = True
            self.hide()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Licencia Revocada o Expirada", f"Tu acceso a JARVIS ha sido bloqueado:\n{reason}\n\nIngresa un nuevo código de uso válido para continuar.")
            from core.setup_wizard import ensure_api_keys_and_privacy
            from pathlib import Path
            cfg_path = Path(__file__).parent / "config" / "api_keys.json"
            ensure_api_keys_and_privacy(cfg_path)
        except Exception as e:
            print(f"[UI Relock] Error: {e}")
        finally:
            import os
            os._exit(0)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
        else: event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            filepath = urls[0].toLocalFile()
            self.ui.current_file = filepath
            self.ui.clear_jarvis_response()
            self.ui.stream_jarvis_chunk(f"📥 Archivo absorbido: {os.path.basename(filepath)}")
            if self.ui.on_text_command:
                self.ui.on_text_command(f"[DROPPED_FILE] path={filepath}")

    def update_theme_styles(self):
        self.central_widget.setStyleSheet(f"""
            QWidget#centralWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(18, 13, 4, 0.94),
                    stop:1 rgba(5, 4, 2, 0.95)
                );
                border: 2px solid {C_PRI};
                border-radius: 22px;
            }}
        """)

        self.lbl_brand.setStyleSheet(f"color: {C_PRI}; font-weight: bold; background: transparent;")

        for btn, icon, _ in self.head_buttons:
            if HAS_QTA: btn.setIcon(qta.icon(icon, color="#FFFFFF"))
            btn.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid rgba(255,255,255,0.25); border-radius: 15px; }} QPushButton:hover {{ background: rgba(255,255,255,0.15); border-color: #FFFFFF; }}")

        for btn in [self.btn_mic_toggle, self.btn_camera_preview]:
            btn.setFixedSize(32, 32)
            btn.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid rgba(255,255,255,0.25); border-radius: 16px; }} QPushButton:hover {{ background: rgba(255,255,255,0.15); border-color: #FFFFFF; }}")

        if getattr(self.ui, 'muted', False):
            if HAS_QTA: self.btn_mic_toggle.setIcon(qta.icon("fa5s.microphone-slash", color="#ff3b30"))
        else:
            if HAS_QTA: self.btn_mic_toggle.setIcon(qta.icon("fa5s.microphone", color="#FFFFFF"))

        if getattr(self, 'camera_view_active', False):
            if HAS_QTA: self.btn_camera_preview.setIcon(qta.icon("fa5s.video", color="#00d4ff"))
        else:
            if HAS_QTA: self.btn_camera_preview.setIcon(qta.icon("fa5s.video", color="#FFFFFF"))

        if hasattr(self, 'lbl_camera_view'):
            self.lbl_camera_view.setStyleSheet(f"QLabel {{ background: rgba(0, 0, 0, 0.75); border: 2px dashed {C_PRI}; border-radius: 14px; }}")

        self.txt_console.setStyleSheet(f"QTextEdit {{ color: {C_PRI}; font-weight: bold; font-size: 15px; background: transparent; }} QTextEdit QScrollBar:vertical {{ background: transparent; width: 6px; }} QTextEdit QScrollBar::handle:vertical {{ background: {C_PRI_DIM}; border-radius: 3px; }} QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {{ height: 0px; }}")

        self.chat_input.update_style()
        if hasattr(self, "orb"): self.orb.sync_theme()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        W, H = self.central_widget.width(), self.central_widget.height()
        self.header_container.setGeometry(0, 0, W, 45)

        chat_h, console_h, bottom_margin = 58, 90, 18
        self.chat_input.setGeometry(30, H - chat_h - bottom_margin, W - 60, chat_h)
        self.txt_console.setGeometry(30, H - chat_h - bottom_margin - console_h, W - 60, console_h)

        orb_y = 45
        self.orb.setGeometry(0, orb_y, W, H - chat_h - bottom_margin - console_h - 45)

        cam_w, cam_h = 240, 180
        if hasattr(self, 'lbl_camera_view'):
            self.lbl_camera_view.setGeometry(W - cam_w - 30, orb_y + 15, cam_w, cam_h)

        self.orb.lower()
        if hasattr(self, 'lbl_camera_view'): self.lbl_camera_view.raise_()
        self.txt_console.raise_()
        self.chat_input.raise_()

    def _open_settings(self):
        dialog = DeviceSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if self.ui.on_config_saved:
                from memory.config_manager import load_api_keys
                self.ui.on_config_saved(load_api_keys())
                
    def _open_history(self):
        dialog = HistoryDialog(self.ui, self)
        dialog.exec()

    def _toggle_mute(self):
        self.ui.muted = not self.ui.muted
        self.orb.set_state("MUTED" if self.ui.muted else "LISTENING")
        if HAS_QTA: self.btn_mic_toggle.setIcon(qta.icon("fa5s.microphone-slash" if self.ui.muted else "fa5s.microphone", color="#ff3b30" if self.ui.muted else C_PRI))
        if self.ui.muted:
            self.ui.stream_jarvis_chunk("🎤 Canal de escucha cerrado localmente. Modo silencioso activo.")
            if self.ui.on_stop_command: self.ui.on_stop_command()
        else:
            self.ui.stream_jarvis_chunk("🎤 Canal de audio abierto. Escuchando directivas.")

    def _toggle_camera_preview(self):
        self.camera_view_active = not self.camera_view_active
        if self.camera_view_active:
            self.vision_worker = VisionControlWorker(mode="preview")
            self.vision_worker.frame_ready.connect(self._update_camera_frame)
            self.vision_worker.start()
            self.lbl_camera_view.show()
            if HAS_QTA: self.btn_camera_preview.setIcon(qta.icon("fa5s.video", color="#00d4ff"))
            self.ui.stream_jarvis_chunk("📷 Visor de cámara desplegado. Listo para encuadrar objetos.")
        else:
            self._stop_vision_engine()
            if HAS_QTA: self.btn_camera_preview.setIcon(qta.icon("fa5s.video", color=C_PRI_DIM))
            self.ui.stream_jarvis_chunk("📷 Visor de cámara desactivado.")

    def _update_camera_frame(self, pixmap):
        if self.lbl_camera_view.isVisible():
            self.lbl_camera_view.setPixmap(pixmap.scaled(self.lbl_camera_view.width(), self.lbl_camera_view.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def _stop_vision_engine(self):
        if self.vision_worker:
            self.vision_worker.stop()
            self.vision_worker = None
        self.lbl_camera_view.hide()
        self.lbl_camera_view.clear()

    def _safe_show_image_dialog(self, image_path: str, prompt_text: str = ""):
        try:
            dlg = ImagePreviewDialog(image_path, prompt_text, self)
            dlg.exec()
        except Exception as e:
            print(f"[UI] Error desplegando vista previa de imagen: {e}")

    def _setup_tray_icon(self):
        from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QStyle
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = Path(__file__).parent / "assets" / "jarvis_icono.ico"
        if icon_path.exists(): self.tray_icon.setIcon(QIcon(str(icon_path)))
        else: self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        tray_menu = QMenu(self)
        show_action = tray_menu.addAction("Mostrar Asistente")
        show_action.triggered.connect(self.show_and_activate)
        mute_action = tray_menu.addAction("Silenciar/Escuchar")
        mute_action.triggered.connect(self._toggle_mute)
        tray_menu.addSeparator()
        exit_action = tray_menu.addAction("Salir")
        exit_action.triggered.connect(self._exit_application)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def show_and_activate(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _exit_application(self):
        self._force_close = True
        self.close()

    def _handle_shutdown(self):
        self._force_close = True
        self.close()

    def _on_tray_activated(self, reason):
        from PyQt6.QtWidgets import QSystemTrayIcon
        if reason in (QSystemTrayIcon.ActivationReason.DoubleClick, QSystemTrayIcon.ActivationReason.Trigger):
            if self.isVisible(): self.hide()
            else: self.show_and_activate()

    def closeEvent(self, event):
        if getattr(self, "_force_close", False): event.accept()
        else:
            event.ignore()
            self.hide()
            if hasattr(self, "tray_icon") and self.tray_icon.isVisible():
                from PyQt6.QtWidgets import QSystemTrayIcon
                self.tray_icon.showMessage(self.ui.ai_name, "Sigo activo en segundo plano.", QSystemTrayIcon.MessageIcon.Information, 2500)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    @pyqtSlot(str)
    def _safe_update_text(self, html: str):
        self.txt_console.setHtml(html)
        self.txt_console.moveCursor(QTextCursor.MoveOperation.End)

    @pyqtSlot()
    def _safe_clear_text(self):
        self.txt_console.setPlainText("")


class MockRoot:
    def __init__(self, qapp: QApplication):
        self.qapp = qapp
    def mainloop(self):
        sys.exit(self.qapp.exec())
    def after(self, ms: int, func):
        QTimer.singleShot(ms, func)


class JarvisUI:
    def __init__(self, face_path=""):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.root = MockRoot(self.app)

        self.muted = False
        self.current_file = ""

        self.on_text_command = None
        self.on_stop_command = None
        self.on_config_saved = None

        self.jarvis_response_buffer = ""
        self.full_chat_history = [] 
        
        self.user_name = "Señor"
        self.ai_name = "JARVIS"
        self.load_names()

        self._win = MainWindow(self, face_path)
        self._win.show()
        QTimer.singleShot(2000, self.ensure_startup_shortcut)

    def load_names(self):
        try:
            from memory.config_manager import load_api_keys
            cfg = load_api_keys()
            self.user_name = cfg.get("user_name", "Señor").strip() or "Señor"
            self.ai_name = cfg.get("ai_name", "JARVIS").strip() or "JARVIS"
        except:
            pass

    def wait_for_api_key(self):
        pass

    def write_log(self, text: str):
        if text.startswith("SYS: "):
            self.full_chat_history.append({"role": "sys", "text": text[5:].strip()})

    def set_state(self, state: str):
        try:
            if hasattr(self, '_win') and self._win and hasattr(self._win, 'orb') and self._win.orb:
                self._win.orb.set_state(state)
        except (AttributeError, RuntimeError):
            pass

    def set_audio_level(self, level: float):
        try:
            if hasattr(self, '_win') and self._win and hasattr(self._win, 'orb') and self._win.orb:
                self._win.orb.set_audio(level)
        except (AttributeError, RuntimeError):
            pass

    def clear_jarvis_response(self):
        if hasattr(self, 'jarvis_response_buffer') and self.jarvis_response_buffer:
            if not self.jarvis_response_buffer.startswith(f"{self.user_name}:"):
                self.full_chat_history.append({"role": "jarvis", "text": self.jarvis_response_buffer})
                
        self.jarvis_response_buffer = ""
        try:
            if hasattr(self, '_win') and self._win:
                self._win._clear_text_sig.emit()
        except (AttributeError, RuntimeError):
            pass

    def stream_jarvis_chunk(self, chunk: str):
        text = str(chunk or "").replace(f"{self.ai_name}:", "").strip()
        if text:
            if self.jarvis_response_buffer:
                self.jarvis_response_buffer += " " + text
            else:
                self.jarvis_response_buffer = text
            
            html = f"<b style='color:#38bdf8;'>{self.ai_name}:</b> {self.jarvis_response_buffer}"
            try:
                if hasattr(self, '_win') and self._win:
                    self._win._update_text_sig.emit(html)
            except (AttributeError, RuntimeError):
                pass

    def ensure_startup_shortcut(self):
        try:
            import subprocess
            appdata = os.getenv("APPDATA")
            if not appdata: return
            startup_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            shortcut_path = os.path.join(startup_dir, f"{self.ai_name}.lnk")
            current_dir = os.path.abspath(os.path.dirname(__file__))
            icon_path = os.path.join(current_dir, "assets", "jarvis_icono.ico")
            target_vbs = os.path.join(current_dir, "Iniciar JARVIS.vbs")
            if not os.path.exists(target_vbs):
                target_vbs = os.path.join(current_dir, "Iniciar JARVIS Beta.vbs")
            if not os.path.exists(target_vbs): return

            icon_line = f"$s.IconLocation='{icon_path}';" if os.path.exists(icon_path) else ""
            ps_cmd = (
                f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}');"
                f"$s.TargetPath='{target_vbs}';"
                f"$s.WorkingDirectory='{current_dir}';"
                f"{icon_line}"
                f"$s.Description='Lanzador Automatico de {self.ai_name}';"
                f"$s.Save()"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=False, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass