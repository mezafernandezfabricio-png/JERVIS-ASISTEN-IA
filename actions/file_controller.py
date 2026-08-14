# -*- coding: utf-8 -*-

import os
import ctypes
import shutil
from pathlib import Path


def _normalize_name(text: str) -> str:
    return str(text or "").strip().strip('"').strip("'").lower()


def _safe_search_paths() -> list[Path]:
    userprofile = Path(os.environ.get("USERPROFILE", str(Path.home())))

    return [
        userprofile / "Desktop",
        userprofile / "Downloads",
        userprofile / "Documents",
        userprofile / "Pictures",
        userprofile / "Videos",
        userprofile / "Music",
    ]


def _find_target(name_or_path: str) -> Path | None:
    raw = str(name_or_path or "").strip().strip('"').strip("'")
    if not raw:
        return None

    possible_path = Path(raw).expanduser()
    if possible_path.exists():
        return possible_path

    # 1. Búsqueda en el índice global de la PC
    try:
        from actions.open_app import search_pc_index, _realtime_disk_search
        matches = search_pc_index(raw, limit=5)
        for m in matches:
            p = Path(m.get("path", ""))
            if p.exists():
                return p

        # 2. Escaneo rápido en tiempo real
        disk_match = _realtime_disk_search(raw)
        if disk_match and disk_match.exists():
            return disk_match
    except Exception:
        pass

    # 3. Respaldo en carpetas comunes
    lowered = raw.lower()
    for base_path in _safe_search_paths():
        if not base_path.exists():
            continue
        try:
            for item in base_path.rglob("*"):
                try:
                    if lowered == item.name.lower() or lowered in item.name.lower():
                        return item
                except Exception:
                    continue
        except Exception:
            continue

    return None


def _restore_from_recycle_bin(target_name: str):
    import winshell

    lowered = target_name.lower()

    for item in winshell.recycle_bin():
        try:
            original_name = Path(item.original_filename()).name.lower()

            if lowered == original_name or lowered in original_name:
                item.undelete()
                return original_name

        except Exception:
            continue

    return None


def file_controller(parameters: dict, player=None) -> str:
    """
    Controlador avanzado de archivos:
    - eliminar
    - restaurar
    - vaciar papelera
    - eliminar definitivo
    """

    action = _normalize_name(parameters.get("action", ""))

    file_name = (
        parameters.get("file_name")
        or parameters.get("filename")
        or parameters.get("name")
        or parameters.get("target")
        or parameters.get("path")
        or ""
    )

    file_name = str(file_name).strip().strip('"').strip("'")

    # =========================================================
    # VACIAR PAPELERA
    # =========================================================

    if action in [
        "empty",
        "empty_bin",
        "vaciar",
        "vaciar_papelera",
        "empty_recycle_bin"
    ]:
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)

            msg = "He vaciado la papelera de reciclaje completamente."

            if player:
                player.write_log(f"🗑️ {msg}")

            return msg

        except Exception as e:
            return f"Error vaciando papelera: {e}"

    # =========================================================
    # RESTAURAR ARCHIVOS
    # =========================================================

    if action in [
        "restore",
        "restaurar",
        "recover",
        "undelete",
        "restore_file"
    ]:

        if not file_name:
            return "No especificaste qué archivo debo restaurar."

        try:
            restored = _restore_from_recycle_bin(file_name)

            if restored:
                msg = f"He restaurado '{restored}' desde la papelera."

                if player:
                    player.write_log(f"♻️ {msg}")

                return msg

            return f"No encontré '{file_name}' dentro de la papelera."

        except Exception as e:
            return f"Error restaurando archivo: {e}"

    # =========================================================
    # ELIMINAR Y ELIMINAR DEFINITIVAMENTE
    # =========================================================

    if action in [
        "delete",
        "eliminar",
        "borrar",
        "remove",
        "trash",
        "delete_file",
        "delete_folder",
        "force_delete",
        "delete_permanent",
        "eliminar_definitivo",
        "borrar_definitivo"
    ]:

        if not file_name:
            return "No recibí el nombre del archivo o carpeta que debo eliminar."

        confirm_val = parameters.get("confirm") or parameters.get("confirmar")
        is_confirmed = False
        if confirm_val is True:
            is_confirmed = True
        elif confirm_val is not None:
            c_str = str(confirm_val).lower().strip()
            negative_words = ["false", "no", "cancela", "cancelar", "abortar", "none", "0"]
            if c_str and not any(neg == c_str for neg in negative_words):
                is_confirmed = True

        target = _find_target(file_name)

        if not target:
            return f"No encontré ningún archivo o carpeta llamado '{file_name}' en tu PC."

        tipo = "carpeta" if target.is_dir() else "archivo"

        # SI NO HA CONFIRMADO: Solicitar confirmación con nombre y ruta exacta
        if not is_confirmed:
            msg = f"CONFIRMACION_REQUERIDA: He localizado la {tipo} '{target.name}' (Ubicación: '{target.parent}'). ¿Estás seguro de que deseas eliminarla por completo? Por favor responde 'sí' para proceder o 'no' para cancelar."
            if player:
                player.write_log(f"❓ {msg}")
            return msg

        # SI CONFIRMÓ: Eliminar SÍ O SÍ
        try:
            from send2trash import send2trash
            send2trash(str(target))
            msg = f"He movido la {tipo} '{target.name}' a la papelera de reciclaje exitosamente."
        except Exception:
            try:
                if target.is_dir():
                    shutil.rmtree(target, ignore_errors=True)
                else:
                    target.unlink(missing_ok=True)
                msg = f"He eliminado la {tipo} '{target.name}' definitivamente de tu PC."
            except Exception as e:
                return f"No se pudo eliminar '{target.name}': {e}"

        if player:
            player.write_log(f"🗑️ {msg}")

        return msg

    return (
        f"Acción '{action}' no soportada.\n"
        "Usa:\n"
        "- eliminar\n"
        "- restaurar\n"
        "- vaciar_papelera\n"
        "- eliminar_definitivo"
    )