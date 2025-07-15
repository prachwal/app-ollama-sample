#!/usr/bin/env python3
"""
Launcher dla Ollama Basic Chat GUI
===================================

Pomocnik do uruchamiania GUI z lepszą obsługą błędów.
"""

import sys
import os
import subprocess

def check_requirements():
    """Sprawdza wymagania systemowe"""
    print("🔍 Sprawdzanie wymagań...")
    
    # Sprawdź Python
    if sys.version_info < (3, 7):
        print("❌ Wymagany Python 3.7 lub nowszy")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Sprawdź tkinter
    try:
        import tkinter
        print("✅ Tkinter dostępny")
    except ImportError:
        print("❌ Tkinter niedostępny - zainstaluj python3-tk")
        return False
    
    # Sprawdź moduły src
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if not os.path.exists(src_path):
        print("❌ Brak folderu src/ - uruchom z głównego katalogu projektu")
        return False
    
    print("✅ Struktura modułów OK")
    
    return True

def main():
    """Główna funkcja launchera"""
    print("🚀 Ollama Basic Chat GUI Launcher")
    print("=" * 40)
    
    if not check_requirements():
        print("\n❌ Nie można uruchomić aplikacji - brak wymagań")
        input("Naciśnij Enter aby zakończyć...")
        return
    
    print("\n🎯 Uruchamianie GUI...")
    
    try:
        # Uruchom GUI
        import ollama_basic_chat_gui
        ollama_basic_chat_gui.main()
        
    except ImportError as e:
        print(f"❌ Błąd importu: {e}")
        print("Sprawdź czy plik ollama_basic_chat_gui.py istnieje")
        
    except KeyboardInterrupt:
        print("\n👋 Zamknięto przez użytkownika")
        
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}")
        print("Sprawdź logi powyżej")
    
    finally:
        input("\nNaciśnij Enter aby zakończyć...")

if __name__ == "__main__":
    main()
