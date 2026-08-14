# core/setup_wizard.py
# -*- coding: utf-8 -*-
import sys
import json
import webbrowser
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox, QWidget
from PyQt6.QtCore import Qt

def ensure_api_keys_and_privacy(config_path: Path):
    """
    Despliega la ventana de Onboarding inicial si faltan las claves, 
    nombres de personalización o si no se han aceptado los términos de privacidad.
    """
    cfg = {}
    if config_path.exists():
        try: 
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception: 
            pass
            
    gemini = cfg.get("gemini_api_key", "").strip()
    openrouter = cfg.get("openrouter_api_key", "").strip()
    privacidad_aceptada = cfg.get("privacy_accepted", False)
    user_name = cfg.get("user_name", "").strip()
    ai_name = cfg.get("ai_name", "").strip()
            
    if gemini and privacidad_aceptada and user_name and ai_name:
        return 
                
    app = QApplication.instance() or QApplication(sys.argv)
    dialog = QDialog()
    dialog.setWindowTitle("XDS AI Assistant - Inicialización y Personalización")
    dialog.resize(550, 650)
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    dialog.setStyleSheet("background-color: #030811; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;")
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(40, 20, 40, 20)
    layout.setSpacing(10)
            
    lbl_title = QLabel("X D S   A I")
    lbl_title.setStyleSheet("color: #ffffff; font-size: 28px; font-weight: bold; letter-spacing: 5px;")
    lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(lbl_title)
    
    lbl_creator = QLabel("by Xdata Security")
    lbl_creator.setStyleSheet("color: #38bdf8; font-size: 13px; font-weight: 600; letter-spacing: 2px;")
    lbl_creator.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(lbl_creator)
    
    lbl_info = QLabel("Bienvenido. Para activar las redes neuronales de XDS AI, debes configurar tus accesos seguros y personalizar el sistema.")
    lbl_info.setWordWrap(True)
    lbl_info.setStyleSheet("font-size: 13px; color: #e2e8f0; text-align: center;")
    lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(lbl_info)
    
    form_container = QWidget()
    form_container.setStyleSheet("background-color: #0b1221; border-radius: 12px; border: 1px solid #334155;")
    form_layout = QVBoxLayout(form_container)
    form_layout.setContentsMargins(20, 20, 20, 20)
    form_layout.setSpacing(8)
    
    # API Keys
    lbl_keys = QLabel("🔑 CONEXIÓN NEURONAL")
    lbl_keys.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px; margin-bottom: 5px;")
    form_layout.addWidget(lbl_keys)

    btn_link_gemini = QPushButton("Obtener Gemini API Key (Gratis)")
    btn_link_gemini.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_link_gemini.setStyleSheet("color: #ffffff; background: transparent; text-align: left; text-decoration: underline; border: none; padding: 0; font-weight: 600;")
    btn_link_gemini.clicked.connect(lambda: webbrowser.open("https://aistudio.google.com/app/apikey"))
    form_layout.addWidget(btn_link_gemini)

    inp_gemini = QLineEdit()
    inp_gemini.setPlaceholderText("Pega tu llave de Gemini aquí...")
    inp_gemini.setText(gemini)
    inp_gemini.setEchoMode(QLineEdit.EchoMode.Password)
    inp_gemini.setStyleSheet("color: #ffffff; background: #0f172a; border: 1px solid #475569; padding: 10px; border-radius: 6px; margin-bottom: 5px; font-size: 13px;")
    form_layout.addWidget(inp_gemini)
            
    btn_link_or = QPushButton("Obtener OpenRouter API Key")
    btn_link_or.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_link_or.setStyleSheet("color: #38bdf8; background: transparent; text-align: left; text-decoration: underline; border: none; padding: 0; font-weight: 600;")
    btn_link_or.clicked.connect(lambda: webbrowser.open("https://openrouter.ai/keys"))
    form_layout.addWidget(btn_link_or)

    inp_openrouter = QLineEdit()
    inp_openrouter.setPlaceholderText("Pega tu llave de OpenRouter aquí...")
    inp_openrouter.setText(openrouter)
    inp_openrouter.setEchoMode(QLineEdit.EchoMode.Password)
    inp_openrouter.setStyleSheet("color: #ffffff; background: #0f172a; border: 1px solid #475569; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 13px;")
    form_layout.addWidget(inp_openrouter)

    # Personalización
    lbl_pers = QLabel("👤 PERSONALIZACIÓN")
    lbl_pers.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px; margin-bottom: 5px;")
    form_layout.addWidget(lbl_pers)

    inp_user_name = QLineEdit()
    inp_user_name.setPlaceholderText("¿Cómo quieres que te llame la IA? (Ej: Señor X)")
    inp_user_name.setText(user_name)
    inp_user_name.setStyleSheet("color: #ffffff; background: #0f172a; border: 1px solid #475569; padding: 10px; border-radius: 6px; margin-bottom: 5px; font-size: 13px;")
    form_layout.addWidget(inp_user_name)

    inp_ai_name = QLineEdit()
    inp_ai_name.setPlaceholderText("¿Cómo se llamará tu asistente? (Ej: XDS)")
    inp_ai_name.setText(ai_name or "XDS")
    inp_ai_name.setStyleSheet("color: #ffffff; background: #0f172a; border: 1px solid #475569; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 13px;")
    form_layout.addWidget(inp_ai_name)

    # Código de Uso Único / Licencia Comercial Firebase
    lbl_lic = QLabel("🛡️ CÓDIGO DE USO ÚNICO (LICENCIA COMERCIAL)")
    lbl_lic.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 14px; margin-bottom: 5px;")
    form_layout.addWidget(lbl_lic)

    license_key_saved = cfg.get("license_key", "").strip()
    inp_license_key = QLineEdit()
    inp_license_key.setPlaceholderText("JRV-XXXX-XXXX-XXXX")
    inp_license_key.setText(license_key_saved)
    inp_license_key.setStyleSheet("color: #38bdf8; background: #0f172a; border: 1px solid #38bdf8; padding: 10px; border-radius: 6px; font-family: monospace; font-weight: bold; font-size: 14px;")
    form_layout.addWidget(inp_license_key)
    
    layout.addWidget(form_container)
    
    chk_privacy = QCheckBox(" Acepto que el asistente procese comandos de voz y analice la pantalla.")
    chk_privacy.setStyleSheet("color: #e2e8f0; font-size: 11px; margin-top: 5px;")
    layout.addWidget(chk_privacy)

    layout.addStretch()

    btn_save = QPushButton("INICIAR SISTEMA")
    btn_save.setStyleSheet("QPushButton { background-color: #ffffff; color: #000000; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 14px; letter-spacing: 2px;} QPushButton:hover { background-color: #e2e8f0; }")
    btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
    layout.addWidget(btn_save)
            
    def on_save():
        g = inp_gemini.text().strip()
        o = inp_openrouter.text().strip()
        un = inp_user_name.text().strip()
        an = inp_ai_name.text().strip()
        lk = inp_license_key.text().strip()

        if not g:
            QMessageBox.warning(dialog, "Acceso Denegado", "La clave de Gemini API es obligatoria para encender el núcleo.")
            return
        if not un or not an:
            QMessageBox.warning(dialog, "Faltan Datos", "Por favor, ingresa tu nombre y el nombre que deseas darle a la IA.")
            return
        if not lk:
            QMessageBox.warning(dialog, "Licencia Faltante", "Por favor ingresa tu Código de Uso Único (Licencia Comercial).")
            return

        # Validar la Licencia con el Servidor Firebase
        try:
            from core.firebase_license import validate_firebase_license
            valid_lic, reason_lic = validate_firebase_license(lk)
            if not valid_lic:
                QMessageBox.critical(dialog, "Licencia Rechazada", f"No se pudo activar el asistente:\n{reason_lic}")
                return
        except Exception as e:
            print(f"[Licencia] Error de verificación: {e}")

        if not chk_privacy.isChecked():
            QMessageBox.warning(dialog, "Protocolo de Seguridad", "Debe aceptar los términos de privacidad.")
            return

        cfg["gemini_api_key"] = g
        cfg["openrouter_api_key"] = o
        cfg["user_name"] = un
        cfg["ai_name"] = an
        cfg["license_key"] = lk
        cfg["privacy_accepted"] = True
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(cfg, indent=4, ensure_ascii=False), encoding="utf-8")

        try:
            lic_path = config_path.parent / "license.json"
            lic_path.write_text(json.dumps({"license_key": lk}, indent=4, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

        dialog.accept()
                
    btn_save.clicked.connect(on_save)
    
    if dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)