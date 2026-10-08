@echo off
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo No se encontro el entorno virtual de Python.
    echo Ejecuta instalar.bat para instalar la aplicacion.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" -c "import flask, yt_dlp" >nul 2>nul
if errorlevel 1 (
    echo Faltan dependencias en el entorno virtual.
    echo Ejecuta instalar.bat para instalarlas y vuelve a iniciar la app.
    pause
    exit /b 1
)

echo ============================================
echo   Iniciando servidor...
echo   No cierres esta ventana mientras usas la app.
echo ============================================
"venv\Scripts\python.exe" run.py
if errorlevel 1 (
    echo.
    echo El servidor termino con un error. Revisa el mensaje anterior.
)
pause
