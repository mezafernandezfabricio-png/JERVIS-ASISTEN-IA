# core/security_manager.py
# -*- coding: utf-8 -*-
import ctypes

def confirmar_comando_peligroso(comando: str) -> bool:
    """
    Evalúa si un comando de terminal es destructivo o altera el sistema.
    Lanza una alerta nativa de Windows (Thread-Safe) por encima de todas las ventanas.
    """
    # Lista de comandos que no queremos que la IA ejecute sin nuestro permiso
    palabras_peligrosas = ["rm ", "del ", "format ", "winget", "pip install", "reg ", "taskkill", "rd ", "rmdir"]
    comando_lower = comando.lower()
    
    # Verificar si contiene palabras peligrosas
    if not any(palabra in comando_lower for palabra in palabras_peligrosas):
        return True # Seguro, se ejecuta en silencio sin molestar

    # Llamada a la API nativa de Windows (Completamente a prueba de hilos)
    # MB_YESNO (4) | MB_ICONWARNING (0x30) | MB_SYSTEMMODAL (0x1000 - Siempre visible al frente)
    MB_YESNO = 0x04
    MB_ICONWARNING = 0x30
    MB_SYSTEMMODAL = 0x1000
    IDYES = 6

    texto = f"JARVIS intenta ejecutar un comando en PowerShell potencialmente peligroso.\n\nComando:\n{comando}\n\n¿Desea permitir la ejecución?"
    titulo = "JARVIS - Protocolo de Seguridad (Warden)"

    respuesta = ctypes.windll.user32.MessageBoxW(0, texto, titulo, MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    return respuesta == IDYES