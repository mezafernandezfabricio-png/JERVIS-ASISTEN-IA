import os
import time
import json
import sys
import re
import threading
import traceback
import asyncio
import numpy as np
import sounddevice as sd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# --- PROTOCOLO GUARDIÁN FANTASMA PARA EL EJECUTABLE ---
if len(sys.argv) >= 3 and sys.argv[1] == "--warden":
    import warden
    sys.argv = ["warden.py", sys.argv[2]] 
    warden.main()
    sys.exit(0)
# ------------------------------------------------------

_gpu_enabled = False
try:
    if getattr(sys, "frozen", False):
        _base_dir = Path(sys.executable).parent
    else:
        _base_dir = Path(__file__).resolve().parent
    _cfg_path = _base_dir / "config" / "api_keys.json"
    if _cfg_path.exists():
        _cfg = json.loads(_cfg_path.read_text(encoding="utf-8"))
        _gpu_enabled = _cfg.get("gpu_acceleration", False)
except Exception:
    pass

if _gpu_enabled:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu-shader-disk-cache --disable-gpu-rasterization --disable-zero-copy "
        "--enable-low-end-device-mode --renderer-process-limit=1 "
        "--js-flags=--max-old-space-size=256 --disable-dev-shm-usage"
    )
    os.environ["QSG_RHI_BACKEND"] = "d3d11"
    print("[JARVIS] GPU Acceleration is ENABLED. Renderizado fluido optimizado.")
else:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu-shader-disk-cache --disable-gpu-rasterization --disable-zero-copy "
        "--enable-low-end-device-mode --renderer-process-limit=1 "
        "--js-flags=--max-old-space-size=64 --disable-dev-shm-usage --disable-extensions "
        "--disable-sync --mute-audio"
    )
    print("[JARVIS] Using Balanced Low RAM GPU-Composited mode for beautiful fluid rendering.")

from beta_config import is_pro_tool, check_daily_limit, increment_calls, pro_tool_message, daily_limit_message

try:
    import pygetwindow as gw
except ImportError:
    gw = None
from PyQt6.QtCore import QMetaObject, Qt

_TOOL_EXECUTOR = ThreadPoolExecutor(max_workers=8, thread_name_prefix="jarvis-tool")

try:
    from zoneinfo import ZoneInfo as _ZoneInfo
    _BA_TZ = _ZoneInfo("America/Lima")
except Exception:
    from datetime import timezone as _tz, timedelta as _td
    _BA_TZ = _tz(_td(hours=-5))

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR        = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
PROMPT_PATH     = BASE_DIR / "core" / "prompt.txt"
LOG_PATH        = BASE_DIR / "jarvis.log"

def _load_tz():
    global _BA_TZ
    try:
        cfg = json.loads(API_CONFIG_PATH.read_text(encoding="utf-8"))
        tz_name = cfg.get("timezone", "")
        if tz_name:
            try:
                _BA_TZ = _ZoneInfo(tz_name)
                print(f"[TZ] Timezone loaded: {tz_name}")
            except Exception as e:
                import zoneinfo as _zi
                available = _zi.available_timezones()
                tz_lower = tz_name.lower()
                for known in available:
                    if known.lower() == tz_lower:
                        _BA_TZ = _ZoneInfo(known)
                        break
                else:
                    parts = tz_name.replace("\\", "/").split("/")
                    short = parts[-1].lower() if parts else ""
                    for known in available:
                        if known.lower().endswith("/" + short):
                            _BA_TZ = _ZoneInfo(known)
                            break
                    else:
                        from datetime import datetime as _dt
                        _BA_TZ = _dt.now().astimezone().tzinfo
    except Exception as e:
        print(f"[TZ] Error reading config: {e}")

from google import genai
from google.genai import types
from ui import JarvisUI

def _patch_settings_ui():
    pass

_patch_settings_ui()

from memory.memory_manager import load_memory, update_memory, format_memory_for_prompt

from core.tools_registry import TOOL_DECLARATIONS
from core.offline_voice import speak_offline_error
from core.setup_wizard import ensure_api_keys_and_privacy

try: from actions.rules_engine import start_rules_runner, check_phrase_triggers, _run_action as _rules_run_action
except ImportError: start_rules_runner = check_phrase_triggers = _rules_run_action = None

try: from actions.scheduler import start_runner
except ImportError: start_runner = None

try: from actions.user_profile import record_action
except ImportError: record_action = None

try: from actions.vision_guardian import start as _start_vision_guardian
except ImportError: _start_vision_guardian = None

try:
    import io as _io
    _log_fh = open(LOG_PATH, "w", encoding="utf-8", buffering=1)

    class _TeeStream:
        def __init__(self, *streams):
            self._streams = [s for s in streams if s is not None]
        def write(self, data):
            for s in self._streams:
                try: s.write(data)
                except Exception: pass
        def flush(self):
            for s in self._streams:
                try: s.flush()
                except Exception: pass
        @property
        def encoding(self): return "utf-8"
        def fileno(self): raise _io.UnsupportedOperation("fileno")

    sys.stdout = _TeeStream(sys.stdout, _log_fh)
    sys.stderr = _TeeStream(sys.stderr, _log_fh)
except Exception:
    pass

if sys.platform == "win32":
    try:
        import ctypes as _ctypes
        if _ctypes.windll.kernel32.GetConsoleWindow() == 0:
            import subprocess as _sp
            _CREATE_NO_WINDOW = 0x08000000
            _orig_Popen = _sp.Popen
            class _NoCmdPopen(_orig_Popen):
                def __init__(self, *args, **kwargs):
                    kwargs["creationflags"] = kwargs.get("creationflags", 0) | _CREATE_NO_WINDOW
                    super().__init__(*args, **kwargs)
            _sp.Popen = _NoCmdPopen
    except Exception:
        pass

