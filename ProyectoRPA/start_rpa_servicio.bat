@echo off
title Instalador del Servicio RPA Reclutamiento - Umbral S.A.
color 0A

echo =======================================================
echo   INSTALADOR DEL SERVICIO RPA RECLUTAMIENTO (v2)
echo =======================================================
echo.

:: Detener servicio si está corriendo
echo Deteniendo servicio existente...
sc stop RPA_Reclutamiento_Service_v2 >nul 2>&1

:: Esperar un poco
timeout /t 2 >nul

:: Eliminar servicio anterior si existe
echo Eliminando servicio anterior (si existe)...
sc delete RPA_Reclutamiento_Service_v2 >nul 2>&1

timeout /t 2 >nul

:: Crear nuevo servicio apuntando al script Python
echo Creando nuevo servicio...
sc create RPA_Reclutamiento_Service_v2 ^
   binPath= "\"C:\Users\harman\AppData\Local\Programs\Python\Python313\python.exe\" \"C:\RPA_PYTHOM\ProyectoRPA\servicio_rpa_reclutamiento.py\"" ^
   start= auto ^
   DisplayName= "RPA Reclutamiento CVs v2 - Umbral S.A." >nul

if %errorlevel% neq 0 (
    echo ❌ Error al crear el servicio. Verifica permisos de administrador.
    pause
    exit /b
)

echo Servicio creado correctamente.

:: Iniciar servicio
echo Iniciando servicio...
net start RPA_Reclutamiento_Service_v2

if %errorlevel% neq 0 (
    echo ❌ El servicio no pudo iniciarse. Revisa el log en:
    echo C:\RPA_PYTHOM\ProyectoRPA\log_error_servicio.txt
) else (
    echo ✅ El servicio se inició correctamente.
)

echo.
echo -------------------------------------------------------
echo  Si deseas detener el servicio manualmente:
echo     net stop RPA_Reclutamiento_Service_v2
echo -------------------------------------------------------
echo.

pause
exit
