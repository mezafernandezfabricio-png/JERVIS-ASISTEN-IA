# -*- coding: utf-8 -*-

import os
import re
import json
import time
import subprocess
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "config" / "pc_index.json"
_INDEX_LOCK = threading.Lock()
_SCANNING_IN_PROGRESS = False


def _home() -> Path:
    return Path(os.environ.get("USERPROFILE", str(Path.home())))


def _norm(text: str) -> str:
    text = str(text or "").lower().strip()
    text = text.replace("_", " ").replace("-", " ").replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def _save_index(data: list[dict]) -> None:
    with _INDEX_LOCK:
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        INDEX_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_index() -> list[dict]:
    if not INDEX_FILE.exists():
        return []
    try:
        with _INDEX_LOCK:
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _get_all_drives() -> list[Path]:
    drives = []
    if os.name == "nt":
        import string
        from ctypes import windll
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                p = Path(f"{letter}:\\")
                if p.exists():
                    drives.append(p)
            bitmask >>= 1
    if not drives:
        drives = [Path("C:\\")]
    return drives


def _known_locations() -> dict:
    h = _home()
    locs = {
        "escritorio": str(h / "Desktop"),
        "desktop": str(h / "Desktop"),
        "descargas": str(h / "Downloads"),
        "downloads": str(h / "Downloads"),
        "documentos": str(h / "Documents"),
        "documents": str(h / "Documents"),
        "imagenes": str(h / "Pictures"),
        "imágenes": str(h / "Pictures"),
        "fotos": str(h / "Pictures"),
        "pictures": str(h / "Pictures"),
        "videos": str(h / "Videos"),
        "vídeos": str(h / "Videos"),
        "musica": str(h / "Music"),
        "música": str(h / "Music"),
        "music": str(h / "Music"),
        "papelera": "shell:RecycleBinFolder",
        "recycle bin": "shell:RecycleBinFolder",
        "mi pc": "shell:MyComputerFolder",
        "este equipo": "shell:MyComputerFolder",
        "explorador": str(h),
        "explorador de archivos": str(h),
        "configuracion": "ms-settings:",
        "configuración": "ms-settings:",
        "settings": "ms-settings:",
        "panel de control": "control"
    }

    for drive in _get_all_drives():
        d_str = str(drive).lower().rstrip("\\")
        letter = d_str.replace(":", "")
        locs[f"disco {letter}"] = str(drive)
        locs[letter] = str(drive)
        locs[f"{letter}:"] = str(drive)

    return locs


def _allowed_file_exts() -> set[str]:
    return {
        ".lnk", ".url", ".exe", ".bat", ".cmd", ".msi", ".apk",
        ".txt", ".pdf", ".docx", ".xlsx", ".pptx", ".csv",
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico",
        ".mp4", ".mkv", ".avi", ".mov", ".wmv",
        ".mp3", ".wav", ".flac", ".ogg",
        ".html", ".css", ".js", ".py", ".json", ".xml",
        ".zip", ".rar", ".7z", ".iso"
    }


def _should_skip_dir(dir_name: str, full_path: str) -> bool:
    skip_names = {
        "$recycle.bin", "system volume information", "winsxs", "servicing",
        "node_modules", ".git", ".venv", "__pycache__", "package_cache",
        "msocache", "appdata\\local\\temp", "appdata\\local\\microsoft\\windows\\inetcache"
    }
    low_name = dir_name.lower()
    low_path = full_path.lower()

    if low_name in skip_names:
        return True
    if any(s in low_path for s in ["\\windows\\winsxs", "\\$recycle.bin", "\\node_modules"]):
        return True
    return False


def _looks_like_app_exe(path: Path) -> bool:
    name = _norm(path.stem)
    bad_words = [
        "unins", "uninstall", "setup", "install", "installer",
        "update", "updater", "crash", "helper", "service",
        "broker", "reporter", "runtime", "redist", "repair",
        "maintenancetool"
    ]

    if any(w in name for w in bad_words):
        return False

    return path.suffix.lower() == ".exe"


def _add_item(items: list[dict], seen: set[str], path: Path, item_type: str, source: str, score: int) -> None:
    try:
        p = str(path)
        p_lower = p.lower()
        if p_lower in seen:
            return

        seen.add(p_lower)
        items.append({
            "name": _norm(path.name),
            "stem": _norm(path.stem),
            "display_name": path.stem,
            "path": p,
            "type": item_type,
            "ext": path.suffix.lower(),
            "source": source,
            "score": score
        })
    except Exception:
        pass


def _scan_registry_apps(items: list[dict], seen: set[str]) -> None:
    try:
        import winreg
    except Exception:
        return

    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths")
    ]

    for hive, key_path in registry_paths:
        try:
            key = winreg.OpenKey(hive, key_path)
            num_keys = winreg.QueryInfoKey(key)[0]
            for i in range(num_keys):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    exe_path, _ = winreg.QueryValueEx(subkey, "")
                    if exe_path:
                        clean_path = str(exe_path).strip('"')
                        p = Path(clean_path)
                        if p.exists():
                            _add_item(items, seen, p, "app", "registry_app_paths", 120)
                except Exception:
                    continue
        except Exception:
            continue


