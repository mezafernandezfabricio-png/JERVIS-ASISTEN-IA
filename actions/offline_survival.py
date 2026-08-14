import urllib.request
import json

def offline_survival(parameters: dict, player=None) -> str:
    """Usa el motor local de Ollama cuando no hay internet."""
    prompt = parameters.get("prompt", "")
    
    if player:
        player.write_log("🛡️ Protocolo de supervivencia local activo...")
        
    url = "http://localhost:11434/api/generate"
    payload = {"model": "llama3", "prompt": prompt, "stream": False}
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={'Content-Type': 'application/json'}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as response:
            respuesta = json.loads(response.read().decode("utf-8"))["response"]
            return respuesta
    except Exception:
        return "Servidores caídos y el motor local no está encendido. Por favor, abre la aplicación Ollama en tu PC para activar mi cerebro offline."