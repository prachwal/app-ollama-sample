"""
Base tester class providing common functionality for all LLM testers.
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..api import get_available_models, ask_ollama, judge_with_gemini
from ..utils import (
    print_progress_bar, 
    get_gemini_api_key, 
    create_file_header, 
    format_test_header,
    generate_summary
)
from ..config import DEFAULT_SLEEP_BETWEEN_MODELS, GEMINI_JUDGE_MODEL_NAME


class BaseTester:
    """
    Bazowa klasa dla wszystkich testerów LLM.
    Zapewnia wspólną funkcjonalność dla testowania modeli.
    """
    
    def __init__(self, use_judge: bool = True):
        """
        Inicjalizuje bazowy tester.
        
        Args:
            use_judge (bool): Czy używać sędziego AI do oceny odpowiedzi
        """
        self.use_judge = use_judge
        self.gemini_api_key = None
        if use_judge:
            self.gemini_api_key = get_gemini_api_key()
            self.use_judge = self.gemini_api_key is not None
    
    def get_models(self) -> List[str]:
        """
        Pobiera listę dostępnych modeli.
        
        Returns:
            List[str]: Lista nazw modeli
        """
        models = get_available_models()
        if not models:
            print("Nie znaleziono dostępnych modeli.")
            return []
        return models
    
    def run_single_test(
        self, 
        model: str, 
        test: Dict[str, Any], 
        output_file: str
    ) -> Optional[Dict[str, Any]]:
        """
        Uruchamia pojedynczy test dla modelu.
        
        Args:
            model (str): Nazwa modelu
            test (Dict[str, Any]): Definicja testu
            output_file (str): Plik wyjściowy
            
        Returns:
            Optional[Dict[str, Any]]: Wyniki testu lub None w przypadku błędu
        """
        # Użyj timeoutu z opcji promptu, lub domyślnego
        timeout_for_task = test.get('options', {}).get('timeout')
        result = ask_ollama(
            model, 
            test['prompt'], 
            test['name'], 
            output_file, 
            timeout=timeout_for_task, 
            **test.get('options', {})
        )
        
        if result and self.use_judge:
            print("\n--- Ocena sędziego AI ---", end="", flush=True)
            rating, justification = judge_with_gemini(
                result['response'], 
                test['prompt'], 
                self.gemini_api_key
            )
            result['judge_rating'] = rating
            result['judge_justification'] = justification
            
            print(f"\nOcena: {rating}/5")
            print(f"Uzasadnienie: {justification}")
            print("--------------------------\n")
            
            # Zaktualizuj plik wyników o ocenę sędziego
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\nOcena Sędziego AI ({GEMINI_JUDGE_MODEL_NAME}): {rating}/5\n")
                f.write(f"Uzasadnienie Sędziego AI: {justification}\n")
                f.write("="*80 + "\n")
        elif result:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write("="*80 + "\n")
        
        return result
    
    def run_test_suite(
        self, 
        test_prompts: List[Dict[str, Any]], 
        test_name_prefix: str,
        output_file: str
    ) -> List[Dict[str, Any]]:
        """
        Uruchamia zestaw testów dla wszystkich modeli.
        
        Args:
            test_prompts (List[Dict[str, Any]]): Lista testów do wykonania
            test_name_prefix (str): Prefix nazwy testu
            output_file (str): Plik wyjściowy
            
        Returns:
            List[Dict[str, Any]]: Lista wyników testów
        """
        models = self.get_models()
        if not models:
            return []
        
        # Nagłówek pliku
        header = create_file_header(
            test_name_prefix, 
            models, 
            GEMINI_JUDGE_MODEL_NAME, 
            self.use_judge
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(header)
        
        print(f"Rozpoczynam {test_name_prefix.lower()} test {len(models)} modeli z {len(test_prompts)} zadaniami...")
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
                
                result = self.run_single_test(model, test, output_file)
                if result:
                    results.append(result)
                
                time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
        
        # Generuj podsumowanie
        summary = generate_summary(results, output_file)
        print(summary)
        print(f"\n{test_name_prefix} test zakończony! Wyniki zapisane w: {output_file}")
        
        return results
    
    def ask_all_models(self, prompt: str, output_file: str) -> List[Dict[str, Any]]:
        """
        Zadaje to samo pytanie wszystkim dostępnym modelom.
        
        Args:
            prompt (str): Pytanie do zadania
            output_file (str): Plik wyjściowy
            
        Returns:
            List[Dict[str, Any]]: Lista odpowiedzi
        """
        models = self.get_models()
        if not models:
            return []
        
        print(f"Znaleziono {len(models)} modeli: {', '.join(models)}")
        
        results = []
        for model in models:
            result = ask_ollama(model, prompt, "Pojedyncze pytanie", output_file)
            if result:
                results.append(result)
            time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
        
        return results