def _scan_directory_fast(root: Path, items: list[dict], seen: set[str], max_depth: int = 5) -> None:
    allowed_exts = _allowed_file_exts()
    
    def _walk(curr_path: Path, current_depth: int):
        if current_depth > max_depth or not curr_path.exists():
            return

        try:
            with os.scandir(curr_path) as entries:
                for entry in entries:
                    try:
                        entry_path = Path(entry.path)
                        if entry.is_dir(follow_symlinks=False):
                            if not _should_skip_dir(entry.name, entry.path):
                                _add_item(items, seen, entry_path, "folder", "folder_scan", 30)
                                _walk(entry_path, current_depth + 1)
                        elif entry.is_file(follow_symlinks=False):
                            ext = entry_path.suffix.lower()
                            if ext in allowed_exts:
                                if ext in [".lnk", ".url"]:
                                    _add_item(items, seen, entry_path, "app", "shortcut", 100)
                                elif ext in [".exe", ".bat", ".cmd", ".msi"]:
                                    if _looks_like_app_exe(entry_path):
                                        _add_item(items, seen, entry_path, "app", "exe", 85)
                                    else:
                                        _add_item(items, seen, entry_path, "app", "utility", 60)
                                else:
                                    _add_item(items, seen, entry_path, "file", "file_scan", 40)
                    except Exception:
                        continue
        except Exception:
            pass

    _walk(root, 1)


def build_pc_index(player=None) -> str:
    global _SCANNING_IN_PROGRESS
    if _SCANNING_IN_PROGRESS:
        return "El escaneo e indexación de la PC ya está en curso."

    _SCANNING_IN_PROGRESS = True
    start_time = time.time()
    items = []
    seen = set()

    try:
        if player:
            player.write_log("🔍 Escaneando e indexando la PC completa (todos los discos)...")

        # 1. Registro (Súper prioritario)
        _scan_registry_apps(items, seen)

        # 2. Carpetas clave (Menú inicio, Escritorios, Program Files)
        h = _home()
        priority_dirs = [
            Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "Microsoft\\Windows\\Start Menu\\Programs",
            Path(os.environ.get("APPDATA", str(h / "AppData\\Roaming"))) / "Microsoft\\Windows\\Start Menu\\Programs",
            h / "Desktop",
            Path(os.environ.get("PUBLIC", "C:\\Users\\Public")) / "Desktop",
            h / "Downloads",
            h / "Documents",
            h / "Pictures",
            h / "Videos",
            h / "Music",
            Path("C:\\Program Files"),
            Path("C:\\Program Files (x86)")
        ]

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for d in priority_dirs:
                if d.exists():
                    futures.append(executor.submit(_scan_directory_fast, d, items, seen, 4))
            for f in futures:
                try:
                    f.result(timeout=15)
                except Exception:
                    pass

        # 3. Escaneo de raíces de todos los discos disponibles (C:, D:, E:, etc.)
        for drive in _get_all_drives():
            _scan_directory_fast(drive, items, seen, max_depth=3)

        # 4. Ubicaciones conocidas del sistema
        for name, path in _known_locations().items():
            items.append({
                "name": _norm(name),
                "stem": _norm(name),
                "display_name": name,
                "path": path,
                "type": "location",
                "ext": "",
                "source": "known_location",
                "score": 130
            })

        items.sort(key=lambda x: x.get("score", 0), reverse=True)
        _save_index(items)

        elapsed = round(time.time() - start_time, 1)
        msg = f"Índice actualizado correctamente con {len(items)} elementos de la PC en {elapsed}s."
        if player:
            player.write_log(f"🧠 {msg}")
        return msg

    finally:
        _SCANNING_IN_PROGRESS = False


def _open_target(target: str) -> bool:
    target = str(target).strip()
    try:
        if target.startswith("shell:") or target.startswith("ms-settings:"):
            subprocess.Popen(f'explorer "{target}"', shell=True)
            return True

        if target == "control":
            subprocess.Popen("control", shell=True)
            return True

        p = Path(target)
        if p.exists():
            if p.suffix.lower() in [".exe", ".lnk", ".url", ".bat", ".cmd", ".msi"]:
                os.startfile(str(p))
                return True

            if p.is_dir():
                subprocess.Popen(f'explorer "{p}"', shell=True)
                return True

            os.startfile(str(p))
            return True

        subprocess.Popen(f'start "" "{target}"', shell=True)
        return True
    except Exception:
        return False


def _match_score(query: str, item: dict) -> int:
    q = _norm(query)
    name = item.get("name", "")
    stem = item.get("stem", "")
    base_score = int(item.get("score", 0))

    if not q:
        return 0

    if q == stem or q == name:
        return base_score + 1000

    if stem.startswith(q) or name.startswith(q):
        return base_score + 800

    q_words = q.split()
    name_words = name.split()

    if q_words and all(any(nw.startswith(qw) for nw in name_words) for qw in q_words):
        return base_score + 650

    if q in name or q in stem:
        return base_score + 500

    return 0


