#!/usr/bin/env python3
"""
Ollama LLM Comprehensive Benchmark Suite
========================================

Ujednolicony tester modeli LLM z oceną AI sędziego.
Wykorzystuje refaktoryzowaną architekturę modułową.

Autor: Ollama Testing Team
Wersja: 2.0.0
"""

import sys
import os

# Dodaj src do PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.testers import BaseTester
from src.utils import (
    get_comprehensive_test_prompts, 
    get_quick_test_prompts,
    generate_output_filename
)


class ComprehensiveBenchmarkTester(BaseTester):
    """
    Kompleksowy tester LLM z oceną AI sędziego.
    """
    
    def run_comprehensive_test(self):
        """Uruchamia kompleksowy test wszystkich modeli."""
        test_prompts = get_comprehensive_test_prompts()
        output_file = generate_output_filename("comprehensive")
        
        return self.run_test_suite(
            test_prompts, 
            "Kompleksowy", 
            output_file
        )
    
    def run_quick_test(self):
        """Uruchamia szybki test wszystkich modeli."""
        test_prompts = get_quick_test_prompts()
        output_file = generate_output_filename("quick")
        
        return self.run_test_suite(
            test_prompts, 
            "Szybki", 
            output_file
        )
    
    def run_custom_test(self, prompt: str):
        """Uruchamia test z własnym pytaniem."""
        output_file = generate_output_filename("custom")
        
        return self.ask_all_models(prompt, output_file)


def main():
    """Główna funkcja aplikacji."""
    print("=== TESTER MODELI LLM v2.0 ===")
    print("Nowa, ujednolicona architektura modułowa")
    print("=" * 50)
    print("1. Kompleksowy test wszystkich modeli (13 różnych zadań, z oceną AI sędziego Gemini)")
    print("2. Szybki test (6 podstawowych zadań, z oceną AI sędziego Gemini)")
    print("3. Własne pytanie do wszystkich modeli (bez oceny AI sędziego)")
    
    choice = input("\nWybierz opcję (1, 2 lub 3): ").strip()
    
    if choice == "1":
        tester = ComprehensiveBenchmarkTester(use_judge=True)
        tester.run_comprehensive_test()
    elif choice == "2":
        tester = ComprehensiveBenchmarkTester(use_judge=True)
        tester.run_quick_test()
    elif choice == "3":
        prompt = input("Wpisz swoje pytanie: ").strip()
        if prompt:
            tester = ComprehensiveBenchmarkTester(use_judge=False)
            tester.run_custom_test(prompt)
        else:
            print("Nie podano pytania!")
    else:
        print("Nieprawidłowy wybór! Uruchamiam szybki test...")
        tester = ComprehensiveBenchmarkTester(use_judge=True)
        tester.run_quick_test()


if __name__ == "__main__":
    main()
