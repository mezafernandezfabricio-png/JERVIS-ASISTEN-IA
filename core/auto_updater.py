# -*- coding: utf-8 -*-
"""
XDS AI Assistant — Professional Remote Auto-Updater System (OTA)
Verifica actualizaciones obligatorias al iniciar y aplica parches en 1-Clic de forma bloqueante.
"""

import sys
import os
import json
import shutil
import urllib.request
import urllib.error
import subprocess
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = BASE_DIR / "config" / "version.json"
DEFAULT_MANIFEST_URL = "https://raw.githubusercontent.com/mezafernandezfabricio-png/JERVIS-ASISTEN-IA/main/DIST_RELEASE_CLOUD/version.json"

def get_local_version_info() -> dict:
    if VERSION_FILE.exists():
        try:
            return json.loads(VERSION_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "app_name": "XDS AI Assistant",
        "version": "1.0.0",
        "update_url": DEFAULT_MANIFEST_URL,
        "changelog": "Versión comercial inicial."
    }

def check_remote_update(manifest_url: str = None) -> tuple[bool, dict | None]:
    local_info = get_local_version_info()
    url = manifest_url or local_info.get("update_url", DEFAULT_MANIFEST_URL)
    
    # 1. Intentar servidor remoto HTTP/HTTPS
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "XDS-Client/1.0"})
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            remote_info = json.loads(resp.read().decode("utf-8"))
            remote_ver = str(remote_info.get("version", "1.0.0")).strip()
            local_ver = str(local_info.get("version", "1.0.0")).strip()
            
            if remote_ver != local_ver:
                return True, remote_info
    except Exception as e:
        print(f"[XDS AutoUpdater] Verificación remota omitida (offline/servidor no publicado): {e}")

    # 2. Canal local de parches para pruebas / desarrollo local (DIST_RELEASE_CLOUD)
    try:
        local_cloud_manifest = BASE_DIR / "DIST_RELEASE_CLOUD" / "version.json"
        if local_cloud_manifest.exists():
            remote_info = json.loads(local_cloud_manifest.read_text(encoding="utf-8"))
            remote_ver = str(remote_info.get("version", "1.0.0")).strip()
            local_ver = str(local_info.get("version", "1.0.0")).strip()
            if remote_ver != local_ver:
                remote_info["exe_url"] = str((BASE_DIR / "DIST_RELEASE_CLOUD" / "XDS_AI.exe").resolve())
                return True, remote_info
    except Exception as e:
        print(f"[XDS AutoUpdater] Error en canal local de parches: {e}")
        
    return False, None