def search_pc_index(query: str, limit: int = 10) -> list[dict]:
    query_norm = _norm(query)
    index = _load_index()

    if not index:
        build_pc_index()
        index = _load_index()

    matches = []
    for item in index:
        score = _match_score(query_norm, item)
        if score > 0:
            item_copy = dict(item)
            item_copy["_match_score"] = score
            matches.append(item_copy)

    matches.sort(key=lambda x: x["_match_score"], reverse=True)
    return matches[:limit]


def _find_best(query: str) -> dict | None:
    matches = search_pc_index(query, limit=1)
    return matches[0] if matches else None


def _realtime_disk_search(query: str) -> Path | None:
    query_clean = _norm(query)
    if not query_clean:
        return None

    for drive in _get_all_drives():
        try:
            with os.scandir(drive) as entries:
                for entry in entries:
                    try:
                        e_name = _norm(entry.name)
                        if query_clean in e_name:
                            return Path(entry.path)
                    except Exception:
                        continue
        except Exception:
            continue
    return None


def _extract_archive(path: str, background: bool = True) -> str:
    path_obj = Path(path)
    output_dir = path_obj.parent / path_obj.stem
    output_dir.mkdir(exist_ok=True)

    def _run_extract():
        try:
            if path_obj.suffix.lower() == ".zip":
                import zipfile
                with zipfile.ZipFile(path_obj, "r") as z:
                    z.extractall(output_dir)
                return

            from pyunpack import Archive
            Archive(str(path_obj)).extractall(str(output_dir))
        except Exception as e:
            error_file = output_dir / "error_extraccion.txt"
            error_file.write_text(str(e), encoding="utf-8")

    if background:
        threading.Thread(target=_run_extract, daemon=True).start()
        return f"Inicié la extracción de '{path_obj.name}' en segundo plano hacia '{output_dir}'."

    try:
        _run_extract()
        return f"Extraje '{path_obj.name}' en '{output_dir}'."
    except Exception as e:
        return f"No pude extraer '{path_obj.name}': {e}"


def program_updater(parameters: dict = None, player=None, **kwargs) -> str:
    """
    Actualiza el índice local de programas de la PC para incluir cualquier software nuevo recién instalado o descargado.
    """
    return build_pc_index(player)


def start_auto_program_updater():
    """Inicia un hilo en segundo plano para mantener la lista de programas y aplicaciones siempre actualizada."""
    def _loop():
        time.sleep(5.0)
        while True:
            try:
                build_pc_index()
            except Exception:
                pass
            time.sleep(120.0) # Re-indexar sutilmente cada 2 minutos en segundo plano

    threading.Thread(target=_loop, daemon=True).start()


# Iniciar el actualizador automático de programas al cargar el módulo
try:
    start_auto_program_updater()
except Exception:
    pass


def open_app(parameters: dict, response=None, player=None) -> str:
    action = str(parameters.get("action", "open")).lower().strip()

    query = (
        parameters.get("app_name")
        or parameters.get("target")
        or parameters.get("name")
        or parameters.get("path")
        or parameters.get("location")
        or ""
    )

    query = str(query).strip().strip('"').strip("'")

    if action in ["index", "scan", "reindex", "leer_pc", "actualizar_indice", "update", "update_programs"]:
        return build_pc_index(player)

    if not query:
        return "No especificaste qué programa o archivo abrir."

    if not INDEX_FILE.exists():
        build_pc_index(player)

    possible_path = Path(query).expanduser()
    if possible_path.exists():
        if action in ["extract", "extraer", "descomprimir"] or possible_path.suffix.lower() in [".zip", ".rar", ".7z"]:
            return _extract_archive(str(possible_path))

        if _open_target(str(possible_path)):
            return f"He abierto '{possible_path.name}'."

        return f"No pude ejecutar '{possible_path.name}'."

    found = _find_best(query)
    if not found:
        # Intento de escaneo rápido en tiempo real
        disk_match = _realtime_disk_search(query)
        if disk_match:
            found = {
                "display_name": disk_match.name,
                "path": str(disk_match),
                "ext": disk_match.suffix.lower()
            }
        else:
            # Reindexar en segundo plano si no se halló
            threading.Thread(target=build_pc_index, daemon=True).start()

    if found:
        path = found["path"]
        ext = found.get("ext", "")

        if action in ["extract", "extraer", "descomprimir"] or ext in [".zip", ".rar", ".7z"]:
            return _extract_archive(path)

        if _open_target(path):
            return f"He abierto '{found.get('display_name') or Path(path).stem}'."

        return f"Encontré '{found.get('display_name')}', pero ocurrió un error al abrirlo."

    return f"No encontré nada relacionado con '{query}' en los discos de tu equipo."