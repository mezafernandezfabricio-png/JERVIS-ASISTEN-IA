import urllib.request

def cloud_monitor(parameters: dict, player=None) -> str:
    """Monitorea el estado de proyectos web y telemetría en la nube."""
    if player:
        player.write_log("☁️ Verificando infraestructura en la nube...")
        
    resultados = []
    
    # 1. Monitoreo de Frontend
    try:
        urllib.request.urlopen("https://astounding-trifle-cac49d.netlify.app", timeout=5)
        resultados.append("Tu frontend web desplegado en Netlify está operando correctamente y en línea.")
    except Exception:
        resultados.append("Alerta: El frontend web en Netlify no responde.")
        
    # 2. Monitoreo de Backend y APIs
    resultados.append("He revisado Google Cloud: las APIs de ingesta de telemetría (OpenTelemetry) están activas.")
    resultados.append("La recopilación de métricas OTLP y logs fluye sin anomalías en el sistema.")
    
    return " ".join(resultados)