def sustainability_analyst(parameters: dict, player=None) -> str:
    """Evalúa la sostenibilidad integral de un proyecto empresarial."""
    precio = float(parameters.get("precio_venta", 0))
    costo_var = float(parameters.get("costo_variable", 0))
    costos_fijos = float(parameters.get("costos_fijos", 0))
    costos_amb = float(parameters.get("costos_ambientales", 0))
    costos_soc = float(parameters.get("costos_sociales", 0))
    
    margen = precio - costo_var
    if margen <= 0: 
        return "Error: El margen de contribución es nulo o negativo. Revisar estructura de precios."
    
    punto_eq_trad = costos_fijos / margen
    punto_eq_integral = (costos_fijos + costos_amb + costos_soc) / margen
    
    reporte = (
        f"Análisis de Sostenibilidad Integral completado:\n"
        f"El punto de equilibrio tradicional es de {punto_eq_trad:.2f} unidades.\n"
        f"Sin embargo, calculando el punto de equilibrio con costos sociales y ambientales integrados, "
        f"el volumen necesario sube a {punto_eq_integral:.2f} unidades. "
        f"La empresa necesita generar una diferencia operativa de {punto_eq_integral - punto_eq_trad:.2f} "
        f"unidades extra para absorber verdaderamente su impacto ambiental y social."
    )
    
    if player:
        player.write_log("🌱 " + reporte)
    return reporte