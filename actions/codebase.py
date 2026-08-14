# -*- coding: utf-8 -*-
"""codebase.py — Explorador y analizador de estructura de proyectos de código."""
import os
from pathlib import Path

def codebase(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Analiza la base de código del proyecto actual:
    - tree / structure: genera el árbol de archivos.
    - search: busca patrones en archivos de código.
    - stats: estadísticas de líneas de código y tipos de archivo.
    """
    parameters = parameters or {}
    action = (parameters.get("action") or "stats").lower()
    query = parameters.get("query") or parameters.get("pattern") or ""
    root_dir = Path(parameters.get("path") or os.getcwd())

    if player:
        player.write_log(f"📁 Analizando codebase ({action})...")

    exclude_dirs = {'.git', '.venv', '__pycache__', 'node_modules', 'dist', 'build', '.system_generated', 'backups'}

    if action in ["tree", "structure", "arbol"]:
        tree_lines = [f"Directorio raíz: {root_dir.name}/"]
        count = 0
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            rel = os.path.relpath(root, root_dir)
            level = 0 if rel == "." else rel.count(os.sep) + 1
            indent = "  " * level
            if rel != ".":
                tree_lines.append(f"{indent}📁 {os.path.basename(root)}/")
            for f in files:
                tree_lines.append(f"{indent}  📄 {f}")
                count += 1
                if count >= 80:
                    tree_lines.append(f"{indent}  ... [más archivos omitidos]")
                    break
            if count >= 80:
                break
        return "\n".join(tree_lines)

    elif action in ["search", "buscar"]:
        if not query:
            return "Error: Especifique 'query' para buscar en el código."
        matches = []
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                if f.endswith((".py", ".js", ".json", ".html", ".css", ".md", ".txt", ".iss")):
                    fp = Path(root) / f
                    try:
                        text = fp.read_text(encoding="utf-8", errors="ignore")
                        for idx, line in enumerate(text.splitlines(), 1):
                            if query.lower() in line.lower():
                                rel_path = fp.relative_to(root_dir)
                                matches.append(f"{rel_path}:{idx} -> {line.strip()[:100]}")
                                if len(matches) >= 20:
                                    break
                    except Exception:
                        pass
            if len(matches) >= 20:
                break
        if matches:
            return f"Coincidencias para '{query}' ({len(matches)}):\n" + "\n".join(matches)
        return f"No se encontraron coincidencias para '{query}' en el proyecto."

    else:
        # Stats
        ext_count = {}
        total_files = 0
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                ext = os.path.splitext(f)[1].lower() or "sin_extension"
                ext_count[ext] = ext_count.get(ext, 0) + 1
                total_files += 1
        summary = [f"=== ESTADÍSTICAS DEL PROYECTO: {root_dir.name} ===", f"Total de archivos: {total_files}"]
        for ext, cnt in sorted(ext_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            summary.append(f"  • {ext}: {cnt} archivos")
        return "\n".join(summary)
