# -*- coding: utf-8 -*-
"""agent_task.py — Encola tareas complejas o asíncronas para el sub-agente de segundo plano."""
from agent.task_queue import get_queue, TaskPriority

def agent_task(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Encola una tarea de investigación o trabajo pesado para ser ejecutada en segundo plano por el agente.
    """
    parameters = parameters or {}
    goal = parameters.get("goal") or parameters.get("task") or parameters.get("prompt") or ""
    priority_str = str(parameters.get("priority", "normal")).lower()

    if not goal:
        return "Error: Debe especificar la meta ('goal') o instrucción para el agente."

    priority = TaskPriority.NORMAL
    if "high" in priority_str or "alta" in priority_str:
        priority = TaskPriority.HIGH
    elif "low" in priority_str or "baja" in priority_str:
        priority = TaskPriority.LOW

    if player:
        player.write_log(f"📋 Encolando tarea en segundo plano: '{goal[:60]}...'")

    task_id = get_queue().submit(goal=goal, priority=priority, speak=speak)
    return f"Tarea encolada con éxito (ID: {task_id}). El agente generará un reporte detallado en el escritorio al terminar."
