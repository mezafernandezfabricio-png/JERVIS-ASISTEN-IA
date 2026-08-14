# -*- coding: utf-8 -*-
import json
import sys
import py_compile
import subprocess
import traceback
import re
from pathlib import Path

def run_in_sandbox(tool_name: str, test_params: dict) -> tuple[bool, str]:
    """Ejecuta de manera segura la herramienta recién creada en un subproceso sandbox con timeout."""
    python_exe = sys.executable or ".venv/Scripts/python.exe"
    params_json = json.dumps(test_params)
    
    # Ruta de JARVIS segura para Windows
    jarvis_dir = str(Path(__file__).resolve().parent.parent).replace('\\', '\\\\')
    
    # Código que se ejecutará en el sandbox con ESCUDO ANTI-ENVENENAMIENTO
    code = f"""
import sys
import json

# Borramos el directorio actual de la prioridad para que no lea archivos corruptos locales
while '' in sys.path: sys.path.remove('')
while '.' in sys.path: sys.path.remove('.')

sys.path.append('{jarvis_dir}')

try:
    from actions.{tool_name} import {tool_name}
    params = json.loads('''{params_json}''')
    res = {tool_name}(params, player=None)
    print("SUCCESS_OUTPUT:" + str(res))
except Exception as e:
    import traceback
    print("ERROR_TRACEBACK:", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)
"""
    try:
        # Ejecución segura con ESCUDO ANTI-TILDES (errors="replace")
        res = subprocess.run(
            [python_exe, "-c", code],
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace", 
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if res.returncode == 0:
            output = res.stdout.strip()
            if "SUCCESS_OUTPUT:" in output:
                return True, output.split("SUCCESS_OUTPUT:", 1)[1]
            return True, output
        else:
            err_output = res.stderr.strip() or res.stdout.strip()
            return False, err_output
    except subprocess.TimeoutExpired:
        return False, "Error: Timeout de ejecución en sandbox (límite de 60 segundos excedido)."
    except Exception as e:
        return False, f"Fallo al ejecutar en el sandbox: {e}"

def auto_programmer(parameters: dict, player=None) -> str:
    """
    Desarrollo y Auto-Programación autónoma con AUTO-SANACIÓN.
    """
    action = parameters.get("action", "create_tool").lower()
    tool_name = parameters.get("tool_name", "")
    description = parameters.get("description", "")
    parameters_schema_str = parameters.get("parameters_schema", "{}")
    python_code = parameters.get("python_code", "")
    test_params = parameters.get("test_parameters", {})

    if not tool_name:
        return "Error: Se requiere especificar 'tool_name'."

    actions_dir = Path(__file__).resolve().parent
    tool_file = actions_dir / f"{tool_name}.py"

    if action == "create_tool" or action == "fix_tool":
        if not python_code:
            return "Error: Se requiere proporcionar el código Python."

        try:
            tool_file.write_text(python_code, encoding="utf-8")
        except Exception as e:
            return f"Error guardando el código fuente: {e}"

        # 1. Chequeo Sintáctico
        try:
            py_compile.compile(str(tool_file), doraise=True)
        except py_compile.PyCompileError as compile_err:
            return f"Sintaxis Inválida en '{tool_name}.py'.\n\n{compile_err.msg}"

        # 2. Validación de Ejecución (Sandbox Run) con AUTO-SANACIÓN
        success, sandbox_res = run_in_sandbox(tool_name, test_params)
        
        max_retries = 2
        attempts = 0
        instalaciones_exitosas = []

        while not success and attempts < max_retries:
            match = re.search(r"No module named '([^']+)'", sandbox_res)
            
            if match:
                missing_module = match.group(1)
                
                # ESCUDO DE NÚCLEO: Evitar que intente instalar librerías vitales de Python
                modulos_core = ["sys", "os", "math", "time", "json", "re", "subprocess", "threading", "socket"]
                if missing_module.startswith("_") or missing_module in modulos_core:
                    sandbox_res += f"\n\n[SISTEMA] Error: El módulo '{missing_module}' es interno. Revisa si hay archivos locales causando conflicto."
                    break
                
                # Traductor inteligente de librerías
                paquetes_conocidos = {
                    "cv2": "opencv-python",
                    "bs4": "beautifulsoup4",
                    "PIL": "Pillow",
                    "speedtest": "speedtest-cli",
                    "fitz": "PyMuPDF",
                    "docx": "python-docx"
                }
                paquete_a_instalar = paquetes_conocidos.get(missing_module, missing_module)
                
                print(f"[JARVIS] Sandbox detectó ausencia de '{missing_module}'. Instalando '{paquete_a_instalar}' en segundo plano...")
                
                try:
                    # INSTALACIÓN SILENCIOSA CON ESCUDO ANTI-TILDES
                    pip_proc = subprocess.run(
                        [sys.executable, "-m", "pip", "install", paquete_a_instalar],
                        capture_output=True, 
                        text=True, 
                        encoding="utf-8",
                        errors="replace",
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if pip_proc.returncode == 0:
                        instalaciones_exitosas.append(paquete_a_instalar)
                        print(f"[JARVIS] '{paquete_a_instalar}' instalado. Reintentando sandbox...")
                        success, sandbox_res = run_in_sandbox(tool_name, test_params)
                        attempts += 1
                        continue
                    else:
                        sandbox_res += f"\n\n[SISTEMA] Fallo en PIP al instalar '{paquete_a_instalar}':\n{pip_proc.stderr[-200:]}"
                        break
                except Exception as e:
                    sandbox_res += f"\n\n[SISTEMA] Fallo crítico en PIP: {e}"
                    break
            else:
                break 

        if not success:
            return (
                f"Fallo de Ejecución en Sandbox para la herramienta '{tool_name}'. "
                f"Rastreo del error (traceback):\n\n{sandbox_res}"
            )

        # 3. Construcción del JSON Schema
        try:
            import ast
            properties = ast.literal_eval(parameters_schema_str)
            if not isinstance(properties, dict):
                properties = {}
        except Exception:
            try:
                properties = json.loads(parameters_schema_str)
            except Exception:
                properties = {}

        new_tool_def = {
            "name": tool_name,
            "description": description or f"Herramienta autónoma {tool_name}",
            "parameters": {
                "type": "OBJECT",
                "properties": properties,
                "required": list(properties.keys())
            }
        }

        # 4. Guardar definición (Persistencia)
        custom_tools_path = actions_dir / "custom_tools.json"
        custom_tools = []
        if custom_tools_path.exists():
            try:
                custom_tools = json.loads(custom_tools_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        custom_tools = [t for t in custom_tools if t["name"] != tool_name]
        custom_tools.append(new_tool_def)
        custom_tools_path.write_text(json.dumps(custom_tools, indent=4, ensure_ascii=False), encoding="utf-8")

        # 5. Inyección dinámica en memoria
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, 'TOOL_DECLARATIONS'):
            main_module.TOOL_DECLARATIONS = [t for t in main_module.TOOL_DECLARATIONS if t.get("name") != tool_name]
            main_module.TOOL_DECLARATIONS.append(new_tool_def)

        # 6. Forzar la reconexión
        reload_msg = ""
        if player and hasattr(player, "on_config_saved"):
            from threading import Timer
            def delayed_reload():
                try:
                    player.on_config_saved({})
                except Exception:
                    pass
            Timer(8.0, delayed_reload).start()
            reload_msg = " Reiniciando módulos cognitivos para incorporarla de inmediato..."

        mensaje_instalaciones = ""
        if instalaciones_exitosas:
            mensaje_instalaciones = f"\n- Dependencias Auto-Instaladas: {', '.join(instalaciones_exitosas)}"

        return (
            f"¡Herramienta '{tool_name}' desarrollada e integrada con éxito!\n"
            f"- Prueba en Sandbox: Exitosa.{mensaje_instalaciones}\n"
            f"- Persistencia e Inyección: Completadas.{reload_msg}"
        )

    elif action == "test_tool":
        if not tool_file.exists():
            return f"Error: La herramienta '{tool_name}' no existe."
        
        success, sandbox_res = run_in_sandbox(tool_name, test_params)
        if success:
            return f"Prueba manual exitosa. Retornó: {sandbox_res}"
        else:
            return f"Fallo en sandbox manual:\n\n{sandbox_res}"

    elif action == "list_tools":
        custom_tools_path = actions_dir / "custom_tools.json"
        if not custom_tools_path.exists():
            return "No se ha desarrollado ninguna herramienta."
        try:
            custom_tools = json.loads(custom_tools_path.read_text(encoding="utf-8"))
            res = "Herramientas Desarrolladas de Forma Autónoma:\n"
            for idx, t in enumerate(custom_tools, 1):
                res += f"{idx}. {t.get('name')} - {t.get('description')}\n"
            return res
        except Exception as e:
            return f"Error leyendo lista: {e}"

    else:
        return f"Acción '{action}' no soportada."