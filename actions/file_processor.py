# -*- coding: utf-8 -*-
"""file_processor.py — Procesador inteligente de archivos multiformato (PDF, DOCX, CSV, imágenes, texto)."""
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
API_FILE = BASE_DIR / "config" / "api_keys.json"

def _get_api_key() -> str:
    try:
        if API_FILE.exists():
            return json.loads(API_FILE.read_text(encoding="utf-8")).get("gemini_api_key", "")
    except Exception:
        pass
    return ""

def file_processor(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Procesa cualquier archivo que el usuario haya indicado o arrastrado a la interfaz.
    Soporta: PDFs, DOCX, TXT, CSV, JSON, imágenes, código, etc.
    """
    parameters = parameters or {}
    file_path = parameters.get("file_path") or ""
    action = (parameters.get("action") or "summarize").lower()
    instruction = parameters.get("instruction") or ""

    if not file_path and player and getattr(player, "current_file", ""):
        file_path = player.current_file

    if not file_path:
        return "Error: No se especificó la ruta del archivo a procesar."

    p = Path(file_path)
    if not p.exists():
        return f"Error: El archivo no existe en la ruta: {file_path}"

    ext = p.suffix.lower().lstrip(".")
    if player:
        player.write_log(f"📄 Procesando archivo ({p.name}) con acción '{action}'...")

    content = ""
    try:
        if ext in ["txt", "py", "html", "json", "csv", "js", "css", "md", "xml", "log", "yaml", "yml", "ini"]:
            try:
                content = p.read_text(encoding="utf-8")
            except Exception:
                content = p.read_bytes().decode("latin-1", errors="ignore")

        elif ext == "pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(p))
                content = "\n".join([page.extract_text() or "" for page in reader.pages[:20]])
            except ImportError:
                try:
                    import docx2txt
                    content = p.read_bytes().decode("latin-1", errors="ignore")[:10000]
                except Exception:
                    content = f"Archivo PDF: {p.name} ({p.stat().st_size} bytes)"

        elif ext in ["docx", "doc"]:
            try:
                import docx2txt
                content = docx2txt.process(str(p))
            except Exception:
                content = f"Documento Word: {p.name}"

        else:
            content = f"Archivo '{p.name}' de tipo '{ext}' (Tamaño: {p.stat().st_size} bytes)."

    except Exception as e:
        return f"Error al leer el contenido del archivo '{p.name}': {e}"

    api_key = _get_api_key()
    if not api_key:
        return f"Contenido extraído de {p.name} ({len(content)} caracteres):\n\n{content[:2000]}"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = (
            f"El usuario solicita procesar el archivo '{p.name}'. Acción requerida: '{action}'. "
            f"Instrucción adicional: '{instruction}'. "
            f"Contenido del archivo:\n\n{content[:25000]}\n\n"
            "Proporciona un resultado claro, conciso, útil y estructurado en español."
        )
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return resp.text.strip()
    except Exception as e:
        return f"Lectura completada. Error al procesar con IA: {e}"