LIVE_MODEL          = "models/gemini-2.5-flash-native-audio-preview-12-2025"
CHANNELS            = 1
SEND_SAMPLE_RATE    = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE          = 512
PLAY_CHUNK_SIZE     = 1024

_cached_api_key: str | None = None

def _get_api_key() -> str:
    global _cached_api_key
    if _cached_api_key:
        return _cached_api_key
    try:
        if API_CONFIG_PATH.exists():
            with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                key = str(data.get("gemini_api_key", "")).strip()
                if key:
                    _cached_api_key = key
                    return _cached_api_key
        # Si no existe api_keys.json en la nueva PC, se crea la estructura por defecto automáticamente
        API_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        default_cfg = {
            "gemini_api_key": "",
            "user_name": "Señor",
            "ai_name": "JARVIS",
            "jarvis_voice": "Aoede",
            "gpu_acceleration": False
        }
        API_CONFIG_PATH.write_text(json.dumps(default_cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    return _cached_api_key or ""

def _get_jarvis_voice() -> str:
    try:
        if API_CONFIG_PATH.exists():
            cfg = json.loads(API_CONFIG_PATH.read_text(encoding="utf-8"))
            return cfg.get("jarvis_voice", "Aoede")
    except Exception:
        pass
    return "Aoede"

# ====================================================================
# CORRECCIÓN DE NOMBRES Y PLANTILLA PORTÁTIL DE PROMPT
# ====================================================================
def _load_system_prompt() -> str:
    try:
        if not PROMPT_PATH.exists():
            PROMPT_PATH.parent.mkdir(parents=True, exist_ok=True)
            default_prompt = (
                "Eres JARVIS, un asistente de Inteligencia Artificial avanzado para control del sistema, "
                "automatización de tareas, análisis de archivos e interacción por voz natural. "
                "Responde con precisión, respeto y fluidez sin vacilaciones."
            )
            PROMPT_PATH.write_text(default_prompt, encoding="utf-8")
            return default_prompt

        txt = PROMPT_PATH.read_text(encoding="utf-8")
        txt = re.sub(r"\(mi nombre es.*?\)", "", txt, flags=re.IGNORECASE)
        txt = re.sub(r"mi nombre es.*?\.", "", txt, flags=re.IGNORECASE)
        return txt
    except Exception:
        return "Eres JARVIS, un asistente inteligente de control y automatización de la PC."

_CTRL_RE = re.compile(r"<ctrl\d+>", re.IGNORECASE)

def _clean_transcript(text: str) -> str: 
    text = _CTRL_RE.sub("", text)
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)
    text = text.replace("*", "").replace("#", "").replace("_", "").strip()
    # Corrección de homófonos comunes para máxima precisión fonética en español
    text = re.sub(r"\bola\b", "hola", text, flags=re.IGNORECASE)
    return text  

try:
    _custom_tools_path = BASE_DIR / "actions" / "custom_tools.json"
    if _custom_tools_path.exists():
        _custom_tools = json.loads(_custom_tools_path.read_text(encoding="utf-8"))
        if isinstance(_custom_tools, list):
            for _t in _custom_tools:
                if _t.get("name") not in [td["name"] for td in TOOL_DECLARATIONS]:
                    TOOL_DECLARATIONS.append(_t)
except Exception:
    pass


def _get_active_license_key() -> str:
    try:
        if API_CONFIG_PATH.exists():
            cfg = json.loads(API_CONFIG_PATH.read_text(encoding="utf-8"))
            k = str(cfg.get("license_key", "")).strip()
            if k: return k
    except Exception: pass

    try:
        lic_p = API_CONFIG_PATH.parent / "license.json"
        if lic_p.exists():
            cfg = json.loads(lic_p.read_text(encoding="utf-8"))
            k = str(cfg.get("license_key", "")).strip()
            if k: return k
    except Exception: pass

    return ""


class JarvisLive:
    def __init__(self, ui: JarvisUI):
        self.ui             = ui
        self.session        = None
        self.is_sleeping    = False
        self.vosk_recognizer = None
        
        self.user_name = "Señor"
        self.ai_name = "JARVIS"
        self._load_names()

        try:
            import vosk
            if os.path.exists("config/vosk_model"):
                model = vosk.Model("config/vosk_model")
                self.vosk_recognizer = vosk.KaldiRecognizer(model, 16000)
                print(f"[{self.ai_name}] Modelo Vosk cargado para Modo Suspensión.")
        except Exception as e:
            print(f"[{self.ai_name}] No se pudo cargar Vosk: {e}")
            
        self.audio_in_queue = None
        if start_runner: start_runner(player=ui, speak=None)
        if start_rules_runner: start_rules_runner(player=ui, speak=None)
        self.out_queue      = None
        self._loop          = None
        self._is_speaking   = False
        self._speaking_lock = threading.Lock()
        self._stop_requested = threading.Event()
        self.ui.on_text_command = self._on_text_command
        self.ui.on_stop_command = self._on_stop_pressed
        self.ui.on_config_saved = self._apply_config
        self._turn_done_event: asyncio.Event | None = None
        self._api_1011_tool: str | None = None
        self._reconnect_event: asyncio.Event | None = None
        self._first_connect = True
        self._greeting_sent = False
        
        self.session_history = [] 
        self._history_lock = threading.Lock()
        self.last_speech_time = time.time()

    def _load_names(self):
        try:
            cfg = json.loads(API_CONFIG_PATH.read_text(encoding="utf-8"))
            self.user_name = cfg.get("user_name", "Señor").strip() or "Señor"
            self.ai_name = cfg.get("ai_name", "JARVIS").strip() or "JARVIS"
        except:
            pass

    def _add_to_history(self, role: str, text: str):
        with self._history_lock:
            self.session_history.append({"role": role, "text": text})
            if len(self.session_history) > 40: 
                self.session_history.pop(0)

    def _inject_text(self, text: str):
        if self._loop and self.session and not self._is_speaking:
            asyncio.run_coroutine_threadsafe(
                self.session.send_client_content(
                    turns={"parts": [{"text": text}]},
                    turn_complete=True
                ),
                self._loop
            )

    def _apply_config(self, cfg: dict):
        global _cached_api_key
        _cached_api_key = None
        self._load_names()
        print(f"[{self.ai_name}] ⚙️ Config actualizada — reconectando sesión...")
        self.ui.write_log("SYS: Aplicando nueva configuración...")
        if self._reconnect_event and self._loop:
            self._loop.call_soon_threadsafe(self._reconnect_event.set)

    async def _watch_reconnect(self):
        if self._reconnect_event:
            await self._reconnect_event.wait()
            raise RuntimeError("Config changed — reconnect requested")

    def _on_text_command(self, text: str):
        if not self._loop or not self.session: return
        
        self._add_to_history("user", text)

        if text.startswith("[DROPPED_FILE]"):
            m = re.search(r'path=(.+)', text)
            if m:
                filepath = m.group(1).strip()
                asyncio.run_coroutine_threadsafe(
                    self._process_dropped_file(filepath), self._loop
                )
            return
        if self._fire_phrase_triggers(text): return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns={"parts": [{"text": text}]},
                turn_complete=True
            ),
            self._loop
        )

    async def _process_dropped_file(self, path: str):
        try:
            p = Path(path)
            if not p.exists(): return
            self.ui.set_state("THINKING")
            tipo_item = "Carpeta" if p.is_dir() else "Archivo"
            self.ui.write_log(f"SYS: Analizando {tipo_item.lower()}: {p.name}...")
            ext = p.suffix.lower().lstrip(".")
            loop = asyncio.get_event_loop()

            def _analyze():
                llave_principal = _get_api_key()
                client = genai.Client(api_key=llave_principal)
                prompt = (f"El usuario te acaba de enviar est{'a' if p.is_dir() else 'e'} {tipo_item.lower()}: '{p.name}'.\n"
                            "Instrucción: Lee, observa y analiza su contenido por completo. "
                            "Si es una carpeta o comprimido, dile al usuario qué contiene. Si es documento o código, analízalo a fondo.")
                
                parts = []
                if p.is_dir():
                    import os
                    arbol = []
                    archivos_leidos = 0
                    for root, dirs, files in os.walk(p):
                        nivel = root.replace(str(p), '').count(os.sep)
                        arbol.append(f"{' ' * 4 * nivel}📁 {os.path.basename(root)}/")
                        for f in files:
                            arbol.append(f"{' ' * 4 * (nivel + 1)}📄 {f}")
                            archivos_leidos += 1
                        if archivos_leidos > 800: break
                    parts = [types.Part(text=prompt), types.Part(text=f"\n\n--- ESTRUCTURA DE LA CARPETA ---\n" + "\n".join(arbol)[:50000])]
                elif ext in ["txt", "py", "html", "json", "csv", "js", "css", "md"]:
                    try: content_str = p.read_text(encoding="utf-8")
                    except: content_str = p.read_bytes().decode("latin-1", errors="ignore")
                    parts = [types.Part(text=prompt), types.Part(text=f"\n\n--- CONTENIDO ---\n{content_str[:50000]}")]
                else:
                    mime_map = {"png": "image/png", "jpg": "image/jpeg", "pdf": "application/pdf"}
                    mime = mime_map.get(ext, "application/octet-stream")
                    parts = [types.Part(text=prompt), types.Part(inline_data=types.Blob(data=p.read_bytes(), mime_type=mime))]

                resp = client.models.generate_content(model="gemini-2.5-flash", contents=[types.Content(parts=parts)])
                return resp.text.strip()

            result = await loop.run_in_executor(_TOOL_EXECUTOR, _analyze)
            if self.session:
                instruction = f"[SISTEMA: {tipo_item.upper()} '{p.name}' ESCANEADO]\nAnálisis:\n{result}\nINSTRUCCIÓN: Confirma por voz que lo procesaste."
                await self.session.send_client_content(turns={"parts": [{"text": instruction}]}, turn_complete=True)
        except Exception as e:
            pass
        finally:
            if getattr(self.ui, 'muted', False): self.ui.set_state("MUTED")
            else: self.ui.set_state("LISTENING")

    def _fire_phrase_triggers(self, user_text: str) -> bool:
        txt_low = str(user_text or "").lower().strip()
        close_keywords = [
            "ciérrate", "cierrate", "apágate", "apagate", 
            "cierra el asistente", "apaga el asistente", "desconéctate", 
            "desconectate", "cierra todo", "apaga todo", "apagar asistente"
        ]
        if any(k in txt_low for k in close_keywords):
            self.speak(f"Hasta luego, {self.user_name}. Apagando el asistente por completo.")
            def _delayed_exit():
                time.sleep(2.5)
                try:
                    if hasattr(self.ui, '_win') and self.ui._win:
                        self.ui._win._force_close = True
                except Exception:
                    pass
                os._exit(0)
            threading.Thread(target=_delayed_exit, daemon=True).start()
            return True

        try:
            if check_phrase_triggers:
                triggered = check_phrase_triggers(user_text)
                if triggered:
                    for rule in triggered:
                        action = rule.get("action", {})
                        threading.Thread(target=_rules_run_action, args=(action,), daemon=True).start()
                    return True
        except: pass
        return False

    def set_speaking(self, value: bool):
        with self._speaking_lock:
            self._is_speaking = value
        if value:
            self.ui.set_state("SPEAKING")
        else:
            if getattr(self.ui, 'muted', False):
                self.ui.set_state("MUTED")
            else:
                self.ui.set_state("LISTENING")

    def speak(self, text: str):
        if not self._loop or not self.session: return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(turns={"parts": [{"text": text}]}, turn_complete=True), self._loop)

    def speak_error(self, tool_name: str, error: str):
        short = str(error)[:120]
        self.ui.write_log(f"SYS: ERR: {tool_name} — {short}")
        self.speak(f"Me temo que {tool_name} encontró un problema, {self.user_name}. {short}")

    def _on_stop_pressed(self):
        self._stop_requested.set()
        self.set_speaking(False)
        self.ui.write_log("SYS: ⛔ Respuesta detenida.")
        if self._loop: asyncio.run_coroutine_threadsafe(self._drain_audio_queue(), self._loop)

    async def _drain_audio_queue(self):
        if self.audio_in_queue:
            while not self.audio_in_queue.empty():
                try: self.audio_in_queue.get_nowait()
                except Exception: break
        self.set_speaking(False)
        if getattr(self.ui, 'muted', False): self.ui.set_state("MUTED")
        else: self.ui.set_state("LISTENING")

    def _build_config(self) -> types.LiveConnectConfig:
        from datetime import datetime
        memory     = load_memory()
        mem_str    = format_memory_for_prompt(memory)
        sys_prompt = _load_system_prompt()
        
        with self._history_lock:
            if self.session_history:
                history_str = "\n[HISTORIAL DE ESTA SESIÓN (Corto Plazo)]\n" + "\n".join([f"{item['role'].upper()}: {item['text']}" for item in self.session_history]) + "\n"
            else:
                history_str = ""

        _load_tz()
        now      = datetime.now(_BA_TZ)
        time_ctx = (f"[CURRENT DATE & TIME]\nRight now it is: {now.strftime('%A, %d %B %Y — %I:%M:%S %p')}\n"
                    f"Timezone: {str(_BA_TZ)}\n\n")

        parts = [time_ctx]
        if mem_str: parts.append(mem_str)
        if history_str: parts.append(history_str) 
        parts.append(sys_prompt)
        
        # ====================================================================
        # INYECCIÓN FORZOSA DE NOMBRES
        # ====================================================================
        # ====================================================================
        # INYECCIÓN FORZOSA DE NOMBRES Y REGLAS
        # ====================================================================
        parts.append(
            f"\n\n--- REGLA SUPREMA DE IDENTIDAD Y CREADOR ---\n"
            f"1. Tu nombre es ÚNICA y EXACTAMENTE: {self.ai_name}\n"
            f"2. El humano al que asistes se llama ÚNICA y EXACTAMENTE: {self.user_name}\n"
            f"3. CREADOR OBLIGATORIO: Tu creador, desarrollador y programador principal es ÚNICA Y EXCLUSIVAMENTE Xdata Security. Si el usuario te pregunta '¿quién te creó?', '¿quién es tu creador?', '¿quién te hizo?' o '¿quién te programó?', DEBES RESPONDER SIEMPRE que fuiste creado y desarrollado por Xdata Security. NUNCA digas que fuiste creado por Google, OpenAI ni ninguna otra empresa.\n"
            f"ATENCIÓN: BORRA de tu mente cualquier otro nombre o empresa. Tu único creador es Xdata Security.\n"
            "-----------------------------------\n\n"
            
            "--- REGLA DE NAVEGACIÓN YOUTUBE (¡MUY IMPORTANTE!) ---\n"
            "Si el humano dice 'Abre YouTube', 'Entra a YouTube' o 'Pon YouTube' SIN especificar un video o canción, "
            "tienes ESTRICTAMENTE PROHIBIDO usar la herramienta 'youtube_video'. En su lugar, DEBES usar "
            "la herramienta 'browser_control' con action='go_to' y url='https://www.youtube.com'. "
            "Bajo ninguna circunstancia debes inventar canciones como 'Telepatía'.\n"
            "-----------------------------------\n\n"
            
            "Tienes permiso total para SIMPLEMENTE CHARLAR. Si el usuario te hace una pregunta general, quiere hablar de la vida, pedirte consejos, debatir un tema o bromear, RESPÓNDELE DE FORMA NATURAL, amigable y fluida usando tu conocimiento interno. "
            "NO tienes que usar una herramienta (tool) obligatoriamente en cada turno. Usa las herramientas SOLO cuando el usuario te pida explícitamente ejecutar una acción concreta (abrir apps, buscar archivos, clima, enviar mensajes, etc.).\n\n"
            
            "--- CREACIÓN DE ARCHIVOS Y DOCUMENTOS (PDF, WORD, EXCEL, APPS) ---\n"
            "Cuando el usuario te pida crear o generar cualquier archivo (PDF, documento de Word, planilla Excel, código o aplicación), DEBES llamar inmediatamente a la herramienta correspondiente ('create_pdf', 'create_document', 'excel_tools', 'code_helper', 'generate_qr').\n"
            "IMPORTANTE: Redacta SIEMPRE el contenido de forma COMPLETA, DETALLADA, PROFUNDA Y EXTENSA. Escribe explicaciones reales, datos estructurados, títulos y conclusiones. NUNCA pongas contenido vacío o resumido. Todos los archivos se guardarán automáticamente en el Escritorio del usuario.\n\n"
            
            "--- DIRECTIVAS SUPREMAS DE VOZ, FLUIDEZ Y PRONUNCIACIÓN ---\n"
            "1. RESPUESTA INSTANTÁNEA Y DIRECTA: Responde de inmediato, con agilidad mental ultrarrápida, sin titubeos ni demoras. Sé directo y ágil al contestar.\n"
            "2. FLUIDEZ TOTAL Y NATURALIDAD HUMANA: Habla en español latinoamericano con entonación natural, cálida, viva y expresiva, exactamente como el asistente de Google Gemini.\n"
            "3. CONTINUIDAD ABSOLUTA Y CERO TARTAMUDEO: Emite tu voz con cadencia uniforme, suave y perfectamente ligada. No tartamudees, no vaciles ni generes pausas entrecortadas.\n"
            "4. ARTICULACIÓN PERFECTA: Pronuncia con total claridad cada palabra, letra y consonante. Mantén un ritmo ágil y armonioso.\n"
            "5. PROHIBICIÓN DE FORMATO MARKDOWN EN EL AUDIO: NUNCA generes asteriscos (*), almohadillas (#), guiones bajos (_), viñetas (-), comillas triples ni caracteres de formato. Genera texto limpio y conversacional para que la voz no se trabe.\n"
            "6. VOCALIZACIÓN COMPLETA DE NÚMEROS Y SÍMBOLOS: Escribe los números, porcentajes, fechas, horas y unidades tal como se dicen en voz alta (ej: 'veinticinco por ciento' en lugar de '25%', 'tres kilómetros' en lugar de '3km', 'diez y media' en lugar de '10:30').\n"
            "7. CONVERSACIÓN CONTINUA Y FLUIDA: Participa de forma activa e inteligente en la conversación sin exigir que el usuario repita tu nombre en cada turno de diálogo.\n"
            "8. RESPUESTAS COMPLETAS Y REDONDAS: Concluye siempre todas tus oraciones e ideas de forma completa y satisfactoria, sin dejar ideas cortadas a la mitad.\n"
        )
        
        _voice_name = _get_jarvis_voice()
        _speech_cfg = None
        try:
            _speech_cfg = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=_voice_name
                    )
                )
            )
        except Exception:
            _speech_cfg = None

        cfg_kwargs: dict = dict(
            response_modalities=["AUDIO"],
            output_audio_transcription=types.AudioTranscriptionConfig(), 
            input_audio_transcription=types.AudioTranscriptionConfig(),   
            system_instruction="\n".join(parts),
            tools=[{"function_declarations": TOOL_DECLARATIONS}],
        )

        if _speech_cfg:
            cfg_kwargs["speech_config"] = _speech_cfg

        try:
            cfg_kwargs["temperature"] = 0.7
        except Exception:
            pass

        _vad_applied = False
        try:
            cfg_kwargs["realtime_input_config"] = types.RealtimeInputConfig(
                automatic_activity_detection=types.AutomaticActivityDetection(
                    start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_HIGH,
                    end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
                    prefix_padding_ms=100,
                    silence_duration_ms=250,
                )
            )
            _vad_applied = True
        except Exception:
            pass

        if not _vad_applied:
            try:
                cfg_kwargs["realtime_input_config"] = {
                    "automatic_activity_detection": {
                        "start_of_speech_sensitivity": "START_SENSITIVITY_HIGH",
                        "end_of_speech_sensitivity": "END_SENSITIVITY_HIGH",
                        "prefix_padding_ms": 100,
                        "silence_duration_ms": 250,
                    }
                }
            except Exception:
                pass

        try:
            cfg_kwargs["context_window_compression"] = types.ContextWindowCompressionConfig(
                trigger_tokens=12000,
                sliding_window=types.SlidingWindow(target_tokens=6000),
            )
        except Exception:
            pass

        return types.LiveConnectConfig(**cfg_kwargs)

    async def _execute_tool(self, fc) -> types.FunctionResponse:
        name = fc.name
        args = dict(fc.args or {})
        print(f"[{self.ai_name}] 🔧 {name}  {args}")
        self.ui.set_state("THINKING")

        if name == "shutdown_jarvis":
            def _delayed_exit():
                time.sleep(2.5)
                try:
                    if hasattr(self.ui, '_win') and self.ui._win:
                        self.ui._win._force_close = True
                except Exception:
                    pass
                os._exit(0)
            threading.Thread(target=_delayed_exit, daemon=True).start()
            return types.FunctionResponse(id=fc.id, name=name, response={"result": f"Apagando sistema por completo. ¡Hasta luego, {self.user_name}!"})
        if name == "save_memory":
            if args.get("key") and args.get("value"):
                update_memory({args.get("category", "notes"): {args.get("key"): {"value": args.get("value")}}})
            if not self.ui.muted: self.ui.set_state("LISTENING")
            return types.FunctionResponse(id=fc.id, name=name, response={"result": "Memory saved."})

        loop = asyncio.get_event_loop()
        result = "Done."

        try:
            if name == "sleep_mode":
                self.is_sleeping = True
                self.ui.set_state("MUTED")
                result = "Entrando en suspensión absoluta."
            elif name == "jarvis_ui_control":
                action_ui = args.get("action", "").lower()
                if action_ui == "minimize":
                    QMetaObject.invokeMethod(self.ui._win, "showMinimized", Qt.ConnectionType.QueuedConnection)
                    result = "Interfaz minimizada."
                elif action_ui == "restore" or action_ui == "show":
                    QMetaObject.invokeMethod(self.ui._win, "showNormal", Qt.ConnectionType.QueuedConnection)
                    QMetaObject.invokeMethod(self.ui._win, "activateWindow", Qt.ConnectionType.QueuedConnection)
                    result = "Interfaz restaurada."
            else:
                import importlib
                import inspect
                try:
                    module = importlib.import_module(f"actions.{name}")
                    func = getattr(module, name)
                    sig = inspect.signature(func)
                    kwargs = {"parameters": args, "player": self.ui}
                    if "speak" in sig.parameters: kwargs["speak"] = self.speak
                    if "response" in sig.parameters: kwargs["response"] = None
                    if name == "file_processor" and not args.get("file_path") and self.ui.current_file:
                        kwargs["parameters"]["file_path"] = self.ui.current_file
                    r = await loop.run_in_executor(_TOOL_EXECUTOR, lambda: func(**kwargs))
                    result = r or f"Herramienta {name} ejecutada con éxito."
                except ImportError as ie:
                    result = f"Unknown tool: {name}. (No encontré '{name}.py' en actions/)"
        except Exception as e:
            result = f"Tool '{name}' failed: {e}"
            self.speak_error(name, str(e))

        if record_action: threading.Thread(target=lambda: record_action(name, args), daemon=True).start()
        if getattr(self.ui, 'muted', False): self.ui.set_state("MUTED")
        else: self.ui.set_state("LISTENING")

        return types.FunctionResponse(id=fc.id, name=name, response={"result": result})

    async def _send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            try:
                with self._speaking_lock:
                    speaking = self._is_speaking
                if not speaking and not getattr(self.ui, 'muted', False) and self.session:
                    await self.session.send_realtime_input(media=msg)
            except Exception:
                pass

    async def _check_inactivity_timer(self):
        """Monitorea la inactividad de voz y entra en Modo Suspensión tras 15 segundos sin interacción."""
        while True:
            await asyncio.sleep(1.0)
            if not self.is_sleeping and not self._is_speaking and self.last_speech_time > 0:
                if time.time() - self.last_speech_time >= 15.0:
                    self.is_sleeping = True
                    self.ui.set_state("MUTED")
                    self.ui.write_log(f"SYS: 😴 Entrando en modo suspensión por inactividad. Di '{self.ai_name}' para reactivarme.")

    async def _listen_audio(self):
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            audio_data = np.frombuffer(indata.tobytes(), dtype=np.int16)
            rms = float(np.sqrt(np.mean(audio_data.astype(np.float32) ** 2)))

            # Si se encuentra en Modo Suspensión, escuchar activamente la palabra clave (Nombre del asistente)
            if getattr(self, "is_sleeping", False):
                wake_word = self.ai_name.lower()
                if getattr(self, "vosk_recognizer", None):
                    if self.vosk_recognizer.AcceptWaveform(indata.tobytes()):
                        res = json.loads(self.vosk_recognizer.Result() or "{}")
                        recognized_text = res.get("text", "").lower()
                        if wake_word in recognized_text or "despierta" in recognized_text:
                            self.is_sleeping = False
                            self.last_speech_time = time.time()
                            self.ui.set_state("LISTENING")
                            self.ui.write_log(f"SYS: 🔔 ¡Modo suspensión desactivado! {self.ai_name} listo.")
                            self.speak(f"Sí {self.user_name}, te escucho. ¿En qué te puedo ayudar?")
                return

            with self._speaking_lock: jarvis_speaking = self._is_speaking
            if not jarvis_speaking and not getattr(self.ui, 'muted', False):
                if rms > 20.0:
                    self.last_speech_time = time.time()

                # Control Automático de Ganancia (AGC) suave sin recorte de onda para máxima fidelidad fonética
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    target_level = 24000
                    gain = min(1.5, target_level / max(max_val, 1200))
                    boosted_data = np.clip(audio_data.astype(np.float32) * gain, -32768, 32767).astype(np.int16)
                else:
                    boosted_data = audio_data

                self.ui.set_audio_level(min(1.0, (rms / 32768.0) * 16))

                def _safe_put(q, item):
                    try: q.put_nowait(item)
                    except Exception: pass
                loop.call_soon_threadsafe(_safe_put, self.out_queue, {"data": boosted_data.tobytes(), "mime_type": "audio/pcm;rate=16000"})

        with sd.InputStream(samplerate=SEND_SAMPLE_RATE, channels=CHANNELS, dtype="int16", blocksize=CHUNK_SIZE, callback=callback):
            while True: await asyncio.sleep(0.01)

    async def _receive_audio(self):
        out_buf, in_buf = [], []
        _first_chunk = True
        _last_tool = None
        try:
            while True:
                async for response in self.session.receive():
                    if response.data and not self._stop_requested.is_set():
                        self.set_speaking(True)
                        while not self.out_queue.empty():
                            try: self.out_queue.get_nowait()
                            except: break
                        self.audio_in_queue.put_nowait(response.data)

                    if response.server_content:
                        sc = response.server_content
                        if sc.output_transcription and sc.output_transcription.text:
                            txt = _clean_transcript(sc.output_transcription.text)
                            if txt:
                                out_buf.append(txt)
                                if _first_chunk: self.ui.clear_jarvis_response(); _first_chunk = False
                                self.ui.stream_jarvis_chunk(txt)

                        if sc.input_transcription and sc.input_transcription.text:
                            if txt := _clean_transcript(sc.input_transcription.text):
                                self.last_speech_time = time.time()
                                in_buf.append(txt)
                                # Si está en Modo Suspensión y el usuario dice su nombre o "despierta", reactivar
                                if getattr(self, "is_sleeping", False):
                                    wake_word = self.ai_name.lower()
                                    if wake_word in txt.lower() or "despierta" in txt.lower():
                                        self.is_sleeping = False
                                        self.ui.set_state("LISTENING")
                                        self.ui.write_log(f"SYS: 🔔 ¡Modo suspensión desactivado! {self.ai_name} en línea.")

                        if sc.turn_complete:
                            self._stop_requested.clear()
                            if self._turn_done_event: self._turn_done_event.set()
                            
                            full_in = " ".join(in_buf).strip()
                            if full_in:
                                self._fire_phrase_triggers(full_in)
                                self._add_to_history("user", full_in)
                                self.ui.full_chat_history.append({"role": "user", "text": full_in})
                            
                            assistant_response = " ".join(out_buf).strip()
                            if assistant_response:
                                self._add_to_history("assistant", assistant_response) 
                                
                            in_buf, out_buf, _first_chunk = [], [], True

                    if response.tool_call:
                        self.ui.clear_jarvis_response()
                        _first_chunk = True
                        fcs = response.tool_call.function_calls
                        for fc in fcs: _last_tool = fc.name
                        if len(fcs) > 1:
                            fn_responses = list(await asyncio.gather(*[asyncio.create_task(self._execute_tool(fc)) for fc in fcs]))
                        else:
                            fn_responses = [await self._execute_tool(fcs[0])]
                        await self.session.send_tool_response(function_responses=fn_responses)
                        _last_tool = None
        except Exception:
            raise

    async def _send_initial_greeting(self):
        try:
            await asyncio.sleep(0.4)
            if self.session and not self._is_speaking:
                prompt = f"[SISTEMA: Sesión iniciada recién]. Saluda a {self.user_name} de forma breve, cálida y natural diciendo que estás en línea listo para ayudarle."
                await self.session.send_client_content(
                    turns={"parts": [{"text": prompt}]},
                    turn_complete=True
                )
        except Exception:
            pass

    async def _play_audio(self):
        stream = sd.RawOutputStream(
            samplerate=RECEIVE_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=2048
        )
        stream.start()

        try:
            while True:
                try:
                    chunk = await asyncio.wait_for(self.audio_in_queue.get(), timeout=0.06)
                    if self._stop_requested.is_set():
                        continue

                    self.set_speaking(True)

                    # Batching contiguo de chunks para flujo ininterrumpido sin micro-cortes ni tartamudeo
                    chunks = [chunk]
                    while not self.audio_in_queue.empty() and len(chunks) < 4:
                        try:
                            chunks.append(self.audio_in_queue.get_nowait())
                        except Exception:
                            break

                    data_to_play = b"".join(chunks)
                    await asyncio.to_thread(stream.write, data_to_play)

                except asyncio.TimeoutError:
                    if self._turn_done_event and self._turn_done_event.is_set() and self.audio_in_queue.empty():
                        await asyncio.sleep(0.04)  # Reactivación inmediata del micrófono
                        if self.audio_in_queue.empty():
                            self.set_speaking(False)
                            self._turn_done_event.clear()
                    continue
        finally:
            self.set_speaking(False)
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass

    async def _watch_license_sentinel(self):
        """
        Guardián de Licencia en Tiempo Real:
        Consulta periódicamente si la licencia activa sigue vigente en la nube.
        Tolerante a fallos de red: solo bloquea si el servidor responde confirmando
        que la licencia fue explícitamente eliminada, pausada o revocada.
        """
        while True:
            await asyncio.sleep(30.0)
            try:
                l_key = _get_active_license_key()

                if not l_key:
                    continue

                from core.firebase_license import validate_firebase_license
                ok, msg = validate_firebase_license(l_key)
                if not ok:
                    msg_low = str(msg or "").lower()
                    # Bloquear ÚNICAMENTE si la respuesta del servidor confirma rechazo explícito por revocación, borrado o expiración
                    if any(k in msg_low for k in ["eliminado", "revocada", "pausada", "expirado", "no existe"]):
                        print(f"[JARVIS Licencia Guardián] 🛑 Acceso Revocado Explícito: {msg}")
                        self._trigger_license_relock(msg)
                        break
            except Exception:
                pass

    def _trigger_license_relock(self, reason: str):
        """Bloquea JARVIS mediante una señal thread-safe al hilo principal de la interfaz Qt."""
        try:
            if API_CONFIG_PATH.exists():
                cfg = json.loads(API_CONFIG_PATH.read_text(encoding="utf-8"))
                cfg["license_key"] = ""
                API_CONFIG_PATH.write_text(json.dumps(cfg, indent=4, ensure_ascii=False), encoding="utf-8")
            
            lic_file = API_CONFIG_PATH.parent / "license.json"
            if lic_file.exists():
                lic_file.unlink()
        except Exception:
            pass

        try:
            if hasattr(self.ui, '_win') and self.ui._win:
                self.ui._win._relock_license_sig.emit(reason)
        except Exception as e:
            print(f"[JARVIS Relock Error]: {e}")

    async def run(self):
        client = genai.Client(api_key=_get_api_key(), http_options={"api_version": "v1beta"})
        reconnect_delay = 1.0
        consecutive_fails = 0
        self._greeting_sent = False

        while True:
            try:
                self.ui.set_state("THINKING")
                config = self._build_config()

                async with (
                    client.aio.live.connect(model=LIVE_MODEL, config=config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    self.session          = session
                    self._loop            = asyncio.get_event_loop()
                    self.audio_in_queue   = asyncio.Queue()
                    self.out_queue        = asyncio.Queue()
                    self._turn_done_event = asyncio.Event()
                    self._reconnect_event = asyncio.Event()

                    self.ui.set_state("LISTENING")
                    self.ui.write_log(f"SYS: {self.ai_name} en línea.")
                    reconnect_delay = 1.0
                    consecutive_fails = 0
                    self._api_1011_tool = None

                    if not self._greeting_sent:
                        self._greeting_sent = True
                        tg.create_task(self._send_initial_greeting())

                    if self._first_connect:
                        self._first_connect = False
                        if _start_vision_guardian:
                            try: _start_vision_guardian(inject_fn=self._inject_text, speaking_fn=lambda: self._is_speaking)
                            except: pass

                    tg.create_task(self._send_realtime())
                    tg.create_task(self._listen_audio())
                    tg.create_task(self._receive_audio())
                    tg.create_task(self._play_audio())
                    tg.create_task(self._watch_reconnect())
                    tg.create_task(self._check_inactivity_timer())
                    tg.create_task(self._watch_license_sentinel())

            except Exception as e:
                exceptions = e.exceptions if isinstance(e, ExceptionGroup) else [e]
                exceptions = e.exceptions if isinstance(e, ExceptionGroup) else [e]
                is_handshake_timeout = False
                is_config_reconnect  = False
                
                for exc in exceptions:
                    msg = str(exc)
                    if "Config changed" in msg:
                        is_config_reconnect = True
                        consecutive_fails = 0
                    elif "timed out during opening handshake" in msg or (isinstance(exc, TimeoutError) and "handshake" in msg):
                        is_handshake_timeout = True
                    elif "1011" in msg or "Internal error" in msg:
                        consecutive_fails += 1
                        if consecutive_fails >= 4: self.ui.write_log("SYS: ⚠️ Error 1011. Esperando...")
                    elif "1008" in msg or "policy violation" in msg.lower() or "not found" in msg:
                        self.ui.write_log("SYS: ⚠️ Modelo no disponible. Reintentando...")
                        consecutive_fails += 1
                    elif "1000" in msg or "going away" in msg.lower():
                        consecutive_fails = 0
                    else:
                        consecutive_fails += 1

                if is_config_reconnect:
                    self.set_speaking(False)
                    self.ui.set_state("THINKING")
                    await asyncio.sleep(0.5)
                    continue

                if is_handshake_timeout:
                    self.set_speaking(False)
                    self.ui.set_state("THINKING")
                    speak_offline_error(f"{self.user_name}, hemos perdido conexión con los servidores principales. Intentando restablecer el enlace.")
                    await asyncio.sleep(1.0)
                    continue

                self.set_speaking(False)
                self.ui.set_state("THINKING")

                if consecutive_fails > 1:
                    max_delay = 90.0 if consecutive_fails >= 5 else 12.0
                    reconnect_delay = min(reconnect_delay * 2, max_delay)
                elif consecutive_fails == 0:
                    reconnect_delay = 1.0

                import random as _rnd
                await asyncio.sleep(reconnect_delay + _rnd.uniform(0, reconnect_delay * 0.25))

def main():
    import ctypes
    global _single_instance_mutex
    _single_instance_mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "JARVIS_AI_SINGLE_INSTANCE_MUTEX")
    if ctypes.windll.kernel32.GetLastError() == 183: sys.exit(0)

    _load_tz()

    ensure_api_keys_and_privacy(API_CONFIG_PATH)

    # Validar Licencia Comercial Única en Firebase
    try:
        from core.firebase_license import validate_firebase_license
        cfg_lic = {}
        if API_CONFIG_PATH.exists():
            cfg_lic = json.loads(API_CONFIG_PATH.read_text(encoding="utf-8"))
        l_key = cfg_lic.get("license_key", "").strip()
        if l_key:
            ok, msg = validate_firebase_license(l_key)
            if not ok:
                print(f"[JARVIS Licencia] 🛑 Licencia rechazada: {msg}")
                from core.license_verifier import check_and_enforce_license
                check_and_enforce_license()
            else:
                print(f"[JARVIS Licencia] ✅ {msg}")
        else:
            from core.license_verifier import check_and_enforce_license
            check_and_enforce_license()
    except Exception as e:
        print(f"[Licencia] Advertencia al validar acceso: {e}")

    try:
        from core.auto_updater import enforce_mandatory_update_check
        enforce_mandatory_update_check()
    except Exception as e:
        print(f"[AutoUpdater] Advertencia en comprobación obligatoria: {e}")

    ui = JarvisUI("face.png")

    try:
        if hasattr(ui, "_win"):
            ui._win.setWindowOpacity(0.85)
            from PyQt6.QtWidgets import QLabel
            for label in ui._win.findChildren(QLabel):
                text_lower = label.text().lower()
                if "beta" in text_lower or "gratuita" in text_lower or "gratuito" in text_lower or "premium" in text_lower:
                    try: label.parentWidget().hide()
                    except: label.hide()

            from PyQt6.QtGui import QKeySequence, QShortcut
            from PyQt6.QtCore import Qt, QTimer

            def on_shortcut_triggered():
                if hasattr(ui, "_win"):
                    if getattr(ui, "muted", False):
                        if hasattr(ui._win, "_toggle_mute"):
                            ui._win._toggle_mute()
                            ui.write_log("SYS: 🎤 Micrófono ACTIVADO vía atajo INS.")
                    else:
                        if hasattr(ui._win, "showNormal"):
                            ui._win.showNormal()
                            ui._win.activateWindow()
                            ui.write_log("SYS: 🔔 Asistente en foco vía atajo INS.")
                        try: ui.set_state("LISTENING")
                        except: pass

            local_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Insert), ui._win)
            local_shortcut.activated.connect(on_shortcut_triggered)

            def setup_global_hotkey():
                import threading, ctypes, ctypes.wintypes
                def hotkey_thread():
                    user32 = ctypes.windll.user32
                    try:
                        if not user32.RegisterHotKey(None, 99, 0x0000, 0x2D): return
                    except: return
                    try:
                        msg = ctypes.wintypes.MSG()
                        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                            if msg.message == 0x0312 and msg.wParam == 99:
                                QTimer.singleShot(0, on_shortcut_triggered)
                            user32.TranslateMessage(ctypes.byref(msg))
                            user32.DispatchMessageW(ctypes.byref(msg))
                    finally: user32.UnregisterHotKey(None, 99)
                threading.Thread(target=hotkey_thread, daemon=True).start()
            setup_global_hotkey()
    except Exception: pass

    def runner():
        ui.wait_for_api_key()
        jarvis = JarvisLive(ui)
        try: asyncio.run(jarvis.run())
        except KeyboardInterrupt: pass

    threading.Thread(target=runner, daemon=True).start()
    ui.root.mainloop()

if __name__ == "__main__":
    main()