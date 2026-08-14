import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
API_FILE = BASE_DIR / "config" / "api_keys.json"

def _get_api_key() -> str:
    if not API_FILE.exists():
        return ""
    try:
        data = json.loads(API_FILE.read_text(encoding="utf-8"))
        return data.get("openrouter_api_key", "")
    except Exception:
        return ""

def openrouter_agent(parameters: dict = None, player=None, speak=None, query: str = None, model: str = "google/gemini-2.5-flash", **kwargs) -> str:
    """Delega una tarea de texto a OpenRouter asegurando compatibilidad de voz."""
    if isinstance(parameters, dict):
        query = parameters.get("query") or parameters.get("prompt") or parameters.get("text") or query
        model = parameters.get("model") or model

    if not query:
        return "Error: No se proporcionó ninguna consulta o texto para OpenRouter."

    api_key = _get_api_key()
    if not api_key:
        return "No se encontró una clave de OpenRouter en config/api_keys.json."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/jarvis-beta",
        "X-Title": "JARVIS AI Assistant",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "max_tokens": 1500,
        "messages": [
            {"role": "system","content": "Eres JARVIS. Responde en español natural, con frases cortas, sin markdown, sin asteriscos, sin listas largas y terminando cada oración. Usa solo texto plano."},
            {"role": "user", "content": query}
        ]
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            if "choices" in response_data and len(response_data["choices"]) > 0:
                texto_crudo = response_data["choices"][0]["message"]["content"]
                # Filtro final para asegurar que no pase ni un solo símbolo que trabe la voz
                texto_limpio = texto_crudo.replace("*", "").replace("#", "").replace("_", "")
                return texto_limpio
            else:
                return "Error: Respuesta inesperada de OpenRouter."
    except Exception as e:
        return f"Error al conectar con OpenRouter: {str(e)}"