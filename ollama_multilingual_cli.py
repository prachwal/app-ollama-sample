#!/usr/bin/env python3
"""
Ollama Basic Chat CLI - Wielojęzyczny interfejs konsoli
======================================================

Rozszerzona wersja CLI z obsługą wyboru języka testów.
Obsługuje polski i angielski zestaw testów.

Autor: Ollama Testing Team
Wersja: 2.1.0
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
    get_test_prompts_by_language,
    get_available_languages,
    get_language_display_name,
    get_timestamp,
    print_progress_bar,
    format_test_header,
    generate_summary
)
from src.config import DEFAULT_SLEEP_BETWEEN_MODELS


def select_language() -> str:
    """Pozwala użytkownikowi wybrać język testów"""
    print("🌍 Wybór języka testów / Language Selection")
    print("=" * 40)
    
    languages = get_available_languages()
    
    for i, lang in enumerate(languages, 1):
        display_name = get_language_display_name(lang)
        print(f"{i}. {display_name}")
    
    while True:
        try:
            choice = input(f"\nWybierz język (1-{len(languages)}) / Choose language: ").strip()
            if choice.lower() in ['q', 'quit']:
                print("Wyjście / Exit...")
                sys.exit(0)
                
            lang_index = int(choice) - 1
            if 0 <= lang_index < len(languages):
                selected_lang = languages[lang_index]
                print(f"✅ Wybrano język: {get_language_display_name(selected_lang)}")
                return selected_lang
            else:
                print("❌ Nieprawidłowy wybór! / Invalid choice!")
        except ValueError:
            print("❌ Nieprawidłowy wybór! / Invalid choice!")
        except KeyboardInterrupt:
            print("\nWyjście / Exit...")
            sys.exit(0)


def ask_all_models(prompt: str, language: str = "polish"):
    """Zadaje to samo pytanie wszystkim dostępnym modelom"""
    models = get_available_models()
    
    if not models:
        if language == "english":
            print("No available models found.")
        else:
            print("Nie znaleziono dostępnych modeli.")
        return
    
    if language == "english":
        print(f"Found {len(models)} models: {', '.join(models)}")
    else:
        print(f"Znaleziono {len(models)} modeli: {', '.join(models)}")
    
    timestamp = get_timestamp()
    lang_suffix = f"_{language}" if language != "polish" else ""
    output_file = f"single_test{lang_suffix}_{timestamp}.txt"
    
    for model in models:
        test_name = "Single Question" if language == "english" else "Pojedyncze pytanie"
        ask_ollama(model, prompt, test_name, output_file)
        time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)


def run_comprehensive_test(language: str = "polish"):
    """Uruchamia kompletny test wszystkich modeli ze wszystkimi zadaniami"""
    models = get_available_models()
    
    if not models:
        if language == "english":
            print("No available models found.")
        else:
            print("Nie znaleziono dostępnych modeli.")
        return
    
    # Utwórz plik wyników z timestampem
    timestamp = get_timestamp()
    lang_suffix = f"_{language}" if language != "polish" else ""
    output_file = f"test_results{lang_suffix}_{timestamp}.txt"
    
    # Nagłówek pliku
    with open(output_file, 'w', encoding='utf-8') as f:
        if language == "english":
            f.write(f"LLM Models Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Language: English\n")
            f.write(f"Tested models: {', '.join(models)}\n")
        else:
            f.write(f"Test modeli LLM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Język: Polski\n")
            f.write(f"Testowane modele: {', '.join(models)}\n")
        f.write("="*100 + "\n\n")
    
    test_prompts = get_test_prompts_by_language(language, "comprehensive")
    
    if language == "english":
        print(f"Starting test of {len(models)} models with {len(test_prompts)} tasks...")
        print(f"Results will be saved to: {output_file}")
    else:
        print(f"Rozpoczynam test {len(models)} modeli z {len(test_prompts)} zadaniami...")
        print(f"Wyniki będą zapisywane do: {output_file}")
    
    results = []
    total_tests = len(test_prompts) * len(models)
    current_test = 0
    
    for i, test in enumerate(test_prompts, 1):
        print(format_test_header(test['name'], i, len(test_prompts)))
        
        for j, model in enumerate(models, 1):
            current_test += 1
            prefix = f'Model {j}/{len(models)} ({model}):'
            suffix = f'({current_test}/{total_tests})'
            print_progress_bar(current_test, total_tests, prefix=prefix, suffix=suffix)
            
            result = ask_ollama(model, test['prompt'], test['name'], output_file, **test.get('options', {}))
            if result:
                results.append(result)
            
            time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
    
    # Podsumowanie wyników
    summary = generate_summary(results, output_file)
    print(summary)
    
    if language == "english":
        print(f"\nTest completed! Results saved in: {output_file}")
    else:
        print(f"\nTest zakończony! Wyniki zapisane w: {output_file}")


def run_quick_test(language: str = "polish"):
    """Uruchamia szybki test wszystkich modeli z podstawowymi zadaniami"""
    models = get_available_models()
    
    if not models:
        if language == "english":
            print("No available models found.")
        else:
            print("Nie znaleziono dostępnych modeli.")
        return
    
    # Utwórz plik wyników z timestampem
    timestamp = get_timestamp()
    lang_suffix = f"_{language}" if language != "polish" else ""
    output_file = f"quick_test{lang_suffix}_{timestamp}.txt"
    
    # Nagłówek pliku
    with open(output_file, 'w', encoding='utf-8') as f:
        if language == "english":
            f.write(f"Quick LLM Models Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Language: English\n")
            f.write(f"Tested models: {', '.join(models)}\n")
        else:
            f.write(f"Szybki test modeli LLM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Język: Polski\n")
            f.write(f"Testowane modele: {', '.join(models)}\n")
        f.write("="*100 + "\n\n")
    
    test_prompts = get_test_prompts_by_language(language, "quick")
    
    if language == "english":
        print(f"Starting quick test of {len(models)} models with {len(test_prompts)} tasks...")
        print(f"Results will be saved to: {output_file}")
    else:
        print(f"Rozpoczynam szybki test {len(models)} modeli z {len(test_prompts)} zadaniami...")
        print(f"Wyniki będą zapisywane do: {output_file}")
    
    results = []
    total_tests = len(test_prompts) * len(models)
    current_test = 0
    
    for i, test in enumerate(test_prompts, 1):
        print(format_test_header(test['name'], i, len(test_prompts)))
        
        for j, model in enumerate(models, 1):
            current_test += 1
            prefix = f'Model {j}/{len(models)} ({model}):'
            suffix = f'({current_test}/{total_tests})'
            print_progress_bar(current_test, total_tests, prefix=prefix, suffix=suffix)
            
            result = ask_ollama(model, test['prompt'], test['name'], output_file, **test.get('options', {}))
            if result:
                results.append(result)
            
            time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
    
    # Podsumowanie wyników
    summary = generate_summary(results, output_file)
    print(summary)
    
    if language == "english":
        print(f"\nQuick test completed! Results saved in: {output_file}")
    else:
        print(f"\nSzybki test zakończony! Wyniki zapisane w: {output_file}")


def interactive_chat(language: str = "polish"):
    """Interaktywny czat z wybranym modelem"""
    models = get_available_models()
    
    if not models:
        if language == "english":
            print("No available models found.")
        else:
            print("Nie znaleziono dostępnych modeli.")
        return
    
    if language == "english":
        print("Available models:")
    else:
        print("Dostępne modele:")
    
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")
    
    while True:
        try:
            if language == "english":
                choice = input(f"\nChoose model (1-{len(models)}) or 'q' to exit: ").strip()
            else:
                choice = input(f"\nWybierz model (1-{len(models)}) lub 'q' aby wyjść: ").strip()
            
            if choice.lower() == 'q':
                break
                
            model_index = int(choice) - 1
            if 0 <= model_index < len(models):
                selected_model = models[model_index]
                if language == "english":
                    print(f"\nSelected model: {selected_model}")
                    print("Starting chat (type 'quit' to end)")
                else:
                    print(f"\nWybrany model: {selected_model}")
                    print("Rozpoczynam czat (wpisz 'quit' aby zakończyć)")
                
                chat_with_model(selected_model, language)
                break
            else:
                if language == "english":
                    print("Invalid choice!")
                else:
                    print("Nieprawidłowy wybór!")
        except ValueError:
            if language == "english":
                print("Invalid choice!")
            else:
                print("Nieprawidłowy wybór!")
        except KeyboardInterrupt:
            if language == "english":
                print("\nExiting...")
            else:
                print("\nWyjście...")
            break


def chat_with_model(model: str, language: str = "polish"):
    """Prowadzi czat z wybranym modelem"""
    timestamp = get_timestamp()
    lang_suffix = f"_{language}" if language != "polish" else ""
    chat_file = f"chat_{model.replace(':', '_')}{lang_suffix}_{timestamp}.txt"
    
    with open(chat_file, 'w', encoding='utf-8') as f:
        if language == "english":
            f.write(f"Chat with model {model} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Language: English\n")
        else:
            f.write(f"Czat z modelem {model} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Język: Polski\n")
        f.write("="*80 + "\n\n")
    
    if language == "english":
        print(f"Chat started. History will be saved to: {chat_file}")
        user_prompt = "[You]: "
        quit_commands = ['quit', 'exit', 'q']
    else:
        print(f"Rozpoczęto czat. Historia będzie zapisywana w: {chat_file}")
        user_prompt = "[Ty]: "
        quit_commands = ['quit', 'exit', 'q', 'wyjście', 'koniec']
    
    while True:
        try:
            user_input = input(f"\n{user_prompt}").strip()
            
            if user_input.lower() in quit_commands:
                if language == "english":
                    print("Chat ended.")
                else:
                    print("Zakończono czat.")
                break
            
            if not user_input:
                continue
            
            print(f"[{model}]: ", end="", flush=True)
            
            # Zapisz pytanie użytkownika do pliku
            with open(chat_file, 'a', encoding='utf-8') as f:
                f.write(f"{user_prompt}{user_input}\n")
                f.write(f"[{model}]: ")
            
            # Uzyskaj odpowiedź od modelu
            test_name = "Chat" if language == "english" else "Czat"
            result = ask_ollama(model, user_input, test_name, chat_file, temperature=0.7)
            
            if not result:
                if language == "english":
                    print("\nError communicating with model.")
                else:
                    print("\nBłąd podczas komunikacji z modelem.")
            
        except KeyboardInterrupt:
            if language == "english":
                print("\n\nExiting...")
            else:
                print("\n\nWyjście...")
            break
        except Exception as e:
            if language == "english":
                print(f"\nError: {e}")
            else:
                print(f"\nBłąd: {e}")


def show_main_menu(language: str = "polish"):
    """Wyświetla główne menu"""
    lang_name = get_language_display_name(language)
    
    print("=== OLLAMA BASIC CHAT CLI v2.1 ===")
    print(f"Język testów / Test Language: {lang_name}")
    print("=" * 40)
    
    if language == "english":
        print("1. Interactive chat with selected model")
        print("2. Comprehensive test of all models") 
        print("3. Quick test of all models")
        print("4. Custom question to all models")
        print("5. Change language")
        print("q. Exit")
    else:
        print("1. Interaktywny czat z wybranym modelem")
        print("2. Kompleksowy test wszystkich modeli") 
        print("3. Szybki test wszystkich modeli")
        print("4. Własne pytanie do wszystkich modeli")
        print("5. Zmień język")
        print("q. Wyjście")


def main():
    """Główna funkcja aplikacji"""
    print("🚀 Witaj w Ollama Basic Chat CLI / Welcome to Ollama Basic Chat CLI")
    print()
    
    # Wybór języka
    selected_language = select_language()
    
    while True:
        try:
            print()
            show_main_menu(selected_language)
            
            if selected_language == "english":
                choice = input("\nChoose option (1-5) or 'q' to exit: ").strip()
            else:
                choice = input("\nWybierz opcję (1-5) lub 'q' aby wyjść: ").strip()
            
            if choice.lower() == 'q':
                if selected_language == "english":
                    print("Goodbye!")
                else:
                    print("Do widzenia!")
                break
            elif choice == "1":
                interactive_chat(selected_language)
            elif choice == "2":
                run_comprehensive_test(selected_language)
            elif choice == "3":
                run_quick_test(selected_language)
            elif choice == "4":
                if selected_language == "english":
                    prompt = input("Enter your question: ").strip()
                    if prompt:
                        ask_all_models(prompt, selected_language)
                    else:
                        print("No question provided!")
                else:
                    prompt = input("Wpisz swoje pytanie: ").strip()
                    if prompt:
                        ask_all_models(prompt, selected_language)
                    else:
                        print("Nie podano pytania!")
            elif choice == "5":
                selected_language = select_language()
            else:
                if selected_language == "english":
                    print("Invalid choice! Please try again.")
                else:
                    print("Nieprawidłowy wybór! Spróbuj ponownie.")
                    
        except KeyboardInterrupt:
            if selected_language == "english":
                print("\n\nExiting...")
            else:
                print("\n\nWyjście...")
            break
        except Exception as e:
            if selected_language == "english":
                print(f"\nUnexpected error: {e}")
            else:
                print(f"\nNieoczekiwany błąd: {e}")


if __name__ == "__main__":
    main()
