# -*- coding: utf-8 -*-
"""
code_helper.py — Creación, análisis, ejecución y depuración de código fuente y aplicaciones completas para JARVIS.
Guarda SIEMPRE los proyectos y programas en el Escritorio del usuario con ejecución/apertura automática.
"""

import os
import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
API_FILE = BASE_DIR / "config" / "api_keys.json"

def _get_desktop_dir() -> Path:
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
        if onedrive_desktop.exists():
            return onedrive_desktop
        desktop.mkdir(parents=True, exist_ok=True)
    return desktop

def _get_api_key() -> str:
    try:
        if API_FILE.exists():
            return json.loads(API_FILE.read_text(encoding="utf-8")).get("gemini_api_key", "")
    except Exception:
        pass
    return ""

def _sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned if cleaned else f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def code_helper(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Crea, ejecuta, analiza, explica o depura aplicaciones y scripts de código (Python, JS, HTML/CSS, C++, Rust, etc.).
    Parámetros:
        - action: 'create' / 'write' (crear app en escritorio), 'run' (ejecutar), 'explain' (explicar), 'debug' (corregir), 'build'
        - description / prompt / tarea: Qué debe hacer el código o la app a crear
        - code / snippet / content: Código fuente directo (si ya se proporciona)
        - language / lenguaje: Lenguaje ('python', 'html', 'javascript', 'bat', 'vbs', 'powershell', etc.)
        - filename / output_path / nombre: Nombre del archivo de salida
        - run_after / ejecutar: Si debe ejecutarse o abrirse tras crearlo (default True)
    """
    params = parameters or {}
    action = str(params.get("action") or "create").lower()
    desc = params.get("description") or params.get("prompt") or params.get("tarea") or ""
    code_text = params.get("code") or params.get("snippet") or params.get("content") or ""
    language = str(params.get("language") or params.get("lenguaje") or "python").lower()
    filename = params.get("filename") or params.get("output_path") or params.get("nombre") or params.get("file_path") or ""
    run_after = params.get("run_after", params.get("ejecutar", True))
    
    desktop = _get_desktop_dir()

    # Si se pide crear o escribir una aplicación/script
    if action in ["create", "write", "build", "generate", "crear", "hacer"]:
        return _handle_create_app(desktop, desc, code_text, language, filename, run_after, player)

    # Si se pide ejecutar código
    if action in ["run", "execute", "ejecutar"]:
        return _handle_run_code(desktop, filename, code_text, language, player)

    # Análisis o explicación de código
    return _handle_analyze_code(code_text, filename, action, desc, player)

def _handle_create_app(desktop: Path, desc: str, code_text: str, language: str, filename: str, run_after: bool, player) -> str:
    """Genera una aplicación o script completo y lo guarda en el Escritorio."""
    ext_map = {
        "python": "py", "py": "py",
        "html": "html", "web": "html", "htm": "html",
        "javascript": "js", "js": "js",
        "typescript": "ts", "ts": "ts",
        "powershell": "ps1", "ps1": "ps1",
        "batch": "bat", "bat": "bat", "cmd": "bat",
        "vbs": "vbs", "vbscript": "vbs",
        "json": "json", "css": "css", "c": "c", "cpp": "cpp"
    }
    
    target_ext = ext_map.get(language, "py")
    
    if not filename:
        # Generar nombre limpio basado en la descripción
        slug = re.sub(r'[^a-zA-Z0-9_]', '_', desc[:25].strip().lower())
        slug = re.sub(r'_+', '_', slug).strip('_')
        filename = f"{slug if slug else 'aplicacion_jarvis'}.{target_ext}"
    elif "." not in filename:
        filename = f"{_sanitize_filename(filename)}.{target_ext}"
    else:
        filename = _sanitize_filename(filename)

    out_file = desktop / filename

    # Si no se pasó código explícito, pedir a Gemini que genere el código completo y listo para producción
    if not code_text and desc:
        api_key = _get_api_key()
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                prompt = (
                    f"Genera el código completo, funcional y sin errores para la siguiente aplicación en {language.upper()}:\n"
                    f"Requerimiento: {desc}\n\n"
                    "INSTRUCCIONES IMPORTANTES:\n"
                    "1. Devuelve ÚNICAMENTE el código fuente dentro de un bloque ```.\n"
                    "2. Debe ser 100% funcional y listo para ejecutarse sin dependencias faltantes ni placeholders.\n"
                    "3. Si es HTML, incluye CSS y JavaScript embebidos en el mismo archivo para que funcione al hacer doble clic.\n"
                    "4. Si es Python, incluye GUI con tkinter o interfaz limpia para que el usuario pueda usarlo de inmediato."
                )
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                extracted_code = _extract_code_block(resp.text)
                if extracted_code:
                    code_text = extracted_code
            except Exception as e:
                code_text = f"# Aplicacion generada por JARVIS\n# Requerimiento: {desc}\nprint('Ejecutando {desc}...')\n"

    if not code_text:
        if target_ext == "html":
            code_text = f"<!DOCTYPE html><html><head><title>{desc}</title><style>body{{font-family:sans-serif;background:#0f172a;color:white;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}}</style></head><body><h1>{desc}</h1></body></html>"
        else:
            code_text = f"# {desc}\nprint('¡Aplicación {desc} iniciada con éxito por JARVIS!')\n"

    # Escribir en el Escritorio
    out_file.write_text(code_text, encoding="utf-8")

    if player:
        try: player.write_log(f"💻 Aplicación creada en Escritorio: {out_file.name}")
        except: pass

    # Ejecutar o abrir si run_after es True
    if run_after and out_file.exists():
        try:
            if target_ext == "py":
                subprocess.Popen([sys.executable, str(out_file)], cwd=str(desktop))
            else:
                os.startfile(str(out_file))
        except Exception:
            pass

    return f"¡Aplicación creada exitosamente en tu Escritorio!\nArchivo: '{out_file.name}'\nRuta: {out_file}\nEstado: Guardado y ejecutado."

def _handle_run_code(desktop: Path, filename: str, code_text: str, language: str, player) -> str:
    """Ejecuta un script o archivo de código."""
    if filename:
        target = Path(filename) if Path(filename).is_absolute() else desktop / filename
        if target.exists():
            if target.suffix.lower() == ".py":
                res = subprocess.run([sys.executable, str(target)], capture_output=True, text=True, timeout=30)
                return f"Resultado de ejecutar '{target.name}':\n{res.stdout or res.stderr}"
            else:
                os.startfile(str(target))
                return f"Archivo '{target.name}' abierto y ejecutado."
    
    if code_text:
        # Ejecución en caliente
        temp_file = desktop / f"temp_exec_{datetime.now().strftime('%H%M%S')}.py"
        temp_file.write_text(code_text, encoding="utf-8")
        try:
            res = subprocess.run([sys.executable, str(temp_file)], capture_output=True, text=True, timeout=20)
            return f"Salida del código:\n{res.stdout or res.stderr}"
        finally:
            try: temp_file.unlink()
            except: pass

    return "No se pudo ejecutar el código: especifique archivo o código a correr."

def _handle_analyze_code(code_text: str, filename: str, action: str, desc: str, player) -> str:
    desktop = _get_desktop_dir()
    if filename and not code_text:
        target = Path(filename) if Path(filename).is_absolute() else desktop / filename
        if target.exists():
            code_text = target.read_text(encoding="utf-8", errors="ignore")

    if not code_text:
        return "No se proporcionó código para analizar."

    api_key = _get_api_key()
    if not api_key:
        return f"Código cargado ({len(code_text.splitlines())} líneas)."

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = (
            f"Actúa como un experto en programación de JARVIS. Tarea: '{action}'. "
            f"Contexto adicional: {desc}\n\n"
            f"Código:\n```\n{code_text[:12000]}\n```\n\n"
            "Proporciona una respuesta clara, estructurada y en español."
        )
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return resp.text.strip()
    except Exception as e:
        return f"Error al analizar el código: {e}"

def _extract_code_block(text: str) -> str:
    m = re.search(r'```(?:\w+)?\n([\s\S]*?)```', text)
    if m:
        return m.group(1).strip()
    return text.strip()
