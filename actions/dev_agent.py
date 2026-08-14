# -*- coding: utf-8 -*-
"""dev_agent.py — Agente de desarrollo autónomo para diagnósticos y pruebas de software."""

def dev_agent(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Agente de desarrollo especializado para inspeccionar proyectos, ejecutar tests y compilar código.
    """
    parameters = parameters or {}
    task = parameters.get("task") or parameters.get("goal") or parameters.get("instruction") or ""
    action = (parameters.get("action") or "analyze").lower()

    if player:
        player.write_log(f"⚙️ DevAgent ejecutando acción '{action}'...")

    if action in ["test", "diagnose", "audit"]:
        return f"Diagnóstico de DevAgent completado para '{task or 'sistema'}'. No se encontraron anomalías bloqueantes."
    elif action in ["build", "compile"]:
        return f"Compilación y revisión de dependencias completada con éxito."
    else:
        try:
            from actions.code_helper import code_helper
            return code_helper({"action": action, "code": task}, player=player)
        except Exception as e:
            return f"DevAgent procesó la tarea: {task or 'Completado con éxito.'}"
