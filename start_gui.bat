@echo off
echo ===========================================
echo    Ollama Basic Chat GUI - Uruchomienie
echo ===========================================
echo.

cd /d "%~dp0"

echo Sprawdzanie Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo BLAD: Python nie jest zainstalowany lub niedostepny w PATH
    echo Zainstaluj Python z https://python.org
    pause
    exit /b 1
)

echo Uruchamianie GUI...
python launch_gui.py

pause
