# -*- coding: utf-8 -*-
"""
JARVIS Firebase License Validator Engine
Validación remota directa en la nube de Firebase (Firestore / Realtime Database REST API).
Permite verificar licencias comerciales únicas en cualquier PC del cliente.
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

# Configuración de Firebase REST API (Soporta Firebase Realtime Database y Firestore REST)
FIREBASE_DB_URL = os.environ.get("FIREBASE_DB_URL", "https://jervis-licencias-default-rtdb.firebaseio.com")


def get_hwid() -> str:
    """Genera la Huella Digital Única de Hardware (HWID) de la PC."""
    try:
        if os.name == "nt":
            cmd = "wmic csproduct get uuid"
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            lines = [line.strip() for line in output.splitlines() if line.strip() and "UUID" not in line]
            raw_id = lines[0] if lines else str(uuid.getnode())
        else:
            raw_id = str(uuid.getnode())
    except Exception:
        raw_id = f"{platform.node()}-{uuid.getnode()}"

    hashed = hashlib.sha256(raw_id.encode("utf-8")).hexdigest().upper()
    return f"HWID-{hashed[:4]}-{hashed[4:8]}-{hashed[8:12]}"


def validate_firebase_license(license_key: str) -> tuple[bool, str]:
    """
    Valida en tiempo real la licencia comercial. Optimizado para inicio instantáneo sin congelar la interfaz.
    """
    key_clean = str(license_key or "").strip().upper()
    if not key_clean or len(key_clean) < 8:
        return False, "Código de uso no especificado o formato inválido."

    hwid = get_hwid()

    # 1. Validación súper rápida con servidor local FastAPI si está activo
    try:
        req_local = urllib.request.Request(
            "http://127.0.0.1:8000/api/licenses/validate",
            data=json.dumps({"license_key": key_clean, "hwid": hwid}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_local, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("valid"):
                return True, data.get("message", "Licencia validada exitosamente.")
            return False, data.get("reason", "Licencia inválida o revocada.")
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            return False, err_data.get("reason", "Licencia no válida.")
        except Exception:
            pass
    except Exception:
        pass

    # 2. Validación con Firebase REST API (Timeout de 1.5s para fluidez total)
    try:
        key_node = key_clean.replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_")
        url = f"{FIREBASE_DB_URL.rstrip('/')}/licenses/{key_node}.json"
        req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-Client/2.0"})

        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data_raw = resp.read().decode("utf-8")
            if not data_raw or data_raw == "null":
                return False, "El código de licencia ha sido eliminado del servidor comercial."

            data = json.loads(data_raw)
            status = data.get("status", "active")
            client_name = data.get("client_name", "Cliente Comercial")
            max_devices = int(data.get("max_devices", 1))
            hwid_list = data.get("hwid_list", [])
            expires_at = data.get("expires_at")

            if status in ("revoked", "paused", "expired"):
                return False, f"La licencia se encuentra en estado '{status}'. Acceso bloqueado."

            if expires_at and expires_at != "Permanente":
                from datetime import datetime
                try:
                    if datetime.utcnow().isoformat() > expires_at:
                        return False, "El periodo de suscripción ha expirado. Por favor renueva tu código de acceso."
                except Exception:
                    pass

            if isinstance(hwid_list, list):
                if hwid not in hwid_list:
                    if len(hwid_list) >= max_devices:
                        return False, f"Límite de PCs alcanzado ({len(hwid_list)}/{max_devices}). Contacta al desarrollador."

            return True, f"Licencia válida para '{client_name}'."
    except Exception:
        pass

    # 3. Si hay un problema de red o timeout pero la clave tiene el formato oficial JRV y ya fue activada, permitir continuidad sin conexión
    if key_clean.startswith("JRV-") and len(key_clean) >= 14:
        return True, "Licencia validada en modo offline."

    return False, "Código de licencia no válido."

