# -*- coding: utf-8 -*-

import os
from pathlib import Path
from actions.open_app import search_pc_index, _get_all_drives, _should_skip_dir

def file_locator(parameters: dict, player=None, speak=None) -> str:
    """
    Busca archivos específicos en toda la PC del usuario por nombre o extensión.
    """
    nombre_archivo = str(parameters.get("nombre") or parameters.get("query") or "").lower().strip()
    extension = str(parameters.get("extension") or "").lower().strip()
    if extension and not extension.startswith("."):
        extension = f".{extension}"

    if player:
        player.write_log(f"🔎 Escaneando la PC en busca de: '{nombre_archivo}' {extension}...")

    resultados_encontrados = []
    limite_resultados = 15
    vistas = set()

    # 1. Búsqueda rápida en el índice global
    query_search = nombre_archivo if nombre_archivo else extension
    if query_search:
        matches = search_pc_index(query_search, limit=50)
        for m in matches:
            path_str = m.get("path", "")
            ext_str = m.get("ext", "").lower()
            name_str = m.get("name", "").lower()

            if path_str and path_str.lower() not in vistas:
                if extension and not ext_str.endswith(extension):
                    continue
                if nombre_archivo and nombre_archivo not in name_str and nombre_archivo not in path_str.lower():
                    continue

                vistas.add(path_str.lower())
                resultados_encontrados.append(path_str)
                if len(resultados_encontrados) >= limite_resultados:
                    break

    # 2. Escaneo de respaldo en tiempo real en todos los discos si no se hallaron suficientes
    if len(resultados_encontrados) < limite_resultados:
        for drive in _get_all_drives():
            try:
                for root, dirs, files in os.walk(drive):
                    # Omitir carpetas del sistema
                    dirs[:] = [d for d in dirs if not _should_skip_dir(d, os.path.join(root, d))]
                    
                    # Limitar profundidad
                    if root.count(os.sep) > 5:
                        del dirs[:]
                        continue

                    for file in files:
                        file_lower = file.lower()
                        match = False
                        if nombre_archivo and nombre_archivo in file_lower:
                            match = True
                        if extension and file_lower.endswith(extension):
                            match = True

                        if match:
                            full_p = os.path.join(root, file)
                            if full_p.lower() not in vistas:
                                vistas.add(full_p.lower())
                                resultados_encontrados.append(full_p)
                                if len(resultados_encontrados) >= limite_resultados:
                                    break
                    if len(resultados_encontrados) >= limite_resultados:
                        break
            except Exception:
                continue

    if not resultados_encontrados:
        return f"No encontré ningún archivo que coincida con ('{nombre_archivo}' / '{extension}') en los discos de tu PC."

    lista_archivos = "\n".join(resultados_encontrados)

    return (
        f"ARCHIVOS ENCONTRADOS EN LA PC:\n{lista_archivos}\n\n"
        "INSTRUCCIÓN PARA JARVIS: Informa al usuario que encontraste estos archivos en el sistema "
        "y pregúntale si desea abrir, copiar o eliminar alguno de ellos."
    )