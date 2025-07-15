"""
Ollama API communication module.
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional

from ..config import OLLAMA_API_URL, DEFAULT_TIMEOUT_PER_MODEL


def get_available_models() -> List[str]:
    """
    Pobiera listę dostępnych modeli z Ollama.
    
    Returns:
        List[str]: Lista nazw dostępnych modeli
    """
    url = f"{OLLAMA_API_URL}/api/tags"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Wyrzuć wyjątek dla statusów 4xx/5xx
        data = response.json()
        return [model['name'] for model in data.get('models', [])]
    except requests.exceptions.ConnectionError:
        print(f"Błąd połączenia z Ollama na {OLLAMA_API_URL}. Upewnij się, że Ollama jest uruchomiona.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Błąd pobierania modeli: {e}")
        return []


def ask_ollama(
    model: str, 
    prompt: str, 
    test_name: str = "", 
    output_file: Optional[str] = None, 
    timeout: Optional[int] = None,
    system_prompt: Optional[str] = None,
    **model_options
) -> Optional[Dict[str, Any]]:
    """
    Zadaje pytanie do modelu Ollama z pełną obsługą błędów i logowaniem.
    
    Args:
        model (str): Nazwa modelu do testowania
        prompt (str): Tekst pytania
        test_name (str): Nazwa testu dla logowania
        output_file (str): Ścieżka do pliku wyników
        timeout (int): Timeout w sekundach
        system_prompt (str): Opcjonalny prompt systemowy (persona/context)
        **model_options: Dodatkowe opcje dla modelu (temperature, top_p, etc.)
        
    Returns:
        dict: Wyniki testu z metrykami lub None w przypadku błędu
    """
    url = f"{OLLAMA_API_URL}/api/generate"
    
    options = {
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 0.9,
        "num_predict": -1,
    }
    options.update(model_options)

    # Przygotuj prompt z system prompt jeśli podano
    final_prompt = prompt
    if system_prompt and system_prompt.strip():
        # Dodaj system prompt na początku
        final_prompt = f"{system_prompt.strip()}\n\nUser: {prompt}\n\nAssistant:"

    payload = {
        "model": model,
        "prompt": final_prompt,
        "options": options
    }
    
    current_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT_PER_MODEL

    try:
        start_time = time.time()
        response = requests.post(url, json=payload, stream=True, timeout=current_timeout)
        response.raise_for_status()

        result_header = f"\n{'='*80}\n"
        result_header += f"Test: {test_name}\n"
        result_header += f"Model: {model}\n"
        if system_prompt and system_prompt.strip():
            result_header += f"Tryb systemowy: {system_prompt[:100]}{'...' if len(system_prompt) > 100 else ''}\n"
        result_header += f"Pytanie: {prompt}\n"
        result_header += "Odpowiedź: "
        
        print(result_header, end="", flush=True)
        
        first_token_time = None
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode())
                    if 'response' in data:
                        if first_token_time is None:
                            first_token_time = time.time()
                        print(data['response'], end="", flush=True)
                        full_response += data['response']
                    
                    if data.get('done', False):
                        end_time = time.time()
                        total_time = end_time - start_time
                        first_token_delay = first_token_time - start_time if first_token_time else 0
                        
                        timing_info = f"\n\nCzas odpowiedzi:"
                        timing_info += f"\n  - Pierwszy token: {first_token_delay:.2f}s"
                        timing_info += f"\n  - Całkowity czas: {total_time:.2f}s"
                        timing_info += f"\n  - Długość odpowiedzi: {len(full_response)} znaków\n"
                        
                        print(timing_info)
                        
                        # Zapisz do pliku jeśli podano (tylko surowa odpowiedź + timing)
                        if output_file:
                            with open(output_file, 'a', encoding='utf-8') as f:
                                f.write(result_header + full_response + timing_info + "\n")
                        
                        return {
                            'model': model,
                            'test_name': test_name,
                            'prompt': prompt,
                            'response': full_response,
                            'first_token_time': first_token_delay,
                            'total_time': total_time,
                            'response_length': len(full_response)
                        }
                        
                except json.JSONDecodeError:
                    continue
                
    except requests.exceptions.Timeout:
        error_msg = f"\n\nTIMEOUT: Model {model} przekroczył limit {current_timeout}s."
        print(error_msg)
        if output_file:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{result_header}(Brak pełnej odpowiedzi z powodu timeoutu)\n{error_msg}\n")
        return None
    except requests.exceptions.RequestException as e:
        error_msg = f"\n\nBłąd zapytania HTTP dla modelu {model}: {e}"
        print(error_msg)
        if output_file:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{result_header}(Błąd połączenia/zapytania)\n{error_msg}\n")
        return None
    except Exception as e:
        error_msg = f"\n\nNieoczekiwany błąd podczas pytania do modelu {model}: {e}"
        print(error_msg)
        if output_file:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{result_header}(Nieoczekiwany błąd)\n{error_msg}\n")
        return None


def ask_ollama_stream(
    model: str, 
    prompt: str, 
    token_callback,
    test_name: str = "", 
    output_file: Optional[str] = None, 
    timeout: Optional[int] = None,
    system_prompt: Optional[str] = None,
    **model_options
) -> Optional[Dict[str, Any]]:
    """
    Zadaje pytanie do modelu Ollama ze streamingiem dla GUI.
    
    Args:
        model (str): Nazwa modelu do testowania
        prompt (str): Tekst pytania
        token_callback (callable): Funkcja wywoływana dla każdego tokenu (token_text)
        test_name (str): Nazwa testu dla logowania
        output_file (str): Ścieżka do pliku wyników
        timeout (int): Timeout w sekundach
        system_prompt (str): Opcjonalny prompt systemowy
        **model_options: Dodatkowe opcje modelu (temperature, top_p, etc.)
    
    Returns:
        Optional[Dict[str, Any]]: Słownik z wynikami lub None w przypadku błędu
        {
            'response': str,
            'prompt_eval_count': int,
            'eval_count': int,
            'total_duration': int,
            'first_token_time': float,
            'total_time': float
        }
    """
    url = f"{OLLAMA_API_URL}/api/generate"
    
    # Przygotuj payload z opcjami
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": model_options
    }
    
    # Dodaj prompt systemowy jeśli podany
    if system_prompt and system_prompt.strip():
        payload["system"] = system_prompt
    
    current_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT_PER_MODEL

    try:
        start_time = time.time()
        response = requests.post(url, json=payload, stream=True, timeout=current_timeout)
        response.raise_for_status()

        first_token_time = None
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode())
                    if 'response' in data:
                        token_text = data['response']
                        if first_token_time is None:
                            first_token_time = time.time()
                        
                        # Wywołaj callback dla każdego tokenu
                        if token_callback:
                            token_callback(token_text)
                        
                        full_response += token_text
                    
                    if data.get('done', False):
                        end_time = time.time()
                        total_time = end_time - start_time
                        first_token_delay = first_token_time - start_time if first_token_time else 0
                        
                        # Zapisz do pliku jeśli podano
                        if output_file:
                            with open(output_file, 'a', encoding='utf-8') as f:
                                f.write(full_response + "\n")
                        
                        return {
                            'response': full_response,
                            'prompt_eval_count': data.get('prompt_eval_count', 0),
                            'eval_count': data.get('eval_count', 0),
                            'total_duration': data.get('total_duration', 0),
                            'first_token_time': first_token_delay,
                            'total_time': total_time
                        }
                
                except json.JSONDecodeError as e:
                    print(f"Błąd parsowania JSON: {e}, linia: {line}")
                    continue
        
        # Jeśli pętla się skończyła bez 'done'
        return {
            'response': full_response,
            'error': 'Niekompletna odpowiedź'
        }
        
    except requests.exceptions.Timeout:
        error_msg = f"Timeout ({current_timeout}s) dla modelu {model}"
        print(f"❌ {error_msg}")
        return {'error': error_msg}
    except requests.exceptions.ConnectionError:
        error_msg = f"Błąd połączenia z Ollama na {OLLAMA_API_URL}"
        print(f"❌ {error_msg}")
        return {'error': error_msg}
    except requests.exceptions.RequestException as e:
        error_msg = f"Błąd API: {e}"
        print(f"❌ {error_msg}")
        return {'error': error_msg}
    except Exception as e:
        error_msg = f"Niespodziewany błąd: {e}"
        print(f"❌ {error_msg}")
        return {'error': error_msg}
