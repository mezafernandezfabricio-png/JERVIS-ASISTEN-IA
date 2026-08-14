# -*- coding: utf-8 -*-
"""web_search.py — Búsqueda en la web en tiempo real con DuckDuckGo y fuentes públicas."""
import urllib.parse
import webbrowser

def web_search(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Busca información en la web en tiempo real y retorna resúmenes con enlaces.
    """
    parameters = parameters or {}
    query = parameters.get("query") or parameters.get("q") or parameters.get("search") or ""
    max_results = int(parameters.get("max_results", 4))

    if not query:
        return "Error: No se indicó qué buscar en la web."

    if player:
        player.write_log(f"🔍 Buscando en la web: '{query}'...")

    # 1. Intento con DuckDuckGo Search
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if results:
                formatted = [f"=== RESULTADOS DE BÚSQUEDA: '{query}' ==="]
                for idx, r in enumerate(results, 1):
                    title = r.get("title", "Sin título")
                    body = r.get("body", "")
                    href = r.get("href", "")
                    formatted.append(f"{idx}. {title}\n   {body}\n   Fuente: {href}")
                res = "\n\n".join(formatted)
                if player: player.write_log("🔍 Resultados de búsqueda web obtenidos.")
                return res
    except Exception as e:
        pass

    # 2. Fallback: Búsqueda rápida en Wikipedia API
    try:
        import urllib.request
        import json
        wiki_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
        req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0 (JARVIS-AI)'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            title = data.get("title", query)
            extract = data.get("extract", "")
            if extract:
                return f"=== INFORMACIÓN DE {title.upper()} ===\n{extract}"
    except Exception:
        pass

    # 3. Fallback final: Respuesta limpia en texto plano (sin abrir navegador)
    return f"No se obtuvieron resultados adicionales de la web para '{query}'."
