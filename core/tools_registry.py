# core/tools_registry.py
# -*- coding: utf-8 -*-

TOOL_DECLARATIONS = [
    {
        "name": "jarvis_ui_control",
        "description": (
            "Control total sobre la ventana principal y los widgets de la interfaz de JARVIS. "
            "Permite minimizar/restaurar la ventana principal, o abrir, cerrar, alternar la visibilidad de cualquier widget del dashboard.\n"
            "Widgets disponibles: weather (clima), spotify (música), system (sistema), "
            "notes (notas), todo (tareas), maps (mapas), image (imágenes), camera (cámara)."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "minimize (minimizar ventana) | restore (restaurar ventana) | show (mostrar widget) | hide (ocultar widget) | hide_all (ocultar todos los widgets) | toggle (alternar widget)"
                },
                "widget": {
                    "type": "STRING",
                    "description": "Nombre del widget (solo para show/hide/toggle): weather | spotify | system | notes | todo | maps | image | camera"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "open_app",
        "description": "Lee, indexa y abre automáticamente cualquier aplicación, juego, ejecutable, APK, archivo, carpeta, disco o ubicación del sistema encontrada en la PC del usuario. Debe crear un índice local de la PC y usar coincidencias por primer nombre o nombre parcial para ejecutar directamente lo pedido sin preguntar dos veces.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "Acción: open, abrir, launch, index, scan, reindex, leer_pc, extract, extraer o descomprimir."},
                "app_name": {"type": "STRING", "description": "Nombre o primer nombre de la app, archivo, carpeta, juego o ubicación a abrir. Ejemplos: virtual, steam, chrome, documentos, papelera, informe, foto, archivo rar."},
                "target": {"type": "STRING", "description": "Alternativa a app_name. Puede ser nombre parcial o ruta completa."},
                "path": {"type": "STRING", "description": "Ruta exacta opcional del archivo, carpeta o ejecutable."},
                "location": {"type": "STRING", "description": "Ubicación del sistema: escritorio, descargas, documentos, imágenes, videos, música, papelera, disco C o disco D."}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "program_updater",
        "description": (
            "Actualiza y re-escanea automáticamente el índice de programas y aplicaciones de la PC para incluir cualquier software nuevo recién instalado o descargado. "
            "Llamar cuando el usuario pida 'actualiza los programas de mi PC', 'escanea programas nuevos', 'actualizar lista de aplicaciones'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "update, index, scan"}
            }
        }
    },
    {
        "name": "web_search",
        "description": "Obtiene información o resúmenes de la web en segundo plano sin abrir ventanas del navegador. NUNCA abre el navegador web. No usar para preguntas conversacionales normales que puedes responder con tu propio conocimiento.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query":  {"type": "STRING", "description": "Término de búsqueda web"},
                "mode":   {"type": "STRING", "description": "search (default) o compare"},
                "items":  {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Items a comparar"},
                "aspect": {"type": "STRING", "description": "price | specs | reviews"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "weather_report",
        "description": "Obtiene el clima actual exacto y el pronóstico de los próximos días para cualquier ciudad o país del mundo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING", "description": "Nombre de la ciudad y el país (ej: 'Bogotá, Colombia', 'Madrid, España', 'Tokio, Japón')"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "send_message",
        "description": "Sends a text message via Telegram, Discord, Signal or other messaging platform. For WhatsApp, use the 'whatsapp' tool instead.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "receiver":     {"type": "STRING", "description": "Recipient contact name"},
                "message_text": {"type": "STRING", "description": "The message to send"},
                "platform":     {"type": "STRING", "description": "Platform: Telegram, Discord, Signal, Messenger (NOT WhatsApp — use whatsapp tool)"}
            },
            "required": ["receiver", "message_text", "platform"]
        }
    },
    {
        "name": "reminder",
        "description": "Sets a timed reminder using Task Scheduler.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "date":    {"type": "STRING", "description": "Date in YYYY-MM-DD format"},
                "time":    {"type": "STRING", "description": "Time in HH:MM format (24h)"},
                "message": {"type": "STRING", "description": "Reminder message text"}
            },
            "required": ["date", "time", "message"]
        }
    },
    {
        "name": "youtube_video",
        "description": (
            "Controla YouTube completamente. Usar para: reproducir videos (play), pausar/reanudar (pause), "
            "detener (stop), siguiente (next), reiniciar desde cero (restart). "
            "REGLA ESTRICTA: Si el usuario SOLO dice 'Abre YouTube' y NO especifica qué video o canción quiere escuchar, "
            "ESTÁ PROHIBIDO usar esta herramienta e inventar canciones. En ese caso, usa 'browser_control' para ir a youtube.com."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "play | pause | stop | next | restart"},
                "query":  {"type": "STRING", "description": "Término de búsqueda para play"},
                "time":   {"type": "INTEGER", "description": "Segundos de inicio (ej: 120 para el minuto 2)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "computer_settings",
        "description": "Controla ventanas y ajustes del sistema. Puede cerrar, minimizar, maximizar, restaurar o poner pantalla completa la ventana activa. También controla volumen, brillo, WiFi, Bluetooth, modo avión, planes de energía, bloqueo, suspensión, apagado y reinicio sin pedir confirmación.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "Acción: close, cerrar, minimize, minimizar, fullscreen, pantalla_completa, maximize, maximizar, restore, restaurar, volume, subir_volumen, bajar_volumen, silenciar, brightness, subir_brillo, bajar_brillo, wifi_on, wifi_off, encender_wifi, apagar_wifi, bluetooth_on, bluetooth_off, encender_bluetooth, apagar_bluetooth, airplane_mode, modo_avion, power_saver, ahorro_energia, balanced, equilibrado, high_performance, alto_rendimiento, lock, bloquear, sleep, suspender, shutdown, apagar_pc, restart o reiniciar_pc."},
                "window": {"type": "STRING", "description": "Nombre opcional de la ventana o aplicación. Si se omite, se usa la ventana activa."},
                "window_title": {"type": "STRING", "description": "Título opcional de la ventana."},
                "app_name": {"type": "STRING", "description": "Nombre opcional de la aplicación."},
                "target": {"type": "STRING", "description": "Nombre opcional del objetivo, ventana o aplicación."},
                "value": {"type": "STRING", "description": "Valor opcional. Para volumen o brillo puede ser 0-100, subir, bajar, alzar, down, up, mute o silenciar."}
            },
            "required": ["action"]
        }
    },
    {
        "name": "browser_control",
        "description": (
            "Controla el navegador activo del usuario (Chrome, Edge, Firefox, etc.) sin abrir uno nuevo. "
            "Usa esta herramienta cuando el usuario te pida interactuar con la web. "
            "Acciones soportadas: navegar a una URL, buscar en Google, abrir o cerrar pestañas, y scrollear. "
            "REGLA ESTRICTA: Si el usuario dice 'Abre YouTube' (sin pedir un video específico), DEBES usar esta "
            "herramienta con action='go_to' y url='https://www.youtube.com'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "Acciones permitidas: go_to | search | new_tab | close_tab | scroll"},
                "url":         {"type": "STRING", "description": "URL para las acciones go_to o new_tab"},
                "query":       {"type": "STRING", "description": "Término de búsqueda para la acción search"},
                "direction":   {"type": "STRING", "description": "Dirección de scroll: up | down (solo para scroll)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "visual_click",
        "description": "DEBES USAR ESTA HERRAMIENTA OBLIGATORIAMENTE para hacer clic físicamente usando el puntero real del mouse sobre cualquier elemento visible en pantalla. Usa visión artificial adaptativa para encontrar botones, enlaces, URLs, 'primer resultado de búsqueda en Google', 'primera opción', 'primer video en YouTube', 'segunda opción', personas, objetos, imágenes o textos descritos por el usuario. Ejecuta el clic de forma milimétrica en cualquier resolución de pantalla sin confirmación adicional.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "element_description": {"type": "STRING", "description": "Descripción exacta del objetivo visual. Ejemplos: 'primer resultado en Google', 'primera opción', 'primer video de YouTube', 'botón descargar', 'pestaña Chrome'."},
                "action_text": {"type": "STRING", "description": "Alternativa a element_description."},
                "x": {"type": "NUMBER", "description": "Coordenada X opcional si se indica posición exacta."},
                "y": {"type": "NUMBER", "description": "Coordenada Y opcional si se indica posición exacta."},
                "clicks": {"type": "NUMBER", "description": "Cantidad de clics. Por defecto 1."},
                "button": {"type": "STRING", "description": "Botón del mouse: left, right o middle. Por defecto left."}
            },
            "required": ["element_description"]
        }
    },
    {
        "name": "screen_vision",
        "description": "DEBES USAR ESTA HERRAMIENTA OBLIGATORIAMENTE cuando el usuario pregunte '¿qué ves?', 'describe mi pantalla', 'analiza esto' o pida información visual de su monitor. Sin esta herramienta eres ciego. Captura y analiza la pantalla completa o una región específica de forma impecable.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "Acción: analyze, analizar, save, guardar, screenshot, captura, full, completa, region, captura_region, especifica, analyze_region o analizar_region."},
                "query": {"type": "STRING", "description": "Pregunta o instrucción para analizar la captura."},
                "text": {"type": "STRING", "description": "Alternativa a query."},
                "question": {"type": "STRING", "description": "Alternativa a query."},
                "filename": {"type": "STRING", "description": "Nombre opcional para guardar la captura."},
                "name": {"type": "STRING", "description": "Nombre alternativo para el archivo."},
                "monitor": {"type": "INTEGER", "description": "Monitor a capturar. Por defecto 1."},
                "x": {"type": "NUMBER", "description": "Coordenada X inicial para captura específica."},
                "y": {"type": "NUMBER", "description": "Coordenada Y inicial para captura específica."},
                "width": {"type": "NUMBER", "description": "Ancho de captura específica."},
                "height": {"type": "NUMBER", "description": "Alto de captura específica."},
                "save": {"type": "BOOLEAN", "description": "Si es true, guarda captura."}
            },
            "required": ["action"]
        }
    },
    {
        "name": "sleep_mode",
        "description": "Entra en modo suspensión. Desactiva el micrófono para la IA hasta que el usuario diga 'Oye JARVIS' o 'JARVIS' localmente.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "software_installer",
        "description": "Instala software, programas o aplicaciones de forma silenciosa en segundo plano en la PC del usuario usando Winget, Chocolatey o ejecutable local. Traduce nombres comunes (ej. 'chrome' -> 'Google.Chrome', 'vlc' -> 'VideoLAN.VLC') o pasa directamente el nombre/ID o la ruta local del instalador.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "programas": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING"
                    },
                    "description": "Lista de nombres de programas, IDs de Winget o rutas de instaladores a ejecutar silenciosamente (ej. ['Google.Chrome'], ['VLC'], ['C:\\setup.exe'])."
                }
            },
            "required": ["programas"]
        }
    },
    {
        "name": "software_uninstaller",
        "description": "Desinstala rápida y limpiamente programas o aplicaciones de la PC del usuario consultando el Registro de Windows (32/64 bit), Winget o borrado de directorio.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "accion": {
                    "type": "STRING",
                    "description": "Acción a ejecutar: 'desinstalar' (por defecto), 'confirmar', 'cancelar'."
                },
                "programas": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING"
                    },
                    "description": "Lista de nombres de programas o juegos a desinstalar (ej. ['Spotify'], ['VirtualBox'])."
                }
            },
            "required": ["programas"]
        }
    },
    {
        "name": "file_locator",
        "description": "Escanea el disco duro de la PC para buscar archivos, fotos, documentos, carpetas o archivos comprimidos. Úsalo si el usuario dice 'busca mis fotos', 'dónde está el archivo X', 'qué archivos RAR tengo' o 'encuentra mi proyecto'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "nombre": {"type": "STRING", "description": "Una palabra clave del nombre del archivo (ej. 'proyecto', 'vacaciones'). Déjalo vacío si solo busca por extensión."},
                "extension": {"type": "STRING", "description": "La extensión del archivo si aplica (ej. '.rar', '.jpg', '.pdf', '.docx'). Déjalo vacío si no especificó ninguna."}
            },
            "required": []
        }
    },
    {
        "name": "accessibility",
        "description": (
            "Control de accesibilidad del sistema. "
            "Acciones: 'volume_up', 'volume_down', 'mute' (controlar audio), "
            "'read_clipboard' (leer texto seleccionado o copiado para el usuario), "
            "'screen_off' (apagar pantalla), 'lock_pc' (bloquear equipo)."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING", 
                    "description": "volume_up | volume_down | mute | read_clipboard | screen_off | lock_pc"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "accessibility_advanced",
        "description": (
            "Modulo de accesibilidad universal avanzado. "
            "Incluye: task_simplify (descomponer tareas complejas en pasos simples), "
            "emotional (regulacion emocional y analisis de tono de voz), "
            "routine (rutinas diarias gamificadas con racha y progreso), "
            "eye_tracking (control por seguimiento ocular con webcam), "
            "micro_movement (navegacion por movimientos de cabeza), "
            "speech_config (ajustar tolerancia del reconocimiento de voz)."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "task_simplify | emotional | routine | eye_tracking | micro_movement | speech_config | feedback | config"
                },
                "text": {"type": "STRING", "description": "Texto a simplificar (para task_simplify)"},
                "format": {"type": "STRING", "description": "Formato: steps (default) | summary | explain"},
                "name": {"type": "STRING", "description": "Nombre de rutina (para routine add/complete)"},
                "setting": {"type": "STRING", "description": "Clave de configuracion a ver o cambiar"},
                "value": {"type": "STRING", "description": "Valor para la configuracion"},
                "level": {"type": "NUMBER", "description": "Nivel de tolerancia (0.1-1.0) o sensibilidad"},
                "stress_level": {"type": "NUMBER", "description": "Nivel de estres estimado (0.0-1.0)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "remote_assistant",
        "description": "Enciende o apaga el servidor remoto de Telegram (JARVIS Móvil) para recibir comandos desde el exterior celular.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "activar | desactivar"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "security_biometrics",
        "description": "Activa o desactiva la seguridad biométrica: el centinela de bloqueo facial con la cámara y la seguridad de voz.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "activar_facial | desactivar_facial | activar_voz | desactivar_voz"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "screen_summarizer",
        "description": "Extrae automáticamente todo el texto de la pantalla activa (web, PDF, artículo) usando Ctrl+A y Ctrl+C, y te lo devuelve para que lo resumas. USAR SIEMPRE que el usuario diga: 'resúmeme la pantalla', 'qué dice este artículo', 'mucho texto', 'resume lo que estoy viendo' o 'de qué trata esto'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "summarize"}
            },
            "required": []
        }
    },
    {
        "name": "file_controller",
        "description": "Controlador avanzado de archivos y papelera. Puede eliminar, restaurar, vaciar papelera o eliminar definitivamente archivos y carpetas automáticamente sin pedir confirmación adicional.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "Acción a ejecutar. Ejemplos: eliminar, delete, restore, restaurar, vaciar_papelera, eliminar_definitivo."},
                "file_name": {"type": "STRING", "description": "Nombre o ruta del archivo/carpeta. No es necesario para vaciar la papelera."}
            },
            "required": ["action"]
        }
    },
    {
        "name": "desktop_control",
        "description": (
            "Controls the desktop: wallpaper, organize, clean, list, stats. "
            "When the user says to use a file from a directory (e.g. 'el archivo X del escritorio'), "
            "use search_name + search_path to auto-find the file before applying the action."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "wallpaper | wallpaper_url | organize | clean | list | stats | task"},
                "path":        {"type": "STRING", "description": "Image path for wallpaper"},
                "url":         {"type": "STRING", "description": "Image URL for wallpaper_url"},
                "mode":        {"type": "STRING", "description": "by_type or by_date for organize"},
                "task":        {"type": "STRING", "description": "Natural language desktop task"},
                "search_name": {"type": "STRING", "description": "Filename to search for in a directory (auto-finds full path)"},
                "search_path": {"type": "STRING", "description": "Directory to search: desktop, downloads, documents, pictures, home (default: desktop)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "deep_work",
        "description": "Activa el modo de estudio, trabajo profundo o concentración extrema por una cantidad de minutos determinada. Bloquea juegos y webs. Úsalo cuando el usuario diga 'voy a estudiar', 'activa modo concentración', 'bloquea las distracciones'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "minutos": {"type": "INTEGER", "description": "La cantidad de minutos que durará el bloqueo."}
            },
            "required": ["minutos"]
        }
    },
    {
        "name": "code_helper",
        "description": "Writes, edits, explains, runs, or builds code files.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "write | edit | explain | run | build | auto (default: auto)"},
                "description": {"type": "STRING", "description": "What the code should do or what change to make"},
                "language":    {"type": "STRING", "description": "Programming language (default: python)"},
                "output_path": {"type": "STRING", "description": "Where to save the file"},
                "file_path":   {"type": "STRING", "description": "Path to existing file for edit/explain/run/build"},
                "code":        {"type": "STRING", "description": "Raw code string for explain"},
                "args":        {"type": "STRING", "description": "CLI arguments for run/build"},
                "timeout":     {"type": "INTEGER", "description": "Execution timeout in seconds (default: 30)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "dev_agent",
        "description": "Builds complete multi-file projects from scratch: plans, writes files, installs deps, opens VSCode, runs and fixes errors.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "description":  {"type": "STRING", "description": "What the project should do"},
                "language":     {"type": "STRING", "description": "Programming language (default: python)"},
                "project_name": {"type": "STRING", "description": "Optional project folder name"},
                "timeout":      {"type": "INTEGER", "description": "Run timeout in seconds (default: 30)"}
            },
            "required": ["description"]
        }
    },
    {
        "name": "agent_task",
        "description": (
            "Executes complex multi-step tasks requiring multiple different tools. "
            "Examples: 'research X and save to file', 'find and organize files'. "
            "DO NOT use for single commands. NEVER use for Steam/Epic — use game_updater."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "goal":     {"type": "STRING", "description": "Complete description of what to accomplish"},
                "priority": {"type": "STRING", "description": "low | normal | high (default: normal)"}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "computer_control",
        "description": (
            "Control directo del teclado y mouse de la computadora. "
            "HERRAMIENTA OBLIGATORIA PARA PROGRAMACIÓN: Si el usuario pide que escribas código en su entorno de desarrollo "
            "(VS Code, Visual Studio, IntelliJ, MySQL, etc.), USA ESTA HERRAMIENTA. "
            "Si es un fragmento corto, usa action='smart_type' para teclearlo como un humano. "
            "Si es una clase grande o mucho código, usa action='paste' para pegarlo instantáneamente y respetar la indentación. "
            "Pon el código a escribir en el parámetro 'text'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "type | smart_type | click | double_click | right_click | hotkey | press | scroll | move | copy | paste | screenshot | wait | clear_field | focus_window | screen_find | screen_click | random_data | user_data"},
                "text":        {"type": "STRING", "description": "El código completo a pegar, o el texto a teclear"},
                "x":           {"type": "INTEGER", "description": "X coordinate"},
                "y":           {"type": "INTEGER", "description": "Y coordinate"},
                "keys":        {"type": "STRING", "description": "Key combination e.g. 'ctrl+c'"},
                "key":         {"type": "STRING", "description": "Single key e.g. 'enter'"},
                "direction":   {"type": "STRING", "description": "up | down | left | right"},
                "amount":      {"type": "INTEGER", "description": "Scroll amount (default: 3)"},
                "seconds":     {"type": "NUMBER",  "description": "Seconds to wait"},
                "title":       {"type": "STRING",  "description": "Window title for focus_window"},
                "description": {"type": "STRING",  "description": "Element description for screen_find/screen_click"},
                "type":        {"type": "STRING",  "description": "Data type for random_data"},
                "field":       {"type": "STRING",  "description": "Field for user_data: name|email|city"},
                "clear_first": {"type": "BOOLEAN", "description": "Clear field before typing (default: true)"},
                "path":        {"type": "STRING",  "description": "Save path for screenshot"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "game_updater",
        "description": (
            "THE ONLY tool for ANY Steam or Epic Games request. "
            "Use for: installing, downloading, updating games, listing installed games, "
            "checking download status, scheduling updates. "
            "ALWAYS call directly for any Steam/Epic/game request. "
            "NEVER use agent_task, browser_control, or web_search for Steam/Epic."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":    {"type": "STRING",  "description": "update | install | list | download_status | schedule | cancel_schedule | schedule_status (default: update)"},
                "platform":  {"type": "STRING",  "description": "steam | epic | both (default: both)"},
                "game_name": {"type": "STRING",  "description": "Game name (partial match supported)"},
                "app_id":    {"type": "STRING",  "description": "Steam AppID for install (optional)"},
                "hour":      {"type": "INTEGER", "description": "Hour for scheduled update 0-23 (default: 3)"},
                "minute":    {"type": "INTEGER", "description": "Minute for scheduled update 0-59 (default: 0)"},
                "shutdown_when_done": {"type": "BOOLEAN", "description": "Shut down PC when download finishes"}
            },
            "required": []
        }
    },
    {
        "name": "flight_finder",
        "description": "Searches Google Flights and speaks the best options.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "origin":      {"type": "STRING",  "description": "Departure city or airport code"},
                "destination": {"type": "STRING",  "description": "Arrival city or airport code"},
                "date":        {"type": "STRING",  "description": "Departure date (any format)"},
                "return_date": {"type": "STRING",  "description": "Return date for round trips"},
                "passengers":  {"type": "INTEGER", "description": "Number of passengers (default: 1)"},
                "cabin":       {"type": "STRING",  "description": "economy | premium | business | first"},
                "save":        {"type": "BOOLEAN", "description": "Save results to Notepad"}
            },
            "required": ["origin", "destination", "date"]
        }
    },
    {
        "name": "shutdown_jarvis",
        "description": (
            "Shuts down the assistant completely. "
            "Call this when the user expresses intent to end the conversation, "
            "close the assistant, say goodbye, or stop Jarvis. "
            "The user can say this in ANY language."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "file_processor",
        "description": (
            "Processes any file that the user has uploaded or dropped onto the interface. "
            "Use this when the user refers to an uploaded file and wants an action on it. "
            "Supports: images (describe/ocr/resize/compress/convert), "
            "PDFs (summarize/extract_text/to_word), "
            "Word docs & text files (summarize/fix/reformat/translate), "
            "CSV/Excel (analyze/stats/filter/sort/convert), "
            "JSON/XML (validate/format/analyze), "
            "code files (explain/review/fix/optimize/run/document/test), "
            "audio (transcribe/trim/convert/info), "
            "video (trim/extract_audio/extract_frame/compress/transcribe/info), "
            "archives (list/extract), "
            "presentations (summarize/extract_text). "
            "ALWAYS call this tool when a file has been uploaded and the user gives a command about it. "
            "If the user's command is ambiguous, pick the most logical action for that file type."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_path": {
                    "type": "STRING",
                    "description": "Full path to the uploaded file. Leave empty to use the currently uploaded file."
                },
                "action": {
                    "type": "STRING",
                    "description": (
                        "What to do with the file. Examples by type:\n"
                        "image: describe | ocr | resize | compress | convert | info\n"
                        "pdf: summarize | extract_text | to_word | info\n"
                        "docx/txt: summarize | fix | reformat | translate_hint | word_count | to_bullet\n"
                        "csv/excel: analyze | stats | filter | sort | convert | info\n"
                        "json: validate | format | analyze | to_csv\n"
                        "code: explain | review | fix | optimize | run | document | test\n"
                        "audio: transcribe | trim | convert | info\n"
                        "video: trim | extract_audio | extract_frame | compress | transcribe | info | convert\n"
                        "archive: list | extract\n"
                        "pptx: summarize | extract_text | analyze"
                    )
                },
                "instruction": {
                    "type": "STRING",
                    "description": "Free-form instruction if action doesn't cover it. E.g. 'translate this to Turkish', 'find all email addresses'"
                },
                "format": {"type": "STRING", "description": "Target format for conversion. E.g. 'mp3', 'pdf', 'csv', 'png'"},
                "width":     {"type": "INTEGER", "description": "Target width for image resize"},
                "height":    {"type": "INTEGER", "description": "Target height for image resize"},
                "scale":     {"type": "NUMBER",  "description": "Scale factor for image resize (e.g. 0.5)"},
                "quality":   {"type": "INTEGER", "description": "Quality 1-100 for image/video compress"},
                "start":     {"type": "STRING",  "description": "Start time for trim: seconds or HH:MM:SS"},
                "end":       {"type": "STRING",  "description": "End time for trim: seconds or HH:MM:SS"},
                "timestamp": {"type": "STRING",  "description": "Timestamp for video frame extraction HH:MM:SS"},
                "column":    {"type": "STRING",  "description": "Column name for CSV filter/sort"},
                "value":     {"type": "STRING",  "description": "Filter value for CSV filter"},
                "condition": {"type": "STRING",  "description": "Filter condition: equals|contains|gt|lt"},
                "ascending": {"type": "BOOLEAN", "description": "Sort order for CSV sort (default: true)"},
                "save":      {"type": "BOOLEAN", "description": "Save result to file (default: true)"},
                "destination": {"type": "STRING", "description": "Output folder for archive extract"}
            },
            "required": []
        }
    },
    {
        "name": "google_calendar",
        "description": (
            "Manages the user's Google Calendar: create, list, edit, or delete events. "
            "Use for ANY request about calendar events, appointments, reminders with dates, "
            "scheduling meetings, or checking what's coming up. "
            "ALWAYS call this tool for calendar requests — never simulate. "
            "For 'list': shows upcoming events. "
            "For 'create': needs summary and start (end defaults to +1h). "
            "For 'edit'/'delete': needs event_id (get it from 'list' first)."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING",  "description": "list | create | edit | delete"},
                "summary":     {"type": "STRING",  "description": "Event title/name"},
                "start":       {"type": "STRING",  "description": "Start date/time: ISO, YYYY-MM-DD HH:MM, or DD/MM/YYYY HH:MM"},
                "end":         {"type": "STRING",  "description": "End date/time (optional — defaults to start + 1 hour)"},
                "description": {"type": "STRING",  "description": "Event notes or description"},
                "location":    {"type": "STRING",  "description": "Event location"},
                "event_id":    {"type": "STRING",  "description": "Event ID (first 8 chars from list) for edit/delete"},
                "days_ahead":  {"type": "INTEGER", "description": "Days to look ahead for list (default: 7)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "spotify_control",
        "description": (
            "Control total de Spotify: reproducir, pausar, siguiente, anterior, volumen, "
            "buscar canciones/artistas/álbumes/playlists, aleatorio, repetir, ver qué suena, "
            "guardar canciones, ver dispositivos. "
            "SIEMPRE llamar esta herramienta para CUALQUIER pedido relacionado con Spotify o música."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "play | pause | resume | next | previous | volume | shuffle | repeat | current | search | like | devices | playlist"},
                "query":  {"type": "STRING", "description": "Búsqueda para play/search: canción, artista, álbum o playlist"},
                "type":   {"type": "STRING", "description": "track | album | playlist | artist (default: track)"},
                "value":  {"type": "STRING", "description": "Valor para volume (0-100), shuffle (true/false), repeat (off/track/context)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "rgb_control",
        "description": (
            "Controla las luces RGB de periféricos y componentes de la PC (teclado, mouse, GPU, RAM, etc.). "
            "Requiere OpenRGB corriendo con servidor SDK activado. "
            "Usar para: cambiar color, apagar, brillo, efectos, arco iris."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":     {"type": "STRING", "description": "set_color | off | brightness | effect | rainbow | list"},
                "color":      {"type": "STRING", "description": "Color: nombre (rojo, azul, verde, blanco…) o hex #RRGGBB"},
                "brightness": {"type": "INTEGER", "description": "Brillo 0-100 (default: 100)"},
                "device":     {"type": "STRING", "description": "Filtro por nombre de dispositivo (opcional, aplica a todos si se omite)"},
                "effect":     {"type": "STRING", "description": "Nombre del efecto para la acción effect"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "scheduler",
        "description": (
            "Crea, lista, elimina o ejecuta automatizaciones programadas (tareas recurrentes). "
            "Ejemplos: backup diario, notificaciones, scripts automáticos. "
            "Usar para CUALQUIER pedido de 'todos los días a las X', 'cada semana', 'automatizar'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":           {"type": "STRING",  "description": "list | create | delete | enable | disable | run_now"},
                "name":             {"type": "STRING",  "description": "Nombre descriptivo de la tarea"},
                "frequency":        {"type": "STRING",  "description": "daily | weekly | interval | once"},
                "hour":             {"type": "INTEGER", "description": "Hora de ejecución (0-23)"},
                "minute":           {"type": "INTEGER", "description": "Minuto de ejecución (0-59)"},
                "weekday":          {"type": "STRING",  "description": "Día de la semana para frequency=weekly"},
                "interval_minutes": {"type": "INTEGER", "description": "Intervalo en minutos para frequency=interval"},
                "task_action":      {"type": "STRING",  "description": "backup | file_controller | notify | custom_script | browser_control"},
                "task_parameters":  {"type": "OBJECT",  "description": "Parámetros de la tarea (source, destination para backup, etc.)"},
                "task_id":          {"type": "STRING",  "description": "ID de la tarea (primeros 6 chars) para delete/enable/disable/run_now"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "google_drive",
        "description": (
            "Gestiona Google Drive: listar archivos, buscar, subir, descargar, crear carpetas, eliminar, compartir. "
            "SIEMPRE usar para cualquier pedido sobre Google Drive."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "list | search | upload | download | create_folder | delete | share | info"},
                "folder_id":   {"type": "STRING", "description": "ID de la carpeta (default: root)"},
                "file_id":     {"type": "STRING", "description": "ID del archivo para download/delete/share/info"},
                "path":        {"type": "STRING", "description": "Ruta local para upload"},
                "name":        {"type": "STRING", "description": "Nombre de la nueva carpeta"},
                "query":       {"type": "STRING", "description": "Término de búsqueda"},
                "destination": {"type": "STRING", "description": "Carpeta local de destino para download"},
                "email":       {"type": "STRING", "description": "Email para compartir"},
                "role":        {"type": "STRING", "description": "reader | writer | commenter"},
                "confirm":     {"type": "BOOLEAN", "description": "true para confirmar eliminación"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "gmail_control",
        "description": (
            "Gestiona Gmail: leer bandeja, leer correo, enviar, responder, buscar, archivar, eliminar. "
            "SIEMPRE usar para cualquier pedido sobre correo electrónico o Gmail."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":     {"type": "STRING",  "description": "inbox | read | send | reply | search | archive | delete | mark_read | labels"},
                "count":      {"type": "INTEGER", "description": "Cantidad de correos a listar/buscar (default: 5)"},
                "message_id": {"type": "STRING",  "description": "ID del mensaje para read/reply/archive/delete/mark_read"},
                "to":         {"type": "STRING",  "description": "Destinatario para send"},
                "subject":    {"type": "STRING",  "description": "Asunto para send"},
                "body":       {"type": "STRING",  "description": "Cuerpo del correo para send/reply"},
                "query":      {"type": "STRING",  "description": "Búsqueda Gmail para search (ej: 'from:juan', 'subject:factura')"},
                "confirm":    {"type": "BOOLEAN", "description": "true para confirmar eliminación"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "google_maps",
        "description": (
            "Muestra rutas de navegación y mapas interactivos. "
            "Usar para: cómo llegar a un lugar, cuánto tarda, indicaciones paso a paso, "
            "buscar una dirección en el mapa. Abre mapa JARVIS en Chrome con la ruta marcada. "
            "SIEMPRE llamar para cualquier pedido de navegación, rutas o mapas."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "directions | search"},
                "origin":      {"type": "STRING", "description": "Punto de partida (dirección, ciudad, lugar)"},
                "destination": {"type": "STRING", "description": "Destino (dirección, ciudad, lugar)"},
                "mode":        {"type": "STRING", "description": "car (auto) | walk (caminando) | bike (bicicleta). Default: car"},
                "query":       {"type": "STRING", "description": "Lugar a buscar en el mapa (para action=search)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "rules_engine",
        "description": (
            "Motor de automatizaciones y alertas inteligentes. "
            "USAR SIEMPRE cuando el usuario pida: 'cuando diga X hacé Y', 'cada vez que diga X', "
            "'si digo X abrí/poné/hacé Y', 'quiero que cuando diga X...'. "
            "Soporta: phrase triggers (frase → acción), time triggers (hora → acción), alertas. "
            "Listar, crear, eliminar, habilitar/deshabilitar automaciones. "
            "CONDITION types: phrase (frase del usuario), time (hora del día), file_exists, always. "
            "ACTION types: open_app, spotify_play, browser, smart_home, composite (múltiples), notify, speak, run_script."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":     {"type": "STRING", "description": "list | list_phrases | create | delete | enable | disable | trigger | alert"},
                "name":       {"type": "STRING", "description": "Nombre de la automatización"},
                "rule_id":    {"type": "STRING", "description": "ID de la regla para delete/enable/disable/trigger"},
                "condition":  {
                    "type": "OBJECT",
                    "description": (
                        "Condición. phrase: {type:phrase, trigger:'texto exacto', match:contains|exact|startswith}. "
                        "time: {type:time, hour:8, minute:0, days:[monday,...]}. "
                        "file_exists: {type:file_exists, path:'...'}. always: {type:always}"
                    )
                },
                "action_def": {
                    "type": "OBJECT",
                    "description": (
                        "Acción a ejecutar. "
                        "open_app: {type:open_app, app_name:'Spotify'}. "
                        "spotify_play: {type:spotify_play, query:'Back in Black AC/DC'}. "
                        "browser: {type:browser, url:'https://...'}. "
                        "smart_home: {type:smart_home, device:'living', action:'on'}. "
                        "composite: {type:composite, actions:[{...},{...}]}. "
                        "notify: {type:notify, message:'...'}. speak: {type:speak, message:'...'}. "
                        "run_script: {type:run_script, command:'...'}"
                    )
                },
                "message":    {"type": "STRING", "description": "Mensaje para action=alert"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "user_profile",
        "description": (
            "Perfil dinámico del usuario — hábitos, preferencias, historial de uso. "
            "Ver perfil, configurar preferencias, ver hábitos aprendidos, guardar notas personales. "
            "JARVIS aprende automáticamente los patrones del usuario."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "view | set_preference | set_name | add_note | notes | habits | reset"},
                "key":    {"type": "STRING", "description": "Clave de preferencia (ej: idioma, tema, ciudad)"},
                "value":  {"type": "STRING", "description": "Valor de la preferencia"},
                "name":   {"type": "STRING", "description": "Nombre del usuario"},
                "note":   {"type": "STRING", "description": "Nota personal a guardar"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "goals",
        "description": (
            "Sistema de objetivos persistentes a largo plazo. "
            "Crear metas, trackear progreso, marcar pasos completados. "
            "Usar para: metas personales, proyectos, hábitos, objetivos con deadline. "
            "SIEMPRE usar para pedidos de 'quiero lograr X', 'mi objetivo es', 'meta de'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING",  "description": "list | create | update_progress | complete | complete_step | add_step | delete | detail"},
                "goal_id":     {"type": "STRING",  "description": "ID del objetivo para update/complete/delete/detail"},
                "title":       {"type": "STRING",  "description": "Título del objetivo"},
                "description": {"type": "STRING",  "description": "Descripción detallada"},
                "deadline":    {"type": "STRING",  "description": "Fecha límite ISO (YYYY-MM-DD)"},
                "progress":    {"type": "INTEGER", "description": "Progreso 0-100"},
                "steps":       {"type": "ARRAY",   "items": {"type": "STRING"}, "description": "Lista de pasos del objetivo"},
                "step":        {"type": "STRING",  "description": "Texto del nuevo paso (add_step)"},
                "step_index":  {"type": "INTEGER", "description": "Índice del paso a completar (0-based)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "git_control",
        "description": (
            "Integración completa con Git: status, log, diff, commit automático, "
            "branches, pull, push, stash, análisis de cambios. "
            "Usar para CUALQUIER pedido relacionado con Git o control de versiones."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING",  "description": "status | log | diff | commit | add | branches | branch_create | checkout | pull | push | stash | analyze"},
                "repo_path":   {"type": "STRING",  "description": "Ruta al repositorio Git"},
                "message":     {"type": "STRING",  "description": "Mensaje del commit"},
                "branch_name": {"type": "STRING",  "description": "Nombre de la rama"},
                "remote":      {"type": "STRING",  "description": "Remote (default: origin)"},
                "n":           {"type": "INTEGER", "description": "Número de commits para log"},
                "file":        {"type": "STRING",  "description": "Archivo específico para diff"},
                "staged":      {"type": "BOOLEAN", "description": "Mostrar diff staged"},
                "add_all":     {"type": "BOOLEAN", "description": "Agregar todos los archivos antes del commit (default: true)"},
                "files":       {"type": "ARRAY",   "items": {"type": "STRING"}, "description": "Archivos para add"},
                "sub":         {"type": "STRING",  "description": "Subcomando para stash: push|pop|list"}
            },
            "required": ["action", "repo_path"]
        }
    },
    {
        "name": "codebase",
        "description": (
            "Indexación y búsqueda inteligente de proyectos de código. "
            "Indexar proyectos, buscar en archivos, encontrar símbolos (funciones/clases), "
            "generar documentación automática, búsqueda avanzada de código. "
            "Usar para: 'buscar en mi proyecto', 'dónde está la función X', 'generar docs', 'indexar mi código'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":    {"type": "STRING", "description": "index | list | info | search | find_symbol | generate_docs | remove"},
                "path":      {"type": "STRING", "description": "Ruta del proyecto a indexar"},
                "name":      {"type": "STRING", "description": "Nombre del proyecto (default: nombre de carpeta)"},
                "project":   {"type": "STRING", "description": "Nombre del proyecto para info/search/find_symbol"},
                "query":     {"type": "STRING", "description": "Texto a buscar en el código"},
                "symbol":    {"type": "STRING", "description": "Nombre de función/clase a buscar"},
                "file_path": {"type": "STRING", "description": "Ruta del archivo para generate_docs"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "knowledge_base",
        "description": (
            "Segundo cerebro / base de conocimiento personal. "
            "Guardar notas, ideas, snippets de código, referencias, hechos, preguntas. "
            "Buscar en el conocimiento guardado, exportar. "
            "Usar para: 'recordá que...', 'guardá esta idea', 'anotá este código', 'buscar en mis notas'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":   {"type": "STRING", "description": "add/save/store | search/find | list | get/read/view | update | delete | stats | export"},
                "title":    {"type": "STRING", "description": "Título de la entrada"},
                "content":  {"type": "STRING", "description": "Contenido o texto a guardar"},
                "type":     {"type": "STRING", "description": "note | idea | snippet | reference | fact | task | question"},
                "tags":     {"type": "STRING", "description": "Tags separados por coma (ej: python, jarvis, idea)"},
                "query":    {"type": "STRING", "description": "Búsqueda en la base de conocimiento"},
                "entry_id": {"type": "STRING", "description": "ID de la entrada para get/update/delete"},
                "path":     {"type": "STRING", "description": "Ruta para exportar (action=export)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "social_media",
        "description": (
            "Controla redes sociales: Twitter/X, Instagram, TikTok y LinkedIn. "
            "Twitter: publicar tweets, ver timeline, buscar, like, retweet, ver perfil. "
            "Instagram: publicar fotos, subir historias, enviar DMs, ver feed, like, comentar. "
            "TikTok: subir videos, ver perfil/stats, tendencias. "
            "LinkedIn: publicar posts, ver perfil, ver feed, enviar mensajes. "
            "SIEMPRE usar para cualquier pedido de redes sociales. "
            "Para WhatsApp usar la herramienta 'whatsapp'. "
            "Usá action=setup para ver cómo configurar las credenciales."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "platform": {"type": "STRING", "description": "twitter | instagram | tiktok | linkedin | setup"},
                "action":   {"type": "STRING", "description": (
                    "Twitter: tweet, delete_tweet, like, retweet, timeline, search_tweets, my_tweets, profile | "
                    "Instagram: post/upload_photo, story, send_dm, feed, profile, like, comment | "
                    "TikTok: upload/publicar, profile/perfil, trending | "
                    "LinkedIn: post/publicar, profile/perfil, send_message/mensaje, feed"
                )},
                "text":       {"type": "STRING", "description": "Texto del tweet/post/comentario/mensaje"},
                "content":    {"type": "STRING", "description": "Contenido del post (LinkedIn/TikTok)"},
                "tweet_id":   {"type": "STRING", "description": "ID del tweet para like/retweet/delete"},
                "media_id":   {"type": "STRING", "description": "ID del post de Instagram para like/comment"},
                "username":   {"type": "STRING", "description": "Usuario para DM/perfil (Instagram, TikTok, LinkedIn)"},
                "receiver":   {"type": "STRING", "description": "Destinatario del DM de Instagram"},
                "image_path": {"type": "STRING", "description": "Ruta imagen para Instagram/LinkedIn"},
                "video_path": {"type": "STRING", "description": "Ruta del video para TikTok"},
                "caption":    {"type": "STRING", "description": "Descripción/caption de la foto o video"},
                "query":      {"type": "STRING", "description": "Búsqueda de tweets"},
                "count":      {"type": "INTEGER", "description": "Cantidad de resultados (default: 5)"}
            },
            "required": ["platform", "action"]
        }
    },
    {
        "name": "save_memory",
        "description": (
            "Save an important personal fact about the user to long-term memory. "
            "Call this silently whenever the user reveals something worth remembering: "
            "name, age, city, job, preferences, hobbies, relationships, projects, or future plans. "
            "Do NOT call for: weather, reminders, searches, or one-time commands. "
            "Do NOT announce that you are saving — just call it silently. "
            "Values must be in English regardless of the conversation language."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category": {
                    "type": "STRING",
                    "description": (
                        "identity — name, age, birthday, city, job, language, nationality | "
                        "preferences — favorite food/color/music/film/game/sport, hobbies | "
                        "projects — active projects, goals, things being built | "
                        "relationships — friends, family, partner, colleagues | "
                        "wishes — future plans, things to buy, travel dreams | "
                        "notes — habits, schedule, anything else worth remembering"
                    )
                },
                "key":   {"type": "STRING", "description": "Short snake_case key (e.g. name, favorite_food, sister_name)"},
                "value": {"type": "STRING", "description": "Concise value in English (e.g. Fatih, pizza, older sister)"}
            },
            "required": ["category", "key", "value"]
        }
    },
    {
        "name": "smart_home",
        "description": (
            "Controla las luces y dispositivos inteligentes del hogar. "
            "Soporta Tuya/Smart Life, Philips Hue, LIFX y Yeelight. "
            "SIEMPRE llamar para: encender/apagar luces, cambiar color, brillo, temperatura de color, "
            "activar escenas, consultar estado. "
            "Si no hay dispositivos configurados, usar action=setup para ver instrucciones."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING",  "description": "on | off | toggle | color | brightness | temperature | scene | status | list | setup"},
                "device":      {"type": "STRING",  "description": "Nombre o sala del dispositivo (ej: 'sala', 'cuarto', 'lampara principal'). Omitir = todos."},
                "color":       {"type": "STRING",  "description": "Color: nombre (rojo, azul, blanco, cálido…) o hex #RRGGBB"},
                "value":       {"type": "INTEGER", "description": "Valor numérico para brightness (1-100) o temperatura Kelvin (1700-9000)"},
                "brightness":  {"type": "INTEGER", "description": "Brillo 1-100 (alternativa a value)"},
                "scene":       {"type": "STRING",  "description": "Nombre de la escena: relajar, leer, trabajar, noche, fiesta"},
                "protocol":    {"type": "STRING",  "description": "tuya | hue | lifx | yeelight. Omitir = usa el configurado por defecto."},
                "group":       {"type": "STRING",  "description": "Nombre del grupo/sala en Philips Hue"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "system_monitor",
        "description": (
            "Monitorea el rendimiento del sistema en tiempo real: CPU, RAM, GPU, discos, "
            "red, temperatura, batería, procesos activos, uptime. "
            "Usar para: '¿cómo está la PC?', 'qué proceso consume más', 'temperatura del CPU', "
            "'cuánta RAM libre tengo', 'matar proceso X', 'resumen de rendimiento'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":   {"type": "STRING",  "description": "cpu | ram | disk | network | gpu | temperature | battery | uptime | processes | kill | report"},
                "sort_by":  {"type": "STRING",  "description": "Para processes: cpu (default) | ram"},
                "count":    {"type": "INTEGER", "description": "Para processes: cantidad a mostrar (default: 10)"},
                "name":     {"type": "STRING",  "description": "Para kill: nombre o PID del proceso"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "tiktok_analyzer",
        "description": (
            "HERRAMIENTA OBLIGATORIA para controlar TikTok sin abrir pestañas nuevas. "
            "Acciones válidas: "
            "'set_profile' (guardar el usuario de TikTok de la persona que habla), "
            "'scroll_down' (bajar video), 'scroll_up' (subir video), "
            "'play_pause' (cuando pidan pausa, play o stop), 'mute' (silenciar), "
            "'search' (buscar), 'view_profile' (ver el perfil del usuario), "
            "'view_activity', 'video_profile', 'send_message' y 'post_video'. "
            "Si el usuario dice 'Mi usuario es @pepito', usa 'set_profile'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "set_profile | scroll_down | scroll_up | play_pause | mute | search | view_profile | view_activity | video_profile | send_message | post_video"},
                "contact":  {"type": "STRING", "description": "Usuario de TikTok para guardar o enviar mensaje."},
                "text":     {"type": "STRING", "description": "Texto de búsqueda o descripción del video."},
                "file_path":{"type": "STRING", "description": "Nombre del video a publicar."}
            },
            "required": ["action"]
        }
    },
    {
        "name": "arca_invoice",
        "description": (
            "Genera comprobantes digitales electrónicos válidos ante ARCA (ex AFIP). "
            "Para Argentina. Soporta Factura A, B, C, Nota de Crédito, Nota de Débito."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":         {"type": "STRING", "description": "generar | listar | historial"},
                "tipo":           {"type": "INTEGER", "description": "1=Factura A, 5=Factura C (default), 6=Factura B. Usá action=listar para ver todos."},
                "razon_social":   {"type": "STRING", "description": "Razón social del receptor"},
                "cuit_receptor":  {"type": "STRING", "description": "CUIT del receptor"},
                "domicilio":      {"type": "STRING", "description": "Domicilio del receptor"},
                "detalle":        {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"descripcion": {"type": "STRING"}, "precio": {"type": "NUMBER"}, "cantidad": {"type": "INTEGER"}}}, "description": "Lista de productos"},
                "importe_neto":   {"type": "NUMBER", "description": "Importe neto gravado"},
                "importe_iva":    {"type": "NUMBER", "description": "Importe de IVA"},
                "iva_pct":        {"type": "NUMBER", "description": "Porcentaje de IVA (default: 21.0). 0 para exento."},
                "fecha":          {"type": "STRING", "description": "Fecha YYYY-MM-DD"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "morning_brief",
        "description": (
            "Genera el informe matutino de JARVIS. "
            "USAR ÚNICAMENTE cuando el usuario pida EXPLÍCITAMENTE: 'dame mi informe', 'brief matutino', o 'resumen del día'. "
            "ESTÁ ESTRICTAMENTE PROHIBIDO usar esta herramienta si el usuario solo dice 'Hola', 'Buenos días', 'Qué onda' o saludos simples."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "force": {"type": "boolean", "description": "Si True, genera el informe aunque ya se haya dado hoy."}
            },
            "required": []
        }
    },
    {
        "name": "vision_guardian",
        "description": (
            "Controla el Guardian de Visión Ambiental de JARVIS — monitoreo proactivo de pantalla. "
            "Analiza la pantalla periódicamente con IA y ofrece ayuda contextual."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["status", "enable", "disable", "check_now", "set_interval"], "description": "Acción: status | enable | disable | check_now | set_interval"},
                "seconds": {"type": "integer", "description": "Para set_interval: segundos entre análisis (30-600)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "accessibility_overlay",
        "description": "Muestra, oculta o alterna la barra flotante de accesibilidad JARVIS sobre el escritorio.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "show — mostrar | hide — cerrar | toggle — alternar | status — estado actual"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "openrouter_agent",
        "description": (
            "Delega una tarea intelectualmente compleja, de análisis o redacción larga a OpenRouter "
            "(un motor de texto alternativo). "
            "Usar cuando el usuario pida: 'usa openrouter para esto', 'consulta a claude', 'usa otro modelo', "
            "'analiza este código largo', 'redacta un ensayo', o cuando percibas que la tarea es puramente de texto avanzado."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "El prompt o instrucción completa para el agente de OpenRouter"},
                "model": {"type": "STRING", "description": "Opcional. Modelo a usar, por defecto google/gemini-2.5-flash"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "chatgpt_agent",
        "description": (
            "Delega una consulta, generación de código compleja, o análisis profundo a ChatGPT (OpenAI). "
            "USAR SIEMPRE que el usuario diga 'pregúntale a chatgpt', 'usa gpt', 'qué opina chatgpt'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "La instrucción detallada o pregunta que le harás a ChatGPT."},
                "model": {"type": "STRING", "description": "gpt-4o, gpt-4o-mini, o o1-preview. Por defecto: gpt-4o"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "terminal_agent",
        "description": (
            "Ejecuta CUALQUIER comando en la terminal de Windows (PowerShell o CMD). "
            "USAR LIBREMENTE como recurso general para CUALQUIER tarea del sistema operativo: "
            "instalar/desinstalar programas (winget, choco, pip), consultar información del sistema, "
            "ejecutar scripts, manejar archivos y carpetas, configurar redes, descargar archivos, "
            "compilar código, matar procesos, gestionar servicios, y CUALQUIER otra operación."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "command": {"type": "STRING", "description": "El comando exacto a ejecutar"},
                "shell": {"type": "STRING", "description": "Shell a usar: powershell (default) o cmd"},
                "timeout": {"type": "INTEGER", "description": "Timeout en segundos (default: 120, max: 600)"},
                "working_directory": {"type": "STRING", "description": "Directorio de trabajo para el comando (opcional)"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "native_ui",
        "description": (
            "Automatización de Interfaz Nativa de Windows (UI Automation). "
            "USAR para listar, enfocar, escribir o hacer clic en ventanas de forma 100% precisa, saltándose la visión. "
            "Esto EVITA errores de cuota (Error 429) y permite simulación exacta de teclado/mouse."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "Acción a realizar: list_windows | focus_window | type_in_window | click_center"},
                "window_title": {"type": "STRING", "description": "El nombre (o parte del nombre) de la ventana destino. (Ej: 'WhatsApp', 'Chrome')"},
                "text": {"type": "STRING", "description": "El texto a escribir (solo si action es type_in_window)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "audio_generator",
        "description": (
            "Genera archivos de audio MP3 a partir de texto usando diferentes voces neuronales "
            "y LOS GUARDA DIRECTAMENTE EN EL ESCRITORIO. "
            "Llama a esta herramienta cuando el usuario pida: 'crea un audio que diga...', "
            "'generame un mp3 con la voz de...', o 'convierte este texto en audio'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "text": {"type": "STRING", "description": "El texto exacto que debe ser hablado y convertido en audio."},
                "voice": {"type": "STRING", "description": "El tipo de voz a usar. Opciones válidas: 'jorge' (locutor), 'dalia' (chica), 'alvaro' (español), 'elena' (argentina), 'narrador'."}
            },
            "required": ["text"]
        }
    },
    {
        "name": "universal_social",
        "description": (
            "Permite a JARVIS enviar mensajes o CUALQUIER archivo (fotos, APKs, RARs, programas) "
            "por CUALQUIER red social (WhatsApp, Telegram, Instagram, Messenger, o apps nativas). "
            "Usa platform_type='desktop' para abrir las aplicaciones de escritorio de Windows, o 'web' para el navegador."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {"type": "STRING", "description": "Nombre de la red social (WhatsApp, Telegram, Discord, etc.)"},
                "platform_type": {"type": "STRING", "description": "'desktop' para usar la app de Windows, 'web' para el navegador"},
                "contact": {"type": "STRING", "description": "Nombre o número del contacto / usuario"},
                "message": {"type": "STRING", "description": "El mensaje de texto a enviar (opcional si solo envías archivo)"},
                "file_path": {"type": "STRING", "description": "La ruta completa del archivo en la PC a enviar (opcional)"}
            },
            "required": ["app_name", "contact"]
        }
    },
    {
        "name": "tool_creator",
        "description": (
            "Permite a JARVIS programar e instalar sus propias herramientas. "
            "ÚSALO SIEMPRE que el usuario te pida que aprendas a hacer algo nuevo, o si necesitas una funcionalidad que no tienes preinstalada. "
            "Escribirás el código Python y se instalará automáticamente."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "tool_name": {"type": "STRING", "description": "Nombre de la herramienta en snake_case"},
                "description": {"type": "STRING", "description": "Descripción clara de la herramienta y para qué sirve"},
                "parameters_schema": {"type": "STRING", "description": "El bloque de 'properties' del JSON schema en formato string válido. Ej: '{\"accion\": {\"type\": \"STRING\"}}'"},
                "python_code": {"type": "STRING", "description": "Código Python con la función def <tool_name>(parameters: dict, player=None, speak=None) -> str:"}
            },
            "required": ["tool_name", "description", "parameters_schema", "python_code"]
        }
    },
    {
        "name": "dependency_installer",
        "description": "Tu herramienta de Auto-Sanación en caliente. Úsala SIEMPRE que intentes ejecutar código (auto_programmer / code_helper) y detectes un error de 'ModuleNotFoundError' o 'ImportError', o si el usuario te lo pide. Explícale al usuario que falta una dependencia y pregúntale: '¿Deseas que la instale por ti?'. Si dice que SÍ, ejecuta esta herramienta con los nombres de las librerías. Una vez instaladas, la herramienta refrescará la memoria, así que DEBES reintentar inmediatamente la acción original que estabas haciendo sin que el usuario te lo vuelva a pedir.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "packages": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Lista de nombres exactos de las librerías de Python a instalar (ej. ['qrcode', 'speedtest-cli'])."}
            },
            "required": ["packages"]
        }
    },
    {
        "name": "proactive_automation",
        "description": "Gestiona reglas complejas basadas en el uso y hábitos del sistema operativo para optimizar el rendimiento y automatizar recordatorios proactivos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "add_rule (añadir regla) | list_rules (listar) | delete_rule (eliminar) | trigger_check (evaluar reglas activas)"},
                "rule_name": {"type": "STRING", "description": "Nombre identificativo de la regla de automatización"},
                "trigger": {"type": "STRING", "description": "Disparador: cpu_high | ram_high | time_of_day | app_open"},
                "trigger_value": {"type": "STRING", "description": "Valor del disparador (ej. '85' para 85% cpu, '22:00' para hora, 'chrome.exe' para app)"},
                "action_to_take": {"type": "STRING", "description": "Acción a ejecutar (ej. 'optimize_ram', 'mute_system', 'run_script')"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "file_scanner",
        "description": (
            "Radar de Archivos. OBLIGATORIO usar esto cuando el usuario te pida enviar un archivo pero NO te diga el nombre exacto "
            "(ejemplos: 'manda un video', 'envía una foto', 'quiero mandarle un documento a Carlos', 'pásale un rar'). "
            "Esta herramienta escanea la PC y te devuelve una lista de los 5 archivos más recientes de ese tipo. "
            "Tú debes leerle esa lista al usuario en voz alta y preguntarle cuál quiere. Cuando el usuario responda, "
            "entonces usarás la herramienta de redes sociales para enviarlo."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_type": {"type": "STRING", "description": "El tipo de archivo a buscar. Usa SOLO uno de estos: 'video', 'image', 'document', 'archive', 'audio'."}
            },
            "required": ["file_type"]
        }
    },
    {
        "name": "system_updater",
        "description": "Sistema de auto-actualización y recompilación de JARVIS. Permite recompilar el código fuente localmente en un ejecutable (.exe) o descargar e instalar una actualización OTA desde la nube (GitHub).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "local | github"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "unified_communications",
        "description": "Gestión unificada de comunicaciones. Permite leer, enviar y organizar mensajes y notificaciones en WhatsApp, Telegram, Discord y Gmail desde esta única interfaz.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "platform": {"type": "STRING", "description": "Plataforma de comunicación: whatsapp | telegram | discord | gmail"},
                "action": {"type": "STRING", "description": "send_message (enviar mensaje)"},
                "recipient": {"type": "STRING", "description": "Destinatario: número telefónico para WhatsApp, ID de chat o token para Telegram, Webhook URL para Discord, o email para Gmail"},
                "message": {"type": "STRING", "description": "Contenido del mensaje a enviar"},
                "subject": {"type": "STRING", "description": "Asunto del correo (solo aplica para Gmail)"},
                "token": {"type": "STRING", "description": "Token de Bot opcional para Telegram"}
            },
            "required": ["platform", "action", "recipient", "message"]
        }
    },
    {
        "name": "smart_file_organizer",
        "description": "Análisis y organización inteligente de archivos. Clasifica por categorías, detecta duplicados reales mediante hash MD5 y analiza espacio disponible en disco.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "organize (clasificar por tipo) | find_duplicates (buscar duplicados MD5) | disk_space (analizar espacio)"},
                "directory": {"type": "STRING", "description": "Ruta absoluta del directorio a analizar. Por defecto usa la carpeta Descargas."}
            },
            "required": ["action"]
        }
    },
    {
        "name": "contextual_control",
        "description": "Control contextual de entorno. Ajusta dinámicamente volumen, brillo, plan de energía y estado de Focus Assist (No Molestar) basándose en la ventana activa o comandos manuales.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "adjust_context (auto-ajustar por ventana activa) | set_volume (fijar volumen) | set_brightness (fijar brillo) | set_power_plan (energía) | set_dnd (no molestar)"},
                "volume": {"type": "INTEGER", "description": "Nivel de volumen maestro (0-100)"},
                "brightness": {"type": "INTEGER", "description": "Nivel de brillo de la pantalla (0-100)"},
                "power_plan": {"type": "STRING", "description": "Plan de energía de Windows: balanced | high_performance | power_saver"},
                "state": {"type": "STRING", "description": "Estado de No Molestar (Focus Assist): on | off | alarms"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "camera_bus",
        "description": "Activa la cámara/webcam, captura lo que el usuario tiene en la mano y analiza el objeto con IA visual de forma precisa. Debe usarse cuando el usuario diga qué tengo en la mano, mira esto, analiza este objeto, describe este producto o similares.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Pregunta o instrucción sobre lo que se está mostrando a la cámara."},
                "text": {"type": "STRING", "description": "Alternativa a query."},
                "question": {"type": "STRING", "description": "Alternativa a query."},
                "camera_index": {"type": "INTEGER", "description": "Índice de cámara. Normalmente 0."},
                "frames": {"type": "INTEGER", "description": "Cantidad de frames para elegir el más nítido. Por defecto 25."}
            },
            "required": []
        }
    },
    {
        "name": "auto_programmer",
        "description": "Suite de desarrollo y auto-programación autónoma avanzada. Permite a JARVIS escribir código Python para nuevas herramientas, validar sintaxis con py_compile, correr tests sintácticos en un sandbox con traceback detallado, corregir errores e inyectar plugins en caliente.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "create_tool (crear/actualizar) | fix_tool (corregir error) | test_tool (probar en sandbox) | list_tools (listar creadas)"},
                "tool_name": {"type": "STRING", "description": "Nombre de la herramienta en snake_case"},
                "description": {"type": "STRING", "description": "Descripción clara de la herramienta y su uso"},
                "parameters_schema": {"type": "STRING", "description": "JSON de propiedades de parámetros. Ej: '{\"param\": {\"type\": \"STRING\"}}'"},
                "python_code": {"type": "STRING", "description": "Código Python con la función def <tool_name>(parameters: dict, player=None) -> str:"},
                "test_parameters": {"type": "OBJECT", "description": "Parámetros mock de prueba para evaluar la ejecución de la función en el sandbox"}
            },
            "required": ["action", "tool_name"]
        }
    },
    {
        "name": "self_edit",
        "description": "Auto-edición de código: JARVIS puede leer, modificar, crear y gestionar sus propios archivos de código fuente. Crea backups automáticos antes de cada cambio.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "read_file | edit_file | append_file | create_file | list_files | list_backups | restore_backup"},
                "file": {"type": "STRING", "description": "Ruta del archivo relativa al proyecto (ej: 'main.py', 'actions/terminal_agent.py', 'core/prompt.txt')"},
                "target": {"type": "STRING", "description": "Para edit_file: el texto EXACTO a buscar (incluyendo espacios e indentación)"},
                "replacement": {"type": "STRING", "description": "Para edit_file: el texto que reemplazará al target"},
                "content": {"type": "STRING", "description": "Para append_file/create_file: el contenido a escribir"},
                "directory": {"type": "STRING", "description": "Para list_files: directorio a listar (default: raíz del proyecto)"},
                "backup_name": {"type": "STRING", "description": "Para restore_backup: nombre del archivo .bak a restaurar"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "sustainability_analyst",
        "description": "Calcula el punto de equilibrio financiero integrando costos ambientales y sociales para reportes de sostenibilidad.",
        "parameters": {"type": "OBJECT", "properties": {"precio_venta": {"type": "NUMBER"}, "costo_variable": {"type": "NUMBER"}, "costos_fijos": {"type": "NUMBER"}, "costos_ambientales": {"type": "NUMBER"}, "costos_sociales": {"type": "NUMBER"}}, "required": ["precio_venta", "costo_variable", "costos_fijos"]}
    },
    {
        "name": "cloud_monitor",
        "description": "Monitorea el estado del proyecto en Netlify y las métricas de telemetría de Google Cloud.",
        "parameters": {"type": "OBJECT", "properties": {"action": {"type": "STRING"}}}
    },
    {
        "name": "cinematic_voice",
        "description": "Usa el motor neuronal para leer textos muy largos de forma fluida y humana.",
        "parameters": {"type": "OBJECT", "properties": {"text": {"type": "STRING", "description": "El texto que debe ser leído en voz alta."}}, "required": ["text"]}
    },
    {
        "name": "offline_survival",
        "description": "Usa la IA local Llama3 cuando no hay conexión a internet.",
        "parameters": {"type": "OBJECT", "properties": {"prompt": {"type": "STRING"}}, "required": ["prompt"]}
    },
    {
        "name": "context_memory",
        "description": "Analiza la pantalla y guarda lo que el usuario está haciendo para recordárselo después.",
        "parameters": {"type": "OBJECT", "properties": {"action": {"type": "STRING", "description": "save | recall"}}, "required": ["action"]}
    },
    {
        "name": "create_pdf",
        "description": "Crea un documento PDF formateado, estructurado y profesional en el Escritorio del usuario con títulos, subtítulos, fecha y párrafos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING", "description": "Título principal del documento PDF"},
                "content": {"type": "STRING", "description": "Contenido, cuerpo o texto completo del documento"},
                "filename": {"type": "STRING", "description": "Nombre del archivo (opcional, ej: 'informe_financiero.pdf')"},
                "subtitle": {"type": "STRING", "description": "Subtítulo opcional"},
                "author": {"type": "STRING", "description": "Autor opcional"}
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "create_document",
        "description": "Crea documentos de Word (.docx), texto (.txt), Markdown (.md), presentaciones (.pptx) o páginas web (.html) guardándolos en el Escritorio.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING", "description": "Título o nombre del documento"},
                "content": {"type": "STRING", "description": "Contenido o cuerpo del documento"},
                "format": {"type": "STRING", "description": "Formato: 'docx' (Word), 'txt', 'md', 'pptx' (PowerPoint), 'html', 'json', 'csv'"},
                "subtitle": {"type": "STRING", "description": "Subtítulo opcional"}
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "excel_tools",
        "description": "Crea, formatea y organiza hojas de cálculo Excel (.xlsx) y archivos CSV en el Escritorio del usuario con tablas, encabezados y datos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "create (crear planilla) | read (leer planilla)"},
                "filename": {"type": "STRING", "description": "Nombre del archivo Excel (ej: 'gastos_mensuales.xlsx')"},
                "headers": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Lista de encabezados de columnas (ej: ['Fecha', 'Concepto', 'Monto'])"},
                "data": {"type": "ARRAY", "items": {"type": "ARRAY", "items": {"type": "STRING"}}, "description": "Filas de datos para la planilla"}
            },
            "required": ["filename"]
        }
    },
    {
        "name": "generate_qr",
        "description": "Genera códigos QR en alta resolución a partir de cualquier texto, URL, enlace o contacto y los guarda en el Escritorio como imagen PNG.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "text": {"type": "STRING", "description": "El enlace, texto o contenido que contendrá el código QR"},
                "filename": {"type": "STRING", "description": "Nombre de la imagen (opcional, ej: 'qr_mi_web.png')"}
            },
            "required": ["text"]
        }
    }
]