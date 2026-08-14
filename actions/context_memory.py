import time
from pathlib import Path
from actions.screen_vision import screen_vision

def context_memory(parameters: dict, player=None) -> str:
    """Guarda en disco duro lo que estás haciendo en este momento."""
    action = parameters.get("action", "save")
    log_path = Path("memory/context.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    if action == "save":
        if player:
            player.write_log("🧠 Guardando el contexto de la pantalla...")
            
        # Pide a la herramienta visual que resuma la pantalla
        resumen = screen_vision({"action": "analyze", "query": "Resume en una oración en qué estoy trabajando ahora mismo."}, player)
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M')}] {resumen}\n")
        return "He tomado nota del contexto actual en pantalla. Puedes preguntarme en qué te quedaste cuando regreses."
        
    elif action == "recall":
        if not log_path.exists():
            return "No hay ningún contexto guardado en tu memoria local."
            
        with open(log_path, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            if not lineas:
                return "Tu registro de contexto está vacío."
            return "Según mi último registro, tu contexto era: " + lineas[-1]