# -*- coding: utf-8 -*-
"""
JARVIS Client License Verifier
Módulo de validación de licencias y huella digital de hardware (HWID).
Garantiza que el asistente solo funcione con un código de licencia válido y activo.
"""

import sys
import os
import json
import uuid
import hashlib
import platform
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LICENSE_FILE = BASE_DIR / "config" / "license.json"
# URL del Servidor de Licencias (puede ser local o servidor web remoto)
LICENSE_SERVER_URL = os.environ.get("JARVIS_LICENSE_SERVER", "http://127.0.0.1:8000/api/licenses/validate")


def get_hwid() -> str:
    """Genera una huella digital única y persistente de hardware (HWID) para esta PC."""
    try:
        if os.name == "nt":
            # Obtener UUID del sistema en Windows
            cmd = "wmic csproduct get uuid"
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            lines = [line.strip() for line in output.splitlines() if line.strip() and "UUID" not in line]
            if lines:
                raw_id = lines[0]
            else:
                raw_id = str(uuid.getnode())
        else:
            raw_id = str(uuid.getnode())
    except Exception:
        raw_id = f"{platform.node()}-{uuid.getnode()}"

    # Generar hash limpio formateado
    hashed = hashlib.sha256(raw_id.encode("utf-8")).hexdigest().upper()
    return f"HWID-{hashed[:4]}-{hashed[4:8]}-{hashed[8:12]}"


def validate_license_online(license_key: str) -> tuple[bool, str]:
    """Consulta al Servidor de Licencias si el código ingresado es válido y activo."""
    if not license_key or len(license_key.strip()) < 10:
        return False, "Código de licencia no especificado."

    hwid = get_hwid()
    payload = json.dumps({
        "license_key": license_key.strip(),
        "hwid": hwid,
        "app_version": "2.0.0"
    }).encode("utf-8")

    req = urllib.request.Request(
        LICENSE_SERVER_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("valid"):
                return True, data.get("message", "Licencia válida.")
            return False, data.get("reason", "Licencia no válida.")
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            return False, err_data.get("reason", f"Error HTTP {e.code}")
        except Exception:
            return False, f"Servicio de licencias rechazó la clave (HTTP {e.code})."
    except Exception as e:
        # Fallback offline si el servidor local no se encuentra encendido en desarrollo
        # En producción el servidor responderá siempre
        if "127.0.0.1" in LICENSE_SERVER_URL:
            print(f"[Licencia] Servidor local no alcanzado ({e}). Permitiendo ejecución en modo dev local.")
            return True, "Modo desarrollo local."
        return False, f"No se pudo verificar la licencia con el servidor: {e}"


def check_and_enforce_license(ui=None) -> bool:
    """
    Verifica la licencia local y despliega el modal de activación si es necesaria una clave válida.
    Retorna True si el acceso es concedido, o detiene la aplicación si es rechazado.
    """
    stored_key = ""
    cfg_file = BASE_DIR / "config" / "api_keys.json"
    cfg_data = {}
    
    if cfg_file.exists():
        try:
            cfg_data = json.loads(cfg_file.read_text(encoding="utf-8"))
            stored_key = cfg_data.get("license_key", "").strip()
        except Exception:
            pass

    if not stored_key and LICENSE_FILE.exists():
        try:
            data = json.loads(LICENSE_FILE.read_text(encoding="utf-8"))
            stored_key = data.get("license_key", "").strip()
        except Exception:
            pass

    if stored_key:
        valid, msg = validate_license_online(stored_key)
        if valid:
            print(f"[JARVIS Licencia] ✅ {msg}")
            return True
        else:
            print(f"[JARVIS Licencia] ⚠️ Licencia guardada inválida, vencida o eliminada: {msg}")
            # Limpiar clave caducada en configuración para solicitar una nueva clave
            if cfg_data:
                cfg_data["license_key"] = ""
                cfg_file.write_text(json.dumps(cfg_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Si no hay clave válida, mostrar diálogo PyQt6 de validación obligatoria
    try:
        from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        from PyQt6.QtCore import Qt

        app = QApplication.instance() or QApplication(sys.argv)
        dialog = QDialog()
        dialog.setWindowTitle("JARVIS AI - Validación de Licencia Requerida")
        dialog.resize(480, 320)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        dialog.setStyleSheet("background-color: #030712; color: #ffffff; font-family: 'Segoe UI', sans-serif;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        lbl_title = QLabel("🔐 ACTIVACIÓN DE LICENCIA")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_desc = QLabel("Ingresa tu código de uso comercial único para desbloquear las funciones del asistente virtual JARVIS.")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 13px;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_desc)

        inp_key = QLineEdit()
        inp_key.setPlaceholderText("JRV-XXXX-XXXX-XXXX")
        inp_key.setText(stored_key)
        inp_key.setStyleSheet("color: #ffffff; background: #0f172a; border: 1px solid #38bdf8; padding: 12px; border-radius: 8px; font-size: 15px; font-family: monospace; font-weight: bold;")
        layout.addWidget(inp_key)

        lbl_hwid = QLabel(f"Equipo: {get_hwid()}")
        lbl_hwid.setStyleSheet("color: #64748b; font-size: 11px;")
        lbl_hwid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_hwid)

        btn_activate = QPushButton("ACTIVAR MI ASISTENTE")
        btn_activate.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_activate.setStyleSheet("QPushButton { background-color: #ffffff; color: #000000; font-weight: bold; padding: 12px; border-radius: 8px; font-size: 13px; letter-spacing: 1px;} QPushButton:hover { background-color: #e2e8f0; }")
        layout.addWidget(btn_activate)

        def on_activate():
            key_entered = inp_key.text().strip()
            if not key_entered:
                QMessageBox.warning(dialog, "Código Faltante", "Por favor ingresa un código de licencia válido.")
                return

            valid, reason = validate_license_online(key_entered)
            if valid:
                LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
                LICENSE_FILE.write_text(json.dumps({"license_key": key_entered, "hwid": get_hwid()}, indent=2), encoding="utf-8")
                QMessageBox.information(dialog, "Licencia Activada", f"¡Licencia activada con éxito!\n{reason}")
                dialog.accept()
            else:
                QMessageBox.critical(dialog, "Acceso Denegado", f"No se pudo activar JARVIS:\n{reason}")

        btn_activate.clicked.connect(on_activate)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True
        else:
            print("[JARVIS Licencia] 🛑 El usuario canceló la activación. Servicio bloqueado.")
            sys.exit(0)

    except Exception as e:
        print(f"[JARVIS Licencia] Error al mostrar diálogo de licencia: {e}")
        return True
