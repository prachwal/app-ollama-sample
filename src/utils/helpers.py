"""
Utility functions for the Ollama testing suite.
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional


def print_progress_bar(current: int, total: int, prefix: str = 'Progress:', suffix: str = 'Complete', length: int = 50):
    """
    Wyświetla pasek postępu.
    
    Args:
        current (int): Aktualny postęp
        total (int): Całkowita liczba zadań
        prefix (str): Tekst przed paskiem
        suffix (str): Tekst po pasku
        length (int): Długość paska
    """
    percent = "{0:.1f}".format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
    if current == total:
        print()  # Nowa linia po zakończeniu


def get_timestamp() -> str:
    """
    Zwraca aktualny timestamp w formacie dla nazw plików.
    
    Returns:
        str: Timestamp w formacie YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directory_exists(directory_path: str) -> None:
    """
    Upewnia się, że katalog istnieje, tworzy go jeśli nie.
    
    Args:
        directory_path (str): Ścieżka do katalogu
    """
    os.makedirs(directory_path, exist_ok=True)


def get_gemini_api_key() -> Optional[str]:
    """
    Pobiera klucz API Gemini ze zmiennych środowiskowych lub od użytkownika.
    
    Returns:
        Optional[str]: Klucz API lub None jeśli nie podano
    """
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("\n--- UWAGA: KLUCZ API GEMINI ---")
        print("Aby użyć Gemini jako sędziego, potrzebujesz klucza API.")
        print("Możesz go uzyskać na: https://aistudio.google.com/app/apikey")
        gemini_api_key = input("Wprowadź swój klucz API Gemini: ").strip()
        if not gemini_api_key:
            print("Brak klucza API Gemini. Testy zostaną przeprowadzone BEZ oceny sędziego AI.")
            return None
    else:
        print("Używam klucza API Gemini z zmiennej środowiskowej GEMINI_API_KEY.")
    
    return gemini_api_key


def generate_output_filename(test_type: str, extension: str = "txt") -> str:
    """
    Generuje nazwę pliku wyjściowego z timestampem.
    
    Args:
        test_type (str): Typ testu (comprehensive, quick, etc.)
        extension (str): Rozszerzenie pliku
        
    Returns:
        str: Nazwa pliku z timestampem
    """
    timestamp = get_timestamp()
    return f"{test_type}_test_{timestamp}.{extension}"


def format_test_header(test_name: str, test_number: int, total_tests: int) -> str:
    """
    Formatuje nagłówek testu.
    
    Args:
        test_name (str): Nazwa testu
        test_number (int): Numer testu
        total_tests (int): Całkowita liczba testów
        
    Returns:
        str: Sformatowany nagłówek
    """
    return f"\n{'#'*60}\nTEST {test_number}/{total_tests}: {test_name}\n{'#'*60}"


def create_file_header(test_name_prefix: str, models: List[str], judge_model_name: str, use_judge: bool) -> str:
    """
    Tworzy nagłówek pliku wyników.
    
    Args:
        test_name_prefix (str): Prefix nazwy testu
        models (List[str]): Lista modeli
        judge_model_name (str): Nazwa modelu sędziego
        use_judge (bool): Czy używany jest sędzia AI
        
    Returns:
        str: Sformatowany nagłówek pliku
    """
    header = f"{test_name_prefix} test modeli LLM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"Testowane modele: {', '.join(models)}\n"
    header += f"Sędzia AI: {judge_model_name} (status: {'aktywny' if use_judge else 'nieaktywny'})\n"
    header += "="*100 + "\n\n"
    return header
