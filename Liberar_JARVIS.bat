@echo off
title Liberar Instancias de JARVIS
echo.
echo ============================================================
echo   LIBERAR INSTANCIAS DE JARVIS - RESET DE PROCESOS
echo ============================================================
echo.
echo Este script cerrara los procesos colgados de JARVIS para
echo liberar el mutex "JARVIS_AI_SINGLE_INSTANCE_MUTEX".
echo.
set /p confirm=Desea cerrar los procesos de JARVIS ahora? (S/N): 
if /i "%confirm%" neq "S" (
    echo Operacion cancelada.
    pause
    exit /b
)
echo.
taskkill /F /FI "WINDOWTITLE eq JARVIS*" >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
echo.
echo ============================================================
echo   PROCESOS DEPURADOS CON EXITO. Ya puedes iniciar JARVIS.
echo ============================================================
echo.
pause
