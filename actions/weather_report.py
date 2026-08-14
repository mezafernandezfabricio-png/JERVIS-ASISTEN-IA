"""weather_report.py — Reporte de clima actual y pronóstico detallado."""
import urllib.request
import urllib.parse
import json

def weather_report(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """Obtiene el clima actual y pronóstico para cualquier ciudad/país."""
    parameters = parameters or {}
    city = parameters.get("city", "Lima").strip()
    if not city:
        city = "Lima"
        
    try:
        encoded_city = urllib.parse.quote(city)
        # Pedimos el formato j1 (JSON completo) y lang=es (Español)
        url = f"https://wttr.in/{encoded_city}?format=j1&lang=es"
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0"}
        )
        
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        # 1. Extraer clima actual
        current = data['current_condition'][0]
        # La descripción en español viene en 'lang_es', si falla usa el default
        desc_list = current.get('lang_es', current.get('weatherDesc', [{'value': 'Desconocido'}]))
        desc = desc_list[0]['value']
        
        temp = current['temp_C']
        feels = current['FeelsLikeC']
        humidity = current['humidity']
        wind = current['windspeedKmph']
        
        report_lines = [
            f"=== REPORTE CLIMÁTICO: {city.upper()} ===",
            f"CONDICIÓN ACTUAL: {desc}",
            f"Temperatura: {temp}°C (Sensación térmica: {feels}°C)",
            f"Humedad: {humidity}% | Viento: {wind} km/h",
            "",
            "PRONÓSTICO PARA LOS PRÓXIMOS DÍAS:"
        ]
        
        # 2. Extraer pronóstico futuro (hoy, mañana y pasado mañana)
        for day in data.get('weather', []):
            date = day['date']
            maxt = day['maxtempC']
            mint = day['mintempC']
            
            # Buscar probabilidad de lluvia
            hourly = day.get('hourly', [{}])[0]
            rain_chance = hourly.get('chanceofrain', '0')
            
            report_lines.append(f"- Fecha {date}: Máx {maxt}°C | Mín {mint}°C | Prob. lluvia: {rain_chance}%")
            
        report = "\n".join(report_lines)
        
        if player:
            player.write_log(f"🌤️ Clima exacto obtenido para {city}.")
            
        return report
        
    except Exception as e:
        msg = f"No pude conectar a los satélites meteorológicos para obtener el clima de {city}."
        if player:
            player.write_log(f"⚠️ Error obteniendo clima: {e}")
        return msg

weather_action = weather_report