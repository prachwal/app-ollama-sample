#!/usr/bin/env python3
"""
Ollama Basic Chat GUI - Modular Version
=======================================

Interfejs graficzny do komunikacji z modelami Ollama
z funkcjonalnością czatu i testowania.

Wersja: 2.2 (Modular)
"""

import sys
import os

# Dodaj ścieżkę do sys.path dla importów
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import głównej funkcji z modularnego GUI
from gui import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Aplikacja została przerwana przez użytkownika")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")
        sys.exit(1)
