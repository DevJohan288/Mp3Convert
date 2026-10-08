@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo ============================================
echo   Iniciando servidor...
echo   No cierres esta ventana mientras usas la app.
echo ============================================
python run.py
pause
