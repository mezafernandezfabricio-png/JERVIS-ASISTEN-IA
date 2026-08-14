# -*- coding: utf-8 -*-
"""scheduler.py — Programador de tareas y recordatorios temporizados."""
import time
import threading

def scheduler(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Programa recordatorios o tareas temporizadas en el sistema:
    - task / reminder: descripción de la tarea.
    - time / delay: tiempo en minutos o fecha programada.
    """
    parameters = parameters or {}
    task = parameters.get("task") or parameters.get("reminder") or parameters.get("goal") or "Recordatorio general"
    delay_minutes = float(parameters.get("delay", parameters.get("minutes", 10)))

    def _scheduled_alarm():
        time.sleep(delay_minutes * 60)
        if speak:
            try: speak(f"Atención, recordatorio programado: {task}")
            except Exception: pass
        if player:
            try: player.write_log(f"⏰ Recordatorio: {task}")
            except Exception: pass

    threading.Thread(target=_scheduled_alarm, daemon=True).start()
    msg = f"Tarea '{task}' programada exitosamente para ejecutarse en {delay_minutes} minutos."
    if player:
        player.write_log(f"⏰ {msg}")
    return msg

def start_runner(player=None, speak=None) -> None:
    """Inicializador del servicio en segundo plano de tareas programadas."""
    pass
