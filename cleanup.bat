@echo off
echo.
echo ========================================
echo    CZYSZCZENIE PROJEKTU OLLAMA CHAT
echo ========================================
echo.

REM Sprawdź czy jesteśmy w odpowiednim katalogu
if not exist "ollama_basic_chat_gui.py" (
    echo BLAD: Nie znaleziono pliku ollama_basic_chat_gui.py
    echo Upewnij sie, ze uruchamiasz skrypt z katalogu projektu
    pause
    exit /b 1
)

echo Usuwanie plikow cache Python...
del /s /q *.pyc 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

echo Usuwanie plikow testow...
del /q *test*.txt 2>nul
del /q *test*.json 2>nul  
del /q *test*.csv 2>nul
del /q chat_*.txt 2>nul

echo Usuwanie plikow tymczasowych...
del /q *.tmp 2>nul
del /q *.temp 2>nul
del /q *.log 2>nul
del /q .DS_Store 2>nul
del /q Thumbs.db 2>nul

echo Usuwanie plikow backupow...
del /q *.bak 2>nul
del /q *.backup 2>nul
del /q *.old 2>nul

echo.
echo ========================================
echo         CZYSZCZENIE ZAKONCZONE!
echo ========================================
echo.

REM Pokaż pozostałe pliki
echo Pozostale pliki w projekcie:
dir /b *.py *.md *.bat *.ps1 2>nul

echo.
pause
