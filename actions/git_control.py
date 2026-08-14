# -*- coding: utf-8 -*-
"""git_control.py — Control de repositorios Git y control de versiones local."""
import subprocess
import os
from pathlib import Path

def git_control(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Ejecuta comandos de Git de manera segura en el proyecto actual o directorio especificado:
    - status, branch, log, diff, pull, add, commit
    """
    parameters = parameters or {}
    command = parameters.get("command") or parameters.get("action") or "status"
    repo_path = parameters.get("repo_path") or parameters.get("path") or os.getcwd()
    message = parameters.get("message") or "Actualización automática de JARVIS"

    cmd_parts = ["git"]
    if command in ["status", "estado"]:
        cmd_parts.extend(["status", "--short"])
    elif command in ["branch", "ramas"]:
        cmd_parts.extend(["branch", "-a"])
    elif command in ["log", "historial"]:
        cmd_parts.extend(["log", "-n", "5", "--oneline"])
    elif command in ["diff", "cambios"]:
        cmd_parts.extend(["diff", "--stat"])
    elif command in ["pull"]:
        cmd_parts.extend(["pull"])
    elif command in ["commit"]:
        cmd_parts.extend(["commit", "-am", message])
    else:
        # Comando personalizado
        words = command.split()
        if words[0] == "git":
            words = words[1:]
        cmd_parts.extend(words)

    if player:
        player.write_log(f"🌿 Git: ejecutando 'git {' '.join(cmd_parts[1:])}'...")

    try:
        res = subprocess.run(
            cmd_parts,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        output = (res.stdout or res.stderr or "Comando ejecutado sin salida.").strip()
        return f"=== RESULTADO GIT ('{' '.join(cmd_parts)}') ===\n{output}"
    except FileNotFoundError:
        return "Error: Git no está instalado o no se encuentra en el PATH del sistema."
    except Exception as e:
        return f"Error al ejecutar comando Git: {e}"
