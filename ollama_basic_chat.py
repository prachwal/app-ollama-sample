#!/usr/bin/env python3
"""
Ollama Basic Chat - Prosty interfejs do rozmowy z modelami LLM
============================================================

Zmigrowany do nowej, modułowej architektury.
Używa wspólnych komponentów z src/ dla spójności kodu.

Autor: Ollama Testing Team
Wersja: 2.0.0
"""

import sys
import os
import time
from datetime import datetime

# Dodaj src do PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import get_available_models, ask_ollama
from src.utils import (
    get_comprehensive_test_prompts, 
    get_quick_test_prompts,
    get_timestamp,
    print_progress_bar,
    format_test_header,
    generate_summary
)
from src.config import DEFAULT_SLEEP_BETWEEN_MODELS


def ask_all_models(prompt):
    """Zadaje to samo pytanie wszystkim dostępnym modelom (funkcja kompatybilna wstecz)"""
    models = get_available_models()
    
    if not models:
        print("Nie znaleziono dostępnych modeli.")
        return
    
    print(f"Znaleziono {len(models)} modeli: {', '.join(models)}")
    
    timestamp = get_timestamp()
    output_file = f"single_test_{timestamp}.txt"
    
    for model in models:
        ask_ollama(model, prompt, "Pojedyncze pytanie", output_file)
        time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)


def run_comprehensive_test():
    """Uruchamia kompletny test wszystkich modeli ze wszystkimi zadaniami"""
    models = get_available_models()
    
    if not models:
        print("Nie znaleziono dostępnych modeli.")
        return
    
    # Utwórz plik wyników z timestampem
    timestamp = get_timestamp()
    output_file = f"test_results_{timestamp}.txt"
    
    # Nagłówek pliku
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Test modeli LLM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Testowane modele: {', '.join(models)}\n")
        f.write("="*100 + "\n\n")
    
    test_prompts = get_comprehensive_test_prompts()
    print(f"Rozpoczynam test {len(models)} modeli z {len(test_prompts)} zadaniami...")
    print(f"Wyniki będą zapisywane do: {output_file}")
    
    results = []
    total_tests = len(test_prompts) * len(models)
    current_test = 0
    
    for i, test in enumerate(test_prompts, 1):
        print(format_test_header(test['name'], i, len(test_prompts)))
        
        for j, model in enumerate(models, 1):
            current_test += 1
            print_progress_bar(
                current_test, 
                total_tests, 
                prefix=f'Model {j}/{len(models)} ({model}):', 
                suffix=f'({current_test}/{total_tests})'
            )
            
            result = ask_ollama(model, test['prompt'], test['name'], output_file, **test.get('options', {}))
            if result:
                results.append(result)
            
            time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
    
    # Podsumowanie wyników
    summary = generate_summary(results, output_file)
    print(summary)
    print(f"\nTest zakończony! Wyniki zapisane w: {output_file}")


def run_quick_test():
    """Uruchamia szybki test wszystkich modeli z podstawowymi zadaniami"""
    models = get_available_models()
    
    if not models:
        print("Nie znaleziono dostępnych modeli.")
        return
    
    # Utwórz plik wyników z timestampem
    timestamp = get_timestamp()
    output_file = f"quick_test_{timestamp}.txt"
    
    # Nagłówek pliku
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Szybki test modeli LLM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Testowane modele: {', '.join(models)}\n")
        f.write("="*100 + "\n\n")
    
    test_prompts = get_quick_test_prompts()
    print(f"Rozpoczynam szybki test {len(models)} modeli z {len(test_prompts)} zadaniami...")
    print(f"Wyniki będą zapisywane do: {output_file}")
    
    results = []
    total_tests = len(test_prompts) * len(models)
    current_test = 0
    
    for i, test in enumerate(test_prompts, 1):
        print(format_test_header(test['name'], i, len(test_prompts)))
        
        for j, model in enumerate(models, 1):
            current_test += 1
            print_progress_bar(
                current_test, 
                total_tests, 
                prefix=f'Model {j}/{len(models)} ({model}):', 
                suffix=f'({current_test}/{total_tests})'
            )
            
            result = ask_ollama(model, test['prompt'], test['name'], output_file, **test.get('options', {}))
            if result:
                results.append(result)
            
            time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
    
    # Podsumowanie wyników
    summary = generate_summary(results, output_file)
    print(summary)
    print(f"\nSzybki test zakończony! Wyniki zapisane w: {output_file}")


def interactive_chat():
    """Interaktywny czat z wybranym modelem"""
    models = get_available_models()
    
    if not models:
        print("Nie znaleziono dostępnych modeli.")
        return
    
    print("Dostępne modele:")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")
    
    while True:
        try:
            choice = input(f"\nWybierz model (1-{len(models)}) lub 'q' aby wyjść: ").strip()
            if choice.lower() == 'q':
                break
                
            model_index = int(choice) - 1
            if 0 <= model_index < len(models):
                selected_model = models[model_index]
                print(f"\nWybrany model: {selected_model}")
                print("Rozpoczynam czat (wpisz 'quit' aby zakończyć)")
                
                chat_with_model(selected_model)
                break
            else:
                print("Nieprawidłowy wybór!")
        except ValueError:
            print("Nieprawidłowy wybór!")
        except KeyboardInterrupt:
            print("\nWyjście...")
            break


def chat_with_model(model):
    """Prowadzi czat z wybranym modelem"""
    timestamp = get_timestamp()
    chat_file = f"chat_{model.replace(':', '_')}_{timestamp}.txt"
    
    with open(chat_file, 'w', encoding='utf-8') as f:
        f.write(f"Czat z modelem {model} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
    
    print(f"Rozpoczęto czat. Historia będzie zapisywana w: {chat_file}")
    
    while True:
        try:
            user_input = input(f"\n[Ty]: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Zakończono czat.")
                break
            
            if not user_input:
                continue
            
            print(f"[{model}]: ", end="", flush=True)
            
            # Zapisz pytanie użytkownika do pliku
            with open(chat_file, 'a', encoding='utf-8') as f:
                f.write(f"[Ty]: {user_input}\n")
                f.write(f"[{model}]: ")
            
            # Uzyskaj odpowiedź od modelu
            result = ask_ollama(model, user_input, "Czat", chat_file, temperature=0.7)
            
            if not result:
                print("\nBłąd podczas komunikacji z modelem.")
            
        except KeyboardInterrupt:
            print("\n\nWyjście...")
            break
        except Exception as e:
            print(f"\nBłąd: {e}")


def main():
    """Główna funkcja aplikacji"""
    print("=== OLLAMA BASIC CHAT v2.0 ===")
    print("Zmigrowany do modułowej architektury")
    print("=" * 40)
    print("1. Interaktywny czat z wybranym modelem")
    print("2. Kompleksowy test wszystkich modeli") 
    print("3. Szybki test wszystkich modeli")
    print("4. Własne pytanie do wszystkich modeli")
    
    choice = input("\nWybierz opcję (1-4): ").strip()
    
    if choice == "1":
        interactive_chat()
    elif choice == "2":
        run_comprehensive_test()
    elif choice == "3":
        run_quick_test()
    elif choice == "4":
        prompt = input("Wpisz swoje pytanie: ").strip()
        if prompt:
            ask_all_models(prompt)
        else:
            print("Nie podano pytania!")
    else:
        print("Nieprawidłowy wybór! Uruchamiam interaktywny czat...")
        interactive_chat()


if __name__ == "__main__":
    main()
