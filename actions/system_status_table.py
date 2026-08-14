# -*- coding: utf-8 -*-
"""
system_status_table.py — Tabla y métricas completas del estado del sistema para JARVIS.
"""
import psutil
import platform

def system_status_table(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    so = platform.system()
    release = platform.release()
    cpu_usage = psutil.cpu_percent(interval=0.2)
    ram = psutil.virtual_memory()
    ram_total = f"{ram.total / (1024**3):.1f} GB"
    ram_used = f"{ram.used / (1024**3):.1f} GB"
    ram_usage = f"{ram.percent}%"
    
    try:
        disk = psutil.disk_usage('C:\\')
        disk_total = f"{disk.total / (1024**3):.1f} GB"
        disk_used = f"{disk.used / (1024**3):.1f} GB"
        disk_usage = f"{disk.percent}%"
    except Exception:
        disk_total = "N/A"
        disk_used = "N/A"
        disk_usage = "N/A"

    report = (
        f"=== ESTADO DEL SISTEMA JARVIS ===\n"
        f"• Sistema Operativo: {so} {release}\n"
        f"• Uso de CPU: {cpu_usage}%\n"
        f"• Memoria RAM: {ram_used} / {ram_total} ({ram_usage})\n"
        f"• Almacenamiento (C:): {disk_used} / {disk_total} ({disk_usage})"
    )

    if player:
        try: player.write_log(f"💻 CPU: {cpu_usage}% | RAM: {ram_usage} | Disco: {disk_usage}")
        except: pass

    return report