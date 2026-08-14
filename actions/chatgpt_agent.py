import json
import os
from pathlib import Path

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

def chatgpt_agent(parameters: dict, player=None, speak=None) -> str:
    if not HAS_OPENAI:
        return "Error: La librería 'openai' no está instalada. Dile al usuario que ejecute 'pip install openai' en la terminal."

    query = parameters.get("query", "")
    model = parameters.get("model", "gpt-4o") # Modelos soportados: gpt-4o, gpt-4o-mini, o1-preview

    # 1. Buscar la llave de la API de OpenAI
    base_dir = Path(__file__).resolve().parent.parent
    cfg_path = base_dir / "config" / "api_keys.json"
    
    api_key = ""
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            api_key = cfg.get("openai_api_key", "").strip()
        except Exception:
            pass
            
    if not api_key:
        return "Error: No encontré la clave 'openai_api_key' en config/api_keys.json. Dile al usuario que la agregue."

    # 2. Avisar por voz que JARVIS está llamando a ChatGPT
    if speak:
        speak("Abriendo un canal directo con los servidores de OpenAI. Consultando a ChatGPT, dame un momento...")

    # 3. Hacer la consulta a ChatGPT
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Eres ChatGPT, el modelo de IA de OpenAI. "
                        "Estás siendo consultado por JARVIS, una IA de escritorio impulsada por Gemini. "
                        "Tu objetivo es proveer la mejor respuesta, análisis o código posible al usuario humano. "
                        "Sé directo, muy profesional y exacto."
                    )
                },
                {"role": "user", "content": query}
            ]
        )
        
        respuesta_gpt = response.choices[0].message.content
        
        # 4. Guardar un archivo Markdown en el escritorio (Ideal para códigos o textos largos)
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        log_path = os.path.join(desktop, "Respuesta_ChatGPT.md")
        
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"# Respuesta de {model.upper()} (OpenAI)\n\n{respuesta_gpt}")
            
        # Devolvemos un resumen a Gemini para que te lo diga por voz
        return (
            f"ChatGPT respondió exitosamente. La respuesta completa se guardó en {log_path} "
            f"en el escritorio. Resúmele esto al usuario brevemente:\n\n{respuesta_gpt[:800]}..."
        )
        
    except Exception as e:
        return f"Ocurrió un error al intentar hablar con ChatGPT: {str(e)}"