# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess
import urllib.parse
import webbrowser
from pathlib import Path


def _resolve_best_winget_id(query: str) -> str | None:
    try:
        proc = subprocess.run(
            ["winget", "search", query],
            capture_output=True, text=True, timeout=20,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        if proc.returncode != 0 or not proc.stdout:
            return None

        lines = proc.stdout.split("\n")
        candidates = []
        for line in lines:
            line_str = line.strip()
            if len(line_str) > 20 and "---" not in line_str and "Nombre" not in line_str and "Name" not in line_str:
                parts = re.split(r'\s{2,}', line_str)
                if len(parts) >= 2:
                    name, pkg_id = parts[0], parts[1]
                    if "." in pkg_id or "-" in pkg_id:
                        candidates.append((name, pkg_id))

        if candidates:
            # Buscar coincidencia exacta por ID o nombre
            q_norm = query.lower().strip()
            for name, pkg_id in candidates:
                if q_norm in name.lower() or q_norm in pkg_id.lower():
                    return pkg_id
            return candidates[0][1]
    except Exception:
        pass
    return None


def _install_local_file(file_path: Path) -> tuple[bool, str]:
    if not file_path.exists():
        return False, f"El archivo local '{file_path}' no existe."

    ext = file_path.suffix.lower()
    try:
        if ext == ".msi":
            cmd = f'msiexec /i "{file_path}" /qn /norestart'
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
            if proc.returncode in [0, 1605, 3010]:
                return True, f"Instalado exitosamente el paquete MSI local '{file_path.name}'."
        elif ext in [".exe", ".bat", ".cmd"]:
            cmd = f'"{file_path}" /S /silent /quiet /VERYSILENT /NORESTART'
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
            if proc.returncode in [0, 3010]:
                return True, f"Ejecutado e instalado el archivo ejecutable '{file_path.name}'."
    except Exception as e:
        return False, f"Error al ejecutar instalador local '{file_path.name}': {e}"

    return False, f"No se pudo instalar el archivo '{file_path.name}'."


def software_installer(parameters: dict, player=None, speak=None) -> str:
    programas_param = parameters.get("programas") or parameters.get("software") or parameters.get("name") or []

    if isinstance(programas_param, str):
        programas = [programas_param]
    else:
        programas = list(programas_param)

    if not programas:
        return "No especificaste qué programa o aplicación debo instalar."

    resultados = []

    for software in programas:
        software_str = str(software).strip().strip('"').strip("'")
        if not software_str:
            continue

        if player:
            player.write_log(f"📦 Iniciando instalador para: '{software_str}'...")

        # 0. Comprobar si es un archivo local (.exe, .msi)
        p_local = Path(software_str).expanduser()
        if p_local.exists() and p_local.suffix.lower() in [".exe", ".msi", ".bat"]:
            ok, msg = _install_local_file(p_local)
            resultados.append(f"{'✅' if ok else '❌'} {msg}")
            continue

        instalado = False

        # 1. Intentar instalación directa por Winget ID
        try:
            cmd = ["winget", "install", "--id", software_str, "--silent", "--accept-package-agreements", "--accept-source-agreements"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            salida = proc.stdout.lower()

            if proc.returncode == 0 or "already installed" in salida or "ya está instalado" in salida:
                resultados.append(f"✅ '{software_str}' fue instalado correctamente mediante Winget.")
                instalado = True
        except Exception:
            pass

        # 2. Resolución de ID de Winget si el nombre era genérico
        if not instalado:
            best_id = _resolve_best_winget_id(software_str)
            if best_id:
                if player:
                    player.write_log(f"🔎 ID de Winget resuelto: {best_id}. Instalando en segundo plano...")
                try:
                    cmd = ["winget", "install", "--id", best_id, "--silent", "--accept-package-agreements", "--accept-source-agreements"]
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
                    salida = proc.stdout.lower()

                    if proc.returncode == 0 or "already installed" in salida or "ya está instalado" in salida:
                        resultados.append(f"✅ '{software_str}' (ID: {best_id}) fue instalado con éxito vía Winget.")
                        instalado = True
                except Exception:
                    pass

        # 3. Intento genérico con Winget por nombre
        if not instalado:
            try:
                cmd = ["winget", "install", "--name", software_str, "--silent", "--accept-package-agreements", "--accept-source-agreements"]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
                salida = proc.stdout.lower()

                if proc.returncode == 0 or "already installed" in salida or "ya está instalado" in salida:
                    resultados.append(f"✅ '{software_str}' fue instalado mediante Winget por nombre.")
                    instalado = True
            except Exception:
                pass

        # 4. Motor Chocolatey
        if not instalado:
            try:
                proc_choco = subprocess.run(
                    ["choco", "install", software_str, "-y", "--no-progress"],
                    capture_output=True, text=True, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                )
                if proc_choco.returncode == 0:
                    resultados.append(f"✅ '{software_str}' instalado exitosamente vía Chocolatey.")
                    instalado = True
            except Exception:
                pass

        # 5. Reporte final si no se encontró paquete automático
        if not instalado:
            resultados.append(f"⚠️ No se encontró un paquete de instalación automática silenciosa para '{software_str}'.")

    reporte = "\n".join(resultados)
    if player:
        player.write_log(f"📋 {reporte}")

    return f"REPORTE DE INSTALACIÓN:\n{reporte}"