def show_mandatory_update_dialog(remote_info: dict) -> bool:
    """
    Despliega la ventana OBLIGATORIA de actualización en PyQt6.
    El cliente NO podrá entrar ni usar el asistente a menos que presione 'INSTALAR ACTUALIZACIÓN'.
    """
    try:
        from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
        from PyQt6.QtCore import Qt

        app = QApplication.instance() or QApplication(sys.argv)
        dialog = QDialog()
        dialog.setWindowTitle("XDS AI Assistant — Actualización Obligatoria Requerida")
        dialog.resize(520, 460)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        dialog.setStyleSheet("background-color: #030712; color: #ffffff; font-family: 'Segoe UI', sans-serif;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(14)

        lbl_title = QLabel("🚀 NUEVA ACTUALIZACIÓN OBLIGATORIA")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #38bdf8; letter-spacing: 1px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        local_ver = get_local_version_info().get("version", "1.0.0")
        remote_ver = remote_info.get("version", "1.0.1")

        lbl_sub = QLabel(f"Versión instalada: v{local_ver}  ➔  Nueva versión: v{remote_ver}")
        lbl_sub.setStyleSheet("font-size: 13px; color: #94a3b8; font-weight: 600;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        lbl_warn = QLabel("⚠️ Para continuar utilizando el asistente, debes instalar esta actualización.")
        lbl_warn.setStyleSheet("font-size: 12px; font-weight: bold; color: #f59e0b; background: rgba(245,158,11,0.1); border: 1px solid #f59e0b; padding: 8px; border-radius: 6px;")
        lbl_warn.setWordWrap(True)
        lbl_warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_warn)

        lbl_notes = QLabel("Novedades y Cambios Aplicados:")
        lbl_notes.setStyleSheet("font-size: 12px; font-weight: bold; color: #e2e8f0;")
        layout.addWidget(lbl_notes)

        txt_changelog = QTextEdit()
        txt_changelog.setReadOnly(True)
        txt_changelog.setPlainText(remote_info.get("changelog", "Mejoras de estabilidad, rendimiento y optimización del núcleo."))
        txt_changelog.setStyleSheet("background-color: #0b1329; color: #cbd5e1; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; font-size: 12px;")
        layout.addWidget(txt_changelog)

        btn_update = QPushButton("⚡ INSTALAR ACTUALIZACIÓN")
        btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_update.setStyleSheet("""
            QPushButton {
                background-color: #38bdf8;
                color: #000000;
                font-weight: bold;
                padding: 13px;
                border-radius: 8px;
                font-size: 15px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #7dd3fc;
            }
        """)
        layout.addWidget(btn_update)

        btn_exit = QPushButton("✖️ Salir sin Actualizar")
        btn_exit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exit.setStyleSheet("background: transparent; color: #ef4444; border: none; font-size: 12px; text-decoration: underline;")
        layout.addWidget(btn_exit)

        def on_do_update():
            btn_update.setEnabled(False)
            btn_update.setText("Descargando e instalando actualización...")
            app.processEvents()

            exe_name = os.path.basename(sys.executable) if getattr(sys, 'frozen', False) else "XDS_AI.exe"
            download_url = remote_info.get("exe_url") or remote_info.get("download_url")

            if not download_url:
                QMessageBox.critical(dialog, "Error de Servidor", "No se encontró el enlace de descarga de la actualización.")
                btn_update.setEnabled(True)
                btn_update.setText("⚡ INSTALAR ACTUALIZACIÓN")
                return

            try:
                temp_exe = BASE_DIR / "XDS_AI_Update.tmp"
                if download_url.startswith("http://") or download_url.startswith("https://"):
                    req_dl = urllib.request.Request(download_url, headers={"User-Agent": "XDS-Client/1.0"})
                    with urllib.request.urlopen(req_dl, timeout=45) as resp, open(temp_exe, "wb") as f_out:
                        shutil.copyfileobj(resp, f_out)
                else:
                    shutil.copy2(download_url, temp_exe)

                # Script BATCH ejecutable para reemplazar archivos y reiniciar
                bat_path = BASE_DIR / "update_xds.bat"
                bat_content = f"""@echo off
title Actualizando XDS AI Assistant...
color 0A
cls
echo [XDS AI] Instalando la nueva version...
timeout /t 2 /nobreak > NUL
taskkill /f /im "{exe_name}" > NUL 2>&1

echo [XDS AI] Reemplazando nucleo ejecutable...
move /y "{temp_exe.name}" "{exe_name}"

echo [XDS AI] Actualizacion completada con exito.
"""
                bat_path.write_text(bat_content, encoding="utf-8")

                # Guardar nuevo version.json
                new_ver_info = {
                    "app_name": "XDS AI Assistant",
                    "version": remote_ver,
                    "release_date": remote_info.get("release_date", ""),
                    "update_url": remote_info.get("update_url", DEFAULT_MANIFEST_URL),
                    "changelog": remote_info.get("changelog", "")
                }
                VERSION_FILE.write_text(json.dumps(new_ver_info, indent=4, ensure_ascii=False), encoding="utf-8")

                with open(bat_path, "a", encoding="utf-8") as f_bat:
                    f_bat.write(f"\necho Reiniciando XDS AI Assistant...\nstart \"\" \"{exe_name}\"\ndel \"%~f0\"\n")

                subprocess.Popen([str(bat_path)], shell=True, cwd=BASE_DIR)
                sys.exit(0)

            except Exception as ex:
                QMessageBox.critical(dialog, "Fallo al Actualizar", f"No se pudo descargar la actualización:\n{ex}")
                btn_update.setEnabled(True)
                btn_update.setText("⚡ INSTALAR ACTUALIZACIÓN")

        def on_exit():
            sys.exit(0)

        btn_update.clicked.connect(on_do_update)
        btn_exit.clicked.connect(on_exit)

        res = dialog.exec()
        if res != QDialog.DialogCode.Accepted:
            sys.exit(0)

        return True

    except Exception as e:
        print(f"[XDS AutoUpdater] Error en actualización obligatoria: {e}")
        return False

def enforce_mandatory_update_check():
    """
    Comprobación síncrona bloqueante al iniciar XDS AI.
    Si hay una actualización, el cliente DEBE instalarla antes de poder entrar.
    """
    has_update, remote_info = check_remote_update()
    if has_update and remote_info:
        show_mandatory_update_dialog(remote_info)

def check_for_updates_background():
    """Ejecuta verificación periódica en segundo plano."""
    def run_check():
        has_update, remote_info = check_remote_update()
        if has_update and remote_info:
            from PyQt6.QtCore import QMetaObject, Qt
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                QMetaObject.invokeMethod(app, lambda: show_mandatory_update_dialog(remote_info), Qt.ConnectionType.QueuedConnection)

    t = threading.Thread(target=run_check, daemon=True)
    t.start()
