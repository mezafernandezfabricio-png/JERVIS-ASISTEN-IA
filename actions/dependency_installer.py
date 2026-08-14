import subprocess
import sys
import importlib

def dependency_installer(parameters: dict, player=None, speak=None) -> str:
    """
    Instala dependencias de Python faltantes usando pip en caliente, 
    sin necesidad de reiniciar el sistema.
    """
    packages = parameters.get("packages", [])

    if not packages:
        return "[ERROR] No especificaste qué librerías instalar."
    
    resultados = []
    instalacion_exitosa = False

    for pkg in packages:
        print(f"[DEBUG] JARVIS instalando dependencia en caliente: {pkg}")
        try:
            # Usamos sys.executable para garantizar que instale en el entorno virtual correcto (.venv)
            comando = [sys.executable, "-m", "pip", "install", pkg]
            proc = subprocess.run(
                comando, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if proc.returncode == 0 or "Requirement already satisfied" in proc.stdout:
                resultados.append(f"✅ Librería '{pkg}' instalada en caliente correctamente.")
                instalacion_exitosa = True
            else:
                resultados.append(f"❌ Fallo al instalar '{pkg}'. Error: {proc.stderr[-100:]}")
        except Exception as e:
            resultados.append(f"❌ Fallo crítico de sistema con '{pkg}': {e}")
    
    reporte = "\n".join(resultados)
    
    # EL TRUCO DE MAGIA: Le decimos a Python que refresque su memoria interna
    if instalacion_exitosa:
        importlib.invalidate_caches()
    
    # Le damos a Gemini la instrucción de reanudar su trabajo
    return (
        f"REPORTE DE INSTALACIÓN:\n{reporte}\n\n"
        "INSTRUCCIÓN OBLIGATORIA: Dile al usuario que la dependencia se instaló con éxito al instante. "
        "NO TE REINICIES. Si estabas intentando usar una herramienta, desarrollar un script o hacer algo "
        "que falló por falta de esta librería, VUELVE A EJECUTAR ESA ACCIÓN AHORA MISMO de forma automática."
    )