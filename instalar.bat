@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   Instalando Deck - Descargador de YouTube
echo ============================================
echo.

REM --- 1. Verificar Python ---
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo No se encontro Python. Instalando con winget...
    winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
    echo.
    echo IMPORTANTE: cierra esta ventana y vuelve a abrir una terminal nueva
    echo para que Windows reconozca el comando "python", luego vuelve a
    echo ejecutar instalar.bat
    pause
    exit /b
) else (
    echo Python encontrado: OK
)

REM --- 2. Verificar ffmpeg ---
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo No se encontro ffmpeg. Instalando con winget...
    winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
    echo.
    echo IMPORTANTE: cierra esta ventana y vuelve a abrir una terminal nueva
    echo para que Windows reconozca el comando "ffmpeg", luego vuelve a
    echo ejecutar instalar.bat para terminar la instalacion.
    pause
    exit /b
) else (
    echo ffmpeg encontrado: OK
)

REM --- 3. Entorno virtual de Python ---
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Instalando dependencias (Flask, yt-dlp)...
pip install -r requirements.txt --quiet

echo.
echo ============================================
echo   Instalacion terminada.
echo   Ahora usa "iniciar.bat" para abrir la app.
echo ============================================
pause
