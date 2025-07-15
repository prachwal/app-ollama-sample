import requests
import json
import time
import os
from datetime import datetime
import signal
from functools import reduce
from functools import reduce
import pickle
import csv
from pathlib import Path

# --- Konfiguracja (można przenieść do osobnego pliku config.py/json) ---
OLLAMA_API_URL = "http://localhost:11434"
DEFAULT_TIMEOUT_PER_MODEL = 180 # Domyślny timeout dla pojedynczej odpowiedzi modelu testowanego
DEFAULT_SLEEP_BETWEEN_MODELS = 2 # Domyślna pauza między modelami testowanymi

# Konfiguracja dla modelu sędziego (Gemini)
# Upewnij się, że masz klucz API do Gemini. Nie umieszczaj go tutaj na stałe!
# Zostanie poproszony o niego w trakcie działania skryptu.
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_JUDGE_MODEL_NAME = "gemini-2.5-flash" # Zaktualizowano na Gemini 2.5 Flash
GEMINI_JUDGE_TIMEOUT = 60 # Timeout dla odpowiedzi modelu sędziego
# --- Koniec konfiguracji ---

# --- Konfiguracja cache ---
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "models_metadata.pkl"
CACHE_EXPIRY_HOURS = 24  # Cache ważny przez 24 godziny

def get_available_models():
    """
    Pobiera listę dostępnych modeli z Ollama wraz z podstawowymi metadanymi.
    Zwraca listę słowników, gdzie każdy słownik reprezentuje model
    i zawiera klucze takie jak 'name', 'modified_at', 'size', 'digest'.
    """
    url = f"{OLLAMA_API_URL}/api/tags"
    try:
        response = requests.get(url)
        response.raise_for_status() # Wyrzuć wyjątek dla statusów 4xx/5xx
        data = response.json()
        # Zwracamy pełne słowniki modeli, a nie tylko ich nazwy
        return data.get('models', [])
    except requests.exceptions.ConnectionError:
        print(f"Błąd połączenia z Ollama na {OLLAMA_API_URL}. Upewnij się, że Ollama jest uruchomiona.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Błąd pobierania modeli: {e}")
        return []

def get_all_models_with_detailed_metadata():
    """
    Pobiera listę wszystkich modeli z Ollama wraz ze szczegółowymi metadanymi.
    Wykorzystuje endpointy /api/tags i /api/show.
    """
    basic_models_info = get_available_models()
    if not basic_models_info:
        print("Brak dostępnych modeli Ollama do pobrania szczegółowych metadanych.")
        return []

    detailed_models = []
    print("\nPobieram szczegółowe metadane dla modeli Ollama (może chwilę potrwać)...")
    for model_info in basic_models_info:
        model_name = model_info['name']
        url = f"{OLLAMA_API_URL}/api/show"
        payload = {"name": model_name}
        
        try:
            response = requests.post(url, json=payload, timeout=30) # Krótszy timeout dla show
            response.raise_for_status()
            detailed_data = response.json()
            
            # Łączymy podstawowe info z /api/tags z szczegółami z /api/show
            combined_data = {**model_info, **detailed_data}
            detailed_models.append(combined_data)
            print(f" - Pobrane szczegóły dla: {model_name}")
        except requests.exceptions.RequestException as e:
            print(f" - Błąd pobierania szczegółów dla {model_name}: {e}")
            # Dodajemy model z podstawowymi informacjami, jeśli szczegóły nie mogły być pobrane
            detailed_models.append(model_info) 
        except Exception as e:
            print(f" - Nieoczekiwany błąd dla {model_name}: {e}")
            detailed_models.append(model_info)

    return detailed_models


def ask_ollama(model, prompt, test_name="", output_file=None, timeout=None, **model_options):
    """Zadaje pytanie do wybranego modelu z Ollama z timeoutem i dodatkowymi opcjami"""
    url = f"{OLLAMA_API_URL}/api/generate"
    
    options = {
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 0.9,
        "num_predict": -1,
    }
    options.update(model_options)

    payload = {
        "model": model,
        "prompt": prompt,
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
                        timing_info += f"\n  - Pierwszy token: {first_token_delay:.2f}s"
                        timing_info += f"\n  - Całkowity czas: {total_time:.2f}s"
                        timing_info += f"\n  - Długość odpowiedzi: {len(full_response)} znaków\n"
                        
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

def judge_with_llm(model_response, original_prompt, gemini_api_key, judge_model_name=GEMINI_JUDGE_MODEL_NAME):
    """
    Wykorzystuje zewnętrzny model LLM (Gemini) jako sędziego do oceny jakości odpowiedzi.
    Zwraca ocenę (int z 1-5) i uzasadnienie.
    """
    judge_prompt = f"""Oceń jakość poniższej odpowiedzi na oryginalne pytanie.
    Twoja ocena powinna dotyczyć:
    1. Poprawności (czy odpowiedź jest prawdziwa/logiczna?).
    2. Kompletności (czy odpowiedź w pełni odnosi się do pytania?).
    3. Zrozumiałości (czy odpowiedź jest jasna i dobrze sformułowana?).
    4. Zgodności z instrukcją (czy odpowiedź spełnia wszystkie wymogi pytania, np. format kodu, komentarze?).

    Twoja ocena powinna być w skali od 1 (bardzo słaba) do 5 (doskonała).
    Następnie uzasadnij swoją ocenę w kilku zdaniach.

    Format odpowiedzi:
    OCENA: [liczba od 1 do 5]
    UZASADNIENIE: [Twoje uzasadnienie]

    ---
    ORYGINALNE PYTANIE:
    {original_prompt}

    ---
    ODPOWIEDŹ DO OCENY:
    {model_response}
    """
    
    # URL dla API Gemini
    api_url = f"{GEMINI_API_URL}/{judge_model_name}:generateContent?key={gemini_api_key}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": judge_prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2, # Niższa temperatura dla bardziej deterministycznych ocen
            "maxOutputTokens": 300 # Ogranicz długość odpowiedzi sędziego
        }
    }

    try:
        headers = {'Content-Type': 'application/json'}
        judge_response = requests.post(api_url, headers=headers, json=payload, timeout=GEMINI_JUDGE_TIMEOUT)
        judge_response.raise_for_status() # Sprawdź błędy HTTP
        
        result_data = judge_response.json()
        
        # Parsowanie odpowiedzi Gemini
        if result_data and 'candidates' in result_data and len(result_data['candidates']) > 0:
            if 'content' in result_data['candidates'][0] and 'parts' in result_data['candidates'][0]['content'] and len(result_data['candidates'][0]['content']['parts']) > 0:
                judge_full_response = result_data['candidates'][0]['content']['parts'][0]['text']
            else:
                judge_full_response = "Brak treści odpowiedzi od sędziego."
        else:
            judge_full_response = "Nieprawidłowa struktura odpowiedzi od sędziego."
        
        # Parsowanie oceny i uzasadnienia z tekstu odpowiedzi sędziego
        rating = 0
        justification = "Brak uzasadnienia."
        
        lines = judge_full_response.split('\n')
        for line in lines:
            if line.startswith("OCENA:"):
                try:
                    rating = int(line.split(":")[1].strip())
                    if not (1 <= rating <= 5): # Upewnij się, że ocena jest w zakresie
                        rating = 0 
                except (ValueError, IndexError):
                    rating = 0 # Nie udało się sparsować
            elif line.startswith("UZASADNIENIE:"):
                justification = line.split(":", 1)[1].strip()
                
        return rating, justification
        
    except requests.exceptions.Timeout:
        print(f"\nBłąd: Model sędzia ({judge_model_name}) przekroczył limit {GEMINI_JUDGE_TIMEOUT}s.")
        return 0, f"Błąd sędziego: Timeout ({GEMINI_JUDGE_TIMEOUT}s)"
    except requests.exceptions.RequestException as e:
        print(f"\nBłąd zapytania HTTP do modelu sędziego ({judge_model_name}): {e}")
        return 0, f"Błąd sędziego: Błąd HTTP ({e})"
    except Exception as e:
        print(f"\nNieoczekiwany błąd w funkcji sędziego: {e}")
        return 0, f"Nieoczekiwany błąd sędziego: {e}"

def get_test_prompts():
    """Zwraca zestaw testów do oceny modeli LLM z opcjami dla modeli"""
    return [
        {
            "name": "Przedstawienie",
            "prompt": "Przedstaw się krótko - kim jesteś i jakie masz możliwości?",
            "options": {"temperature": 0.7, "num_predict": 500}
        },
        {
            "name": "Zadanie programistyczne - Python",
            "prompt": "Napisz funkcję w Pythonie, która znajduje wszystkie liczby pierwsze mniejsze od n używając sita Eratostenesa. Dodaj komentarze i przykład użycia.",
            "options": {"temperature": 0.3, "num_predict": 2000, "top_p": 0.95}
        },
        {
            "name": "Zadanie programistyczne - JavaScript",
            "prompt": "Napisz funkcję JavaScript, która implementuje debounce z delay 300ms. Pokaż przykład użycia z obsługą kliknięć przycisku.",
            "options": {"temperature": 0.3, "num_predict": 1500, "top_p": 0.95}
        },
        {
            "name": "Analiza sentymentu",
            "prompt": "Oceń sentyment następującego tekstu na skali od -5 (bardzo negatywny) do +5 (bardzo pozytywny) i uzasadnij swoją ocenę:\n\n'Ten produkt to kompletna porażka! Nie działał od pierwszego dnia, obsługa klienta ignoruje moje wiadomości, a zwrot pieniędzy to koszmar. Zdecydowanie odradzam!'",
            "options": {"temperature": 0.5, "num_predict": 300}
        },
        {
            "name": "Logiczne rozumienie",
            "prompt": "Rozwiąż zagadkę logiczną: Mam 3 pudełka - czerwone, niebieskie i zielone. W każdym jest jedna piłka: czerwona, niebieska lub zielona. Wiem, że: 1) czerwona piłka nie jest w czerwonym pudełku, 2) niebieska piłka nie jest w niebieskim pudełku, 3) zielona piłka jest w czerwonym pudełku. Gdzie jest każda piłka?",
            "options": {"temperature": 0.1, "num_predict": 200}
        },
        {
            "name": "Streszczenie tekstu",
            "prompt": "Streć w 2-3 zdaniach następujący tekst:\n\n'Sztuczna inteligencja (AI) to dziedzina informatyki zajmująca się tworzeniem systemów zdolnych do wykonywania zadań wymagających ludzkiej inteligencji. Obejmuje to uczenie maszynowe, przetwarzanie języka naturalnego, rozpoznawanie obrazów i podejmowanie decyzji. AI ma szerokie zastosowania - od asystentów głosowych, przez systemy rekomendacji, po autonomiczne pojazdy. Rozwój AI niesie ogromne możliwości, ale także wyzwania etyczne i społeczne, które wymagają odpowiedzialnego podejścia do implementacji tych technologii.'",
            "options": {"temperature": 0.6, "num_predict": 150}
        },
        {
            "name": "Kreatywne pisanie",
            "prompt": "Napisz krótką historię (3-4 akapity) o robocie, który po raz pierwszy doświadcza emocji. Historia powinna mieć beginning, middle i end.",
            "options": {"temperature": 0.8, "num_predict": 500}
        },
        {
            "name": "Analiza danych - SQL",
            "prompt": "Napisz zapytanie SQL, które znajdzie top 5 klientów według łącznej wartości zamówień w ostatnim roku. Załóż tabele: customers(id, name), orders(id, customer_id, order_date, total_amount).",
            "options": {"temperature": 0.3, "num_predict": 300}
        },
        {
            "name": "Matematyka",
            "prompt": "Wyjaśnij krok po kroku, jak rozwiązać równanie kwadratowe: 2x² - 7x + 3 = 0",
            "options": {"temperature": 0.1, "num_predict": 400}
        },
        {
            "name": "Tłumaczenie i kontekst kulturowy",
            "prompt": "Przetłumacz na angielski i wyjaśnij kontekst kulturowy: 'Nie ma to jak u mamy' - polskie przysłowie.",
            "options": {"temperature": 0.5, "num_predict": 300}
        }
    ]

def get_quick_test_prompts():
    """Zwraca skrócony zestaw testów do szybkiej oceny modeli z opcjami"""
    return [
        {
            "name": "Przedstawienie",
            "prompt": "Przedstaw się krótko - kim jesteś i jakie masz możliwości?",
            "options": {"temperature": 0.7, "num_predict": 300}
        },
        {
            "name": "Programowanie - Python",
            "prompt": "Napisz prostą funkcję Python, która sprawdza czy liczba jest parzysta.",
            "options": {"temperature": 0.3, "num_predict": 200}
        },
        {
            "name": "Analiza sentymentu",
            "prompt": "Oceń sentyment tekstu od -5 do +5: 'Ten produkt to kompletna porażka!'",
            "options": {"temperature": 0.5, "num_predict": 100}
        },
        {
            "name": "Matematyka",
            "prompt": "Rozwiąż: 2x + 5 = 13",
            "options": {"temperature": 0.1, "num_predict": 150}
        },
        {
            "name": "Logika",
            "prompt": "Jeśli wszyscy ludzie są śmiertelni, a Sokrates jest człowiekiem, to czy Sokrates jest śmiertelny?",
            "options": {"temperature": 0.1, "num_predict": 100}
        }
    ]

def ask_all_models(prompt):
    """Zadaje to samo pytanie wszystkim dostępnym modelom (funkcja kompatybilna wstecz)"""
    models = get_available_models()
    
    if not models:
        print("Nie znaleziono dostępnych modeli.")
        return
    
    # Wyciągamy tylko nazwy modeli do wyświetlenia
    model_names = [model['name'] for model in models]
    print(f"Znaleziono {len(model_names)} modeli: {', '.join(model_names)}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"single_test_{timestamp}.txt"
    
    for model_info in models: # Iterujemy po pełnych słownikach modeli
        model_name = model_info['name']
        # Tutaj nie ma oceny sędziego, bo to pojedyncze pytanie
        ask_ollama(model_name, prompt, "Pojedyncze pytanie", output_file)
        time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)


def run_test_with_judge(test_type="comprehensive"):
    """Uruchamia test wszystkich modeli z oceną AI sędziego."""
    models_info = get_available_models() # Pobieramy pełne info o modelach
    
    if not models_info:
        print("Nie znaleziono dostępnych modeli.")
        return

    # Wyciągamy tylko nazwy modeli do przekazania do testów
    models = [model['name'] for model in models_info]

    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("\n--- UWAGA: KLUCZ API GEMINI ---")
        print("Aby użyć Gemini jako sędziego, potrzebujesz klucza API.")
        print("Możesz go uzyskać na: https://aistudio.google.com/app/apikey")
        gemini_api_key = input("Wprowadź swój klucz API Gemini: ").strip()
        if not gemini_api_key:
            print("Brak klucza API Gemini. Testy zostaną przeprowadzone BEZ oceny sędziego AI.")
            use_judge = False
        else:
            use_judge = True
    else:
        print("Używam klucza API Gemini z zmiennej środowiskowej GEMINI_API_KEY.")
        use_judge = True

    # Utwórz plik wyników z timestampem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if test_type == "comprehensive":
        output_file = f"test_results_{timestamp}.txt"
        test_prompts = get_test_prompts()
        test_name_prefix = "Kompleksowy"
    else: # quick
        output_file = f"quick_test_{timestamp}.txt"
        test_prompts = get_quick_test_prompts()
        test_name_prefix = "Szybki"
    
    # Nagłówek pliku
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{test_name_prefix} test modeli LLM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Testowane modele: {', '.join(models)}\n")
        f.write(f"Sędzia AI: {GEMINI_JUDGE_MODEL_NAME} (status: {'aktywny' if use_judge else 'nieaktywny'})\n")
        f.write("="*100 + "\n\n")
    
    print(f"Rozpoczynam {test_name_prefix.lower()} test {len(models)} modeli z {len(test_prompts)} zadaniami...")
    print(f"Wyniki będą zapisywane do: {output_file}")
    
    results = []
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n{'#'*60}")
        print(f"TEST {i}/{len(test_prompts)}: {test['name']}")
        print(f"{'#'*60}")
        
        for model_name in models: # Iterujemy po nazwach modeli
            # Użyj timeoutu z opcji promptu, lub domyślnego
            timeout_for_task = test.get('options', {}).get('timeout', DEFAULT_TIMEOUT_PER_MODEL)
            result = ask_ollama(model_name, test['prompt'], test['name'], output_file, timeout=timeout_for_task, **test.get('options', {}))
            
            if result and use_judge: # Tylko jeśli klucz API Gemini jest dostępny
                print("\n--- Ocena sędziego AI ---", end="", flush=True)
                rating, justification = judge_with_llm(result['response'], test['prompt'], gemini_api_key)
                result['judge_rating'] = rating
                result['judge_justification'] = justification
                
                print(f"\nOcena: {rating}/5")
                print(f"Uzasadnienie: {justification}")
                print("--------------------------\n")
                
                # Zaktualizuj plik wyników o ocenę sędziego
                if output_file:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(f"\nOcena Sędziego AI ({GEMINI_JUDGE_MODEL_NAME}): {rating}/5\n")
                        f.write(f"Uzasadnienie Sędziego AI: {justification}\n")
                        f.write("="*80 + "\n") # Oddzielenie kolejnego modelu
                        
            elif result: # Jeśli nie ma sędziego, ale wynik jest OK
                 if output_file:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write("="*80 + "\n") # Oddzielenie kolejnego modelu
            
            if result:
                results.append(result)
            
            time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
    
    generate_summary(results, output_file)
    print(f"\n{test_name_prefix} test zakończony! Wyniki zapisane w: {output_file}")


def generate_summary(results, output_file):
    """Generuje podsumowanie wyników testów"""
    if not results:
        return
    
    summary = f"\n{'='*100}\n"
    summary += "PODSUMOWANIE WYNIKÓW\n"
    summary += f"{'='*100}\n\n"
    
    models = list(set(r['model'] for r in results))
    
    summary += "Średnie czasy odpowiedzi i oceny jakości:\n"
    summary += "-" * 60 + "\n"
    
    for model in models:
        model_results = [r for r in results if r['model'] == model]
        if model_results:
            avg_first_token = sum(r['first_token_time'] for r in model_results) / len(model_results)
            avg_total_time = sum(r['total_time'] for r in model_results) / len(model_results)
            avg_length = sum(r['response_length'] for r in model_results) / len(model_results)
            
            # Oblicz średnią ocenę sędziego, jeśli dostępne
            judge_ratings = [r['judge_rating'] for r in model_results if 'judge_rating' in r and r['judge_rating'] > 0]
            avg_judge_rating = sum(judge_ratings) / len(judge_ratings) if judge_ratings else "N/A"
            
            summary += f"{model}:\n"
            summary += f"  - Średni czas pierwszego tokena: {avg_first_token:.2f}s\n"
            summary += f"  - Średni całkowity czas: {avg_total_time:.2f}s\n"
            summary += f"  - Średnia długość odpowiedzi: {avg_length:.0f} znaków\n"
            summary += f"  - Zakończonych testów: {len(model_results)}\n"
            summary += f"  - Średnia ocena sędziego AI: {avg_judge_rating:.2f}/5\n" if isinstance(avg_judge_rating, float) else f"  - Średnia ocena sędziego AI: {avg_judge_rating}\n"
            summary += "\n"
    
    summary += "Ranking szybkości (pierwszy token - niżej = szybciej):\n"
    summary += "-" * 60 + "\n"
    
    model_speed = {}
    for model in models:
        model_results = [r for r in results if r['model'] == model]
        if model_results:
            model_speed[model] = sum(r['first_token_time'] for r in model_results) / len(model_results)
    
    sorted_models_speed = sorted(model_speed.items(), key=lambda x: x[1])
    for i, (model, speed) in enumerate(sorted_models_speed, 1):
        summary += f"{i}. {model}: {speed:.2f}s\n"

    summary += "\nRanking jakości (ocena sędziego AI - wyżej = lepiej):\n"
    summary += "-" * 60 + "\n"

    model_quality = {}
    for model in models:
        model_results = [r for r in results if r['model'] == model]
        if model_results:
            judge_ratings = [r['judge_rating'] for r in model_results if 'judge_rating' in r and r['judge_rating'] > 0]
            if judge_ratings:
                model_quality[model] = sum(judge_ratings) / len(judge_ratings)
    
    if model_quality:
        sorted_models_quality = sorted(model_quality.items(), key=lambda x: x[1], reverse=True)
        for i, (model, quality) in enumerate(sorted_models_quality, 1):
            summary += f"{i}. {model}: {quality:.2f}/5\n"
    else:
        summary += "Brak danych o ocenach sędziego AI (upewnij się, że klucz API Gemini jest poprawny).\n"
        
    print(summary)
    
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(summary)

def get_enhanced_model_metadata():
    """
    Pobiera rozszerzone metadane modeli z bardziej użytecznymi informacjami.
    Ekstrakcja kluczowych danych technicznych w czytelnej formie.
    """
    detailed_models = get_all_models_with_detailed_metadata()
    enhanced_models = []
    
    for model_data in detailed_models:
        # Podstawowe informacje
        enhanced_info = {
            'name': model_data.get('name', 'N/A'),
            'size_bytes': model_data.get('size', 0),
            'size_gb': round(model_data.get('size', 0) / (1024**3), 2),
            'modified_at': model_data.get('modified_at', 'N/A'),
            'digest': model_data.get('digest', 'N/A')[:12],  # Skrócona wersja
        }
        
        # Szczegóły z /api/tags
        details = model_data.get('details', {})
        enhanced_info.update({
            'family': details.get('family', 'N/A'),
            'parameter_size': details.get('parameter_size', 'N/A'),
            'quantization': details.get('quantization_level', 'N/A'),
            'format': details.get('format', 'N/A')
        })
        
        # Zaawansowane informacje z /api/show
        model_info = model_data.get('model_info', {})
        if model_info:
            # Architektura modelu
            enhanced_info.update({
                'architecture': model_info.get('general.architecture', 'N/A'),
                'context_length': model_info.get(f"{enhanced_info['family']}.context_length", 'N/A'),
                'embedding_length': model_info.get(f"{enhanced_info['family']}.embedding_length", 'N/A'),
                'layers_count': model_info.get(f"{enhanced_info['family']}.block_count", 'N/A'),
                'attention_heads': model_info.get(f"{enhanced_info['family']}.attention.head_count", 'N/A'),
                'parameter_count': model_info.get('general.parameter_count', 'N/A')
            })
            
            # Tokenizer info
            enhanced_info.update({
                'tokenizer_type': model_info.get('tokenizer.ggml.model', 'N/A'),
                'vocab_size': len(model_info.get('tokenizer.ggml.tokens', [])) if model_info.get('tokenizer.ggml.tokens') else 'N/A',
                'bos_token_id': model_info.get('tokenizer.ggml.bos_token_id', 'N/A'),
                'eos_token_id': model_info.get('tokenizer.ggml.eos_token_id', 'N/A')
            })
        
        # Capabilities
        enhanced_info['capabilities'] = model_data.get('capabilities', [])
        
        # Tensor statistics
        tensors = model_data.get('tensors', [])
        if tensors:
            enhanced_info.update({
                'tensor_count': len(tensors),
                'weight_types': list(set(t.get('type', 'Unknown') for t in tensors)),
                'total_parameters': sum(
                    reduce(lambda x, y: x * y, t.get('shape', [1]), 1) 
                    for t in tensors
                ) if tensors else 'N/A'
            })
        
        enhanced_models.append(enhanced_info)
    
    return enhanced_models

def is_cache_valid():
    """Sprawdza czy cache jest aktualny"""
    if not CACHE_FILE.exists():
        return False
    
    cache_time = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime)
    current_time = datetime.now()
    age_hours = (current_time - cache_time).total_seconds() / 3600
    
    return age_hours < CACHE_EXPIRY_HOURS

def save_to_cache(data):
    """Zapisuje dane do cache"""
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(data, f)
        print(f"✅ Dane zapisane do cache: {CACHE_FILE}")
    except Exception as e:
        print(f"⚠️ Błąd zapisu do cache: {e}")

def load_from_cache():
    """Ładuje dane z cache"""
    try:
        with open(CACHE_FILE, 'rb') as f:
            data = pickle.load(f)
        print(f"✅ Dane załadowane z cache: {CACHE_FILE}")
        return data
    except Exception as e:
        print(f"⚠️ Błąd odczytu cache: {e}")
        return None

def get_all_models_with_detailed_metadata_cached(force_refresh=False):
    """
    Pobiera listę wszystkich modeli z cache lub API Ollama.
    
    Args:
        force_refresh (bool): Wymuś odświeżenie danych z API
    """
    # Sprawdź cache jeśli nie wymuszamy odświeżenia
    if not force_refresh and is_cache_valid():
        cached_data = load_from_cache()
        if cached_data:
            return cached_data
    
    print("🔄 Pobieranie świeżych danych z API Ollama...")
    
    # Pobierz świeże dane z API
    fresh_data = get_all_models_with_detailed_metadata()
    
    # Zapisz do cache
    if fresh_data:
        save_to_cache(fresh_data)
    
    return fresh_data

def export_models_metadata(models_data, format_type="json", filename=None):
    """
    Eksportuje metadane modeli do różnych formatów.
    
    Args:
        models_data: Lista metadanych modeli
        format_type: 'json', 'csv', 'txt'
        filename: Nazwa pliku (opcjonalne)
    """
    if not models_data:
        print("❌ Brak danych do eksportu")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if filename is None:
        filename = f"models_metadata_{timestamp}"
    
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    try:
        if format_type.lower() == "json":
            filepath = export_dir / f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(models_data, f, indent=2, ensure_ascii=False, default=str)
            
        elif format_type.lower() == "csv":
            filepath = export_dir / f"{filename}.csv"
            
            # Przygotuj dane dla CSV (flatten nested structures)
            csv_data = []
            for model in models_data:
                flat_model = {}
                for key, value in model.items():
                    if isinstance(value, dict):
                        for nested_key, nested_value in value.items():
                            flat_model[f"{key}_{nested_key}"] = nested_value
                    elif isinstance(value, list):
                        flat_model[key] = ", ".join(str(v) for v in value)
                    else:
                        flat_model[key] = value
                csv_data.append(flat_model)
            
            if csv_data:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_data)
            
        elif format_type.lower() == "txt":
            filepath = export_dir / f"{filename}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("RAPORT METADANYCH MODELI OLLAMA\n")
                f.write("=" * 50 + "\n")
                f.write(f"Data generowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Liczba modeli: {len(models_data)}\n\n")
                
                for model in models_data:
                    f.write(f"MODEL: {model.get('name', 'N/A')}\n")
                    f.write("-" * 40 + "\n")
                    for key, value in model.items():
                        if key != 'name':
                            f.write(f"{key}: {value}\n")
                    f.write("\n")
        else:
            print(f"❌ Nieznany format: {format_type}")
            return None
        
        print(f"✅ Eksport zakończony: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Błąd eksportu: {e}")
        return None

def compare_models(models_data, criteria=['parameter_size', 'size_gb', 'context_length', 'quantization']):
    """
    Porównuje modele według wybranych kryteriów.
    
    Args:
        models_data: Lista metadanych modeli  
        criteria: Lista kryteriów do porównania
    """
    if not models_data:
        print("❌ Brak danych do porównania")
        return
    
    print("\n" + "="*80)
    print("🔍 PORÓWNANIE MODELI")
    print("="*80)
    
    # Przygotuj dane do porównania
    comparison_data = []
    for model in models_data:
        model_info = {'name': model.get('name', 'N/A')}
        for criterion in criteria:
            model_info[criterion] = model.get(criterion, 'N/A')
        comparison_data.append(model_info)
    
    # Sortuj według pierwszego kryterium
    if criteria and criteria[0] in ['parameter_size', 'size_gb', 'context_length']:
        try:
            comparison_data.sort(key=lambda x: float(str(x[criteria[0]]).replace('B', '').replace('GB', '')) 
                               if x[criteria[0]] != 'N/A' else 0, reverse=True)
        except:
            pass  # Jeśli sortowanie nie wyjdzie, zostaw oryginalną kolejność
    
    # Wyświetl tabele porównawczą
    print(f"{'Model':<25}", end="")
    for criterion in criteria:
        print(f"{criterion:<15}", end="")
    print()
    print("-" * (25 + len(criteria) * 15))
    
    for model_info in comparison_data:
        print(f"{model_info['name']:<25}", end="")
        for criterion in criteria:
            value = str(model_info.get(criterion, 'N/A'))
            print(f"{value:<15}", end="")
        print()
    
    # Dodaj ranking dla każdego kryterium
    print(f"\n🏆 RANKINGI:")
    for criterion in criteria:
        print(f"\n{criterion.upper()}:")
        
        # Sortuj według aktualnego kryterium
        if criterion in ['size_gb', 'context_length']:
            try:
                sorted_models = sorted(comparison_data, 
                                     key=lambda x: float(str(x[criterion]).replace('GB', '')) 
                                     if x[criterion] != 'N/A' else 0, reverse=True)
            except:
                sorted_models = comparison_data
        elif 'parameter' in criterion:
            try:
                sorted_models = sorted(comparison_data,
                                     key=lambda x: float(str(x[criterion]).replace('B', '')) 
                                     if x[criterion] != 'N/A' else 0, reverse=True)
            except:
                sorted_models = comparison_data
        else:
            sorted_models = comparison_data
        
        for i, model_info in enumerate(sorted_models[:5], 1):  # Top 5
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"  {medal} {i}. {model_info['name']}: {model_info[criterion]}")

def display_enhanced_metadata():
    """Wyświetla rozszerzone metadane w czytelnej formie"""
    enhanced_data = get_enhanced_model_metadata()
    
    if not enhanced_data:
        print("Brak danych o modelach.")
        return
    
    print("\n" + "="*100)
    print("ROZSZERZONE METADANE MODELI OLLAMA")
    print("="*100)
    
    for model in enhanced_data:
        print(f"\n🤖 MODEL: {model['name']}")
        print("-" * 80)
        
        # Podstawowe informacje
        print(f"📊 PODSTAWOWE:")
        print(f"   Rozmiar: {model['size_gb']} GB ({model['size_bytes']:,} bajtów)")
        print(f"   Rodzina: {model['family']}")
        print(f"   Parametry: {model['parameter_size']}")
        print(f"   Kwantyzacja: {model['quantization']}")
        print(f"   Format: {model['format']}")
        print(f"   Zmodyfikowano: {model['modified_at']}")
        
        # Architektura
        if model.get('architecture') != 'N/A':
            print(f"\n🏗️ ARCHITEKTURA:")
            print(f"   Typ: {model['architecture']}")
            print(f"   Warstwy: {model['layers_count']}")
            print(f"   Heads attention: {model['attention_heads']}")
            print(f"   Długość kontekstu: {model['context_length']}")
            print(f"   Embedding: {model['embedding_length']}")
            if model.get('parameter_count') != 'N/A':
                print(f"   Parametry (dokładne): {model['parameter_count']:,}")
        
        # Tokenizer
        if model.get('tokenizer_type') != 'N/A':
            print(f"\n🔤 TOKENIZER:")
            print(f"   Typ: {model['tokenizer_type']}")
            print(f"   BOS token ID: {model['bos_token_id']}")
            print(f"   EOS token ID: {model['eos_token_id']}")
        
        # Tensory
        if model.get('tensor_count'):
            print(f"\n⚙️ TENSORY:")
            print(f"   Liczba tensorów: {model['tensor_count']}")
            print(f"   Typy wag: {', '.join(model['weight_types'])}")
        
        # Możliwości
        if model.get('capabilities'):
            print(f"\n✨ MOŻLIWOŚCI: {', '.join(model['capabilities'])}")

def filter_similar_models(enhanced_data, reference_model_name="gemma2:2b"):
    """
    Filtruje modele o podobnych parametrach do modelu referencyjnego
    
    Args:
        enhanced_data: Lista modeli z rozszerzonymi metadanymi
        reference_model_name: Nazwa modelu referencyjnego (domyślnie gemma2:2b)
    
    Returns:
        Lista modeli o podobnych parametrach
    """
    if not enhanced_data:
        print("❌ Brak danych do filtrowania")
        return []
    
    # Znajdź model referencyjny
    reference_model = None
    for model in enhanced_data:
        if model.get('name') == reference_model_name:
            reference_model = model
            break
    
    if not reference_model:
        print(f"❌ Nie znaleziono modelu referencyjnego: {reference_model_name}")
        print("Dostępne modele:")
        for model in enhanced_data:
            print(f"  - {model.get('name', 'N/A')}")
        return []
    
    print(f"\n🎯 MODEL REFERENCYJNY: {reference_model_name}")
    print(f"   Parametry: {reference_model.get('parameter_size', 'N/A')}")
    print(f"   Rozmiar: {reference_model.get('size_gb', 'N/A')} GB")
    print(f"   Kontekst: {reference_model.get('context_length', 'N/A')}")
    print(f"   Warstwy: {reference_model.get('layers_count', 'N/A')}")
    print(f"   Kwantyzacja: {reference_model.get('quantization', 'N/A')}")
    print(f"   Architektura: {reference_model.get('architecture', 'N/A')}")
    
    # Kryteria filtrowania z tolerancją
    ref_size_gb = reference_model.get('size_gb', 0)
    ref_context = reference_model.get('context_length', 0)
    ref_layers = reference_model.get('layers_count', 0)
    ref_param_count = reference_model.get('parameter_count', 0)
    
    # Konwertuj parameter_size na liczby dla porównania
    def extract_param_number(param_size):
        if isinstance(param_size, str) and param_size != 'N/A':
            # Wyciągnij liczbę z tekstu typu "2.6B", "1.5B" itp.
            import re
            match = re.search(r'(\d+\.?\d*)', param_size)
            if match:
                return float(match.group(1))
        return 0
    
    ref_param_number = extract_param_number(reference_model.get('parameter_size', '0'))
    
    print(f"\n🔍 KRYTERIA FILTROWANIA:")
    print(f"   Rozmiar pliku: {ref_size_gb-0.5:.1f} - {ref_size_gb+0.5:.1f} GB")
    print(f"   Parametry: {ref_param_number-1:.1f} - {ref_param_number+1:.1f}B")
    print(f"   Kontekst: {max(0, ref_context-10000)} - {ref_context+50000}")
    print(f"   Warstwy: {max(0, ref_layers-5)} - {ref_layers+5}")
    
    similar_models = []
    
    for model in enhanced_data:
        if model.get('name') == reference_model_name:
            continue  # Pomiń model referencyjny
        
        model_size_gb = model.get('size_gb', 0)
        model_context = model.get('context_length', 0) if model.get('context_length') != 'N/A' else 0
        model_layers = model.get('layers_count', 0) if model.get('layers_count') != 'N/A' else 0
        model_param_number = extract_param_number(model.get('parameter_size', '0'))
        
        # Sprawdź kryteria podobieństwa
        size_similar = abs(model_size_gb - ref_size_gb) <= 0.5  # ±0.5 GB
        param_similar = abs(model_param_number - ref_param_number) <= 1.0  # ±1B parametrów
        context_similar = abs(model_context - ref_context) <= 50000 if ref_context > 0 else True  # ±50k kontekstu
        layers_similar = abs(model_layers - ref_layers) <= 5 if ref_layers > 0 else True  # ±5 warstw
        
        # Model jest podobny jeśli spełnia przynajmniej 2 z 4 kryteriów
        similarity_score = sum([size_similar, param_similar, context_similar, layers_similar])
        
        if similarity_score >= 2:
            model['similarity_score'] = similarity_score
            model['size_diff'] = abs(model_size_gb - ref_size_gb)
            model['param_diff'] = abs(model_param_number - ref_param_number)
            similar_models.append(model)
    
    # Sortuj według wyniku podobieństwa (malejąco) i różnicy rozmiaru (rosnąco)
    similar_models.sort(key=lambda x: (-x['similarity_score'], x['size_diff']))
    
    print(f"\n📋 ZNALEZIONO {len(similar_models)} PODOBNYCH MODELI:")
    print("-" * 80)
    
    for i, model in enumerate(similar_models, 1):
        print(f"\n{i}. {model.get('name', 'N/A')}")
        print(f"   📊 Wynik podobieństwa: {model['similarity_score']}/4")
        print(f"   📁 Rozmiar: {model.get('size_gb', 'N/A')} GB (różnica: {model['size_diff']:.2f} GB)")
        print(f"   🧠 Parametry: {model.get('parameter_size', 'N/A')} (różnica: {model['param_diff']:.1f}B)")
        print(f"   📝 Kontekst: {model.get('context_length', 'N/A')}")
        print(f"   🏗️ Warstwy: {model.get('layers_count', 'N/A')}")
        print(f"   ⚙️ Kwantyzacja: {model.get('quantization', 'N/A')}")
    
    if not similar_models:
        print("❌ Nie znaleziono modeli o podobnych parametrach")
    
    return similar_models

def filter_similar_models_from_csv(csv_file_path, reference_model_name="gemma2:2b", export_results=False):
    """
    Filtruje modele z pliku CSV na podstawie podobieństwa do modelu referencyjnego
    
    Args:
        csv_file_path: Ścieżka do pliku CSV z metadanymi
        reference_model_name: Nazwa modelu referencyjnego
        export_results: Czy wyeksportować wyniki do pliku
        
    Returns:
        Lista przefiltrowanych modeli
    """
    try:
        import pandas as pd
        
        # Wczytaj CSV
        df = pd.read_csv(csv_file_path)
        print(f"📁 Wczytano {len(df)} modeli z pliku: {csv_file_path}")
        
        # Znajdź model referencyjny
        ref_model = df[df['name'] == reference_model_name]
        if ref_model.empty:
            print(f"❌ Nie znaleziono modelu referencyjnego: {reference_model_name}")
            print("Dostępne modele:")
            for name in df['name'].tolist():
                print(f"  - {name}")
            return []
        
        ref_row = ref_model.iloc[0]
        print(f"\n🎯 MODEL REFERENCYJNY: {reference_model_name}")
        print(f"   Parametry: {ref_row.get('parameter_size', 'N/A')}")
        print(f"   Rozmiar: {ref_row.get('size_gb', 'N/A')} GB")
        print(f"   Kontekst: {ref_row.get('context_length', 'N/A')}")
        print(f"   Warstwy: {ref_row.get('layers_count', 'N/A')}")
        print(f"   Kwantyzacja: {ref_row.get('quantization', 'N/A')}")
        
        # Parametry referencyjne
        ref_size_gb = ref_row.get('size_gb', 0)
        ref_context = ref_row.get('context_length', 0)
        ref_layers = ref_row.get('layers_count', 0)
        
        def extract_param_number(param_size):
            if pd.isna(param_size) or param_size == 'N/A':
                return 0
            import re
            match = re.search(r'(\d+\.?\d*)', str(param_size))
            return float(match.group(1)) if match else 0
        
        ref_param_number = extract_param_number(ref_row.get('parameter_size', '0'))
        
        # Filtrowanie
        similar_models = []
        for idx, row in df.iterrows():
            if row['name'] == reference_model_name:
                continue
            
            model_size_gb = row.get('size_gb', 0)
            model_context = row.get('context_length', 0) if pd.notna(row.get('context_length')) else 0
            model_layers = row.get('layers_count', 0) if pd.notna(row.get('layers_count')) else 0
            model_param_number = extract_param_number(row.get('parameter_size', '0'))
            
            # Kryteria podobieństwa
            size_similar = abs(model_size_gb - ref_size_gb) <= 0.5
            param_similar = abs(model_param_number - ref_param_number) <= 1.0
            context_similar = abs(model_context - ref_context) <= 50000 if ref_context > 0 else True
            layers_similar = abs(model_layers - ref_layers) <= 5 if ref_layers > 0 else True
            
            similarity_score = sum([size_similar, param_similar, context_similar, layers_similar])
            
            if similarity_score >= 2:
                model_dict = row.to_dict()
                model_dict['similarity_score'] = similarity_score
                model_dict['size_diff'] = abs(model_size_gb - ref_size_gb)
                model_dict['param_diff'] = abs(model_param_number - ref_param_number)
                similar_models.append(model_dict)
        
        # Sortowanie
        similar_models.sort(key=lambda x: (-x['similarity_score'], x['size_diff']))
        
        print(f"\n📋 ZNALEZIONO {len(similar_models)} PODOBNYCH MODELI:")
        print("-" * 80)
        
        for i, model in enumerate(similar_models, 1):
            print(f"\n{i}. {model.get('name', 'N/A')}")
            print(f"   📊 Wynik podobieństwa: {model['similarity_score']}/4")
            print(f"   📁 Rozmiar: {model.get('size_gb', 'N/A')} GB (różnica: {model['size_diff']:.2f} GB)")
            print(f"   🧠 Parametry: {model.get('parameter_size', 'N/A')} (różnica: {model['param_diff']:.1f}B)")
            print(f"   📝 Kontekst: {model.get('context_length', 'N/A')}")
            print(f"   🏗️ Warstwy: {model.get('layers_count', 'N/A')}")
            print(f"   ⚙️ Kwantyzacja: {model.get('quantization', 'N/A')}")
        
        # Eksport wyników
        if export_results and similar_models:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            # Eksport do CSV
            filtered_df = pd.DataFrame(similar_models)
            csv_filename = f"filtered_models_similar_to_{reference_model_name.replace(':', '_')}_{timestamp}.csv"
            csv_path = export_dir / csv_filename
            filtered_df.to_csv(csv_path, index=False)
            print(f"\n💾 Przefiltrowane wyniki wyeksportowane do: {csv_path}")
            
            # Eksport do JSON
            json_filename = f"filtered_models_similar_to_{reference_model_name.replace(':', '_')}_{timestamp}.json"
            json_path = export_dir / json_filename
            filtered_df.to_json(json_path, orient='records', indent=2)
            print(f"💾 Przefiltrowane wyniki wyeksportowane do: {json_path}")
        
        return similar_models
        
    except ImportError:
        print("❌ Brak modułu pandas. Zainstaluj: pip install pandas")
        return []
    except Exception as e:
        print(f"❌ Błąd podczas filtrowania z CSV: {e}")
        return []

def interactive_csv_filter():
    """Interaktywne filtrowanie modeli z pliku CSV"""
    print("\n📄 FILTROWANIE Z PLIKU CSV")
    print("Dostępne pliki CSV w folderze exports:")
    
    export_dir = Path("exports")
    if not export_dir.exists():
        print("❌ Folder exports nie istnieje")
        return
    
    csv_files = list(export_dir.glob("*.csv"))
    if not csv_files:
        print("❌ Brak plików CSV w folderze exports")
        return
    
    for i, csv_file in enumerate(csv_files, 1):
        print(f"{i}. {csv_file.name}")
    
    try:
        file_choice = int(input("\nWybierz numer pliku CSV: ").strip())
        if 1 <= file_choice <= len(csv_files):
            chosen_file = csv_files[file_choice - 1]
            
            # Wybór modelu referencyjnego
            print("\n1. Użyj gemma2:2b jako model referencyjny")
            print("2. Wybierz inny model z pliku")
            
            ref_choice = input("Wybierz opcję (1-2): ").strip()
            
            if ref_choice == "1":
                reference_model = "gemma2:2b"
            elif ref_choice == "2":
                # Wczytaj nazwy modeli z CSV
                try:
                    import pandas as pd
                    df = pd.read_csv(chosen_file)
                    print("\nDostępne modele w pliku:")
                    for i, name in enumerate(df['name'].tolist(), 1):
                        print(f"{i}. {name}")
                    
                    model_choice = int(input("\nWybierz numer modelu referencyjnego: ").strip())
                    if 1 <= model_choice <= len(df):
                        reference_model = df['name'].iloc[model_choice - 1]
                    else:
                        print("❌ Nieprawidłowy numer modelu")
                        return
                except ImportError:
                    print("❌ Brak modułu pandas")
                    return
                except Exception as e:
                    print(f"❌ Błąd: {e}")
                    return
            else:
                print("❌ Nieprawidłowy wybór")
                return
            
            # Pytanie o eksport
            export_choice = input("\nCzy wyeksportować wyniki? (t/n): ").strip().lower()
            export_results = export_choice in ['t', 'tak', 'y', 'yes']
            
            # Uruchom filtrowanie
            filter_similar_models_from_csv(chosen_file, reference_model, export_results)
            
        else:
            print("❌ Nieprawidłowy numer pliku")
    except ValueError:
        print("❌ Wprowadź prawidłowy numer")

def display_enhanced_metadata_with_options():
    """Wyświetla rozszerzone metadane z opcjami cache, eksportu i porównania"""
    print("\n📊 OPCJE METADANYCH:")
    print("1. Użyj cache (jeśli dostępny)")
    print("2. Odśwież dane z API")
    print("3. Porównaj modele")
    print("4. Eksportuj dane")
    print("5. Filtruj modele podobne do gemma2:2b")
    print("6. Filtruj modele podobne do własnego modelu")
    print("7. Filtruj modele z pliku CSV")
    
    choice = input("\nWybierz opcję (1-7): ").strip()
    
    if choice == "1":
        enhanced_data = get_enhanced_model_metadata_cached()
        display_enhanced_metadata_from_data(enhanced_data)
    elif choice == "2":
        enhanced_data = get_enhanced_model_metadata_cached(force_refresh=True)
        display_enhanced_metadata_from_data(enhanced_data)
    elif choice == "3":
        enhanced_data = get_enhanced_model_metadata_cached()
        if enhanced_data:
            compare_models(enhanced_data)
        else:
            print("❌ Brak danych do porównania")
    elif choice == "4":
        enhanced_data = get_enhanced_model_metadata_cached()
        if enhanced_data:
            print("\nFormaty eksportu:")
            print("1. JSON")
            print("2. CSV") 
            print("3. TXT")
            
            format_choice = input("Wybierz format (1-3): ").strip()
            format_map = {"1": "json", "2": "csv", "3": "txt"}
            
            if format_choice in format_map:
                export_models_metadata(enhanced_data, format_map[format_choice])
            else:
                print("❌ Nieprawidłowy wybór formatu")
        else:
            print("❌ Brak danych do eksportu")
    elif choice == "5":
        enhanced_data = get_enhanced_model_metadata_cached()
        if enhanced_data:
            filter_similar_models(enhanced_data, "gemma2:2b")
        else:
            print("❌ Brak danych do filtrowania")
    elif choice == "6":
        enhanced_data = get_enhanced_model_metadata_cached()
        if enhanced_data:
            print("\nDostępne modele:")
            for i, model in enumerate(enhanced_data, 1):
                print(f"{i}. {model.get('name', 'N/A')}")
            
            try:
                model_choice = int(input("\nWybierz numer modelu referencyjnego: ").strip())
                if 1 <= model_choice <= len(enhanced_data):
                    ref_model_name = enhanced_data[model_choice - 1].get('name')
                    filter_similar_models(enhanced_data, ref_model_name)
                else:
                    print("❌ Nieprawidłowy numer modelu")
            except ValueError:
                print("❌ Wprowadź prawidłowy numer")
        else:
            print("❌ Brak danych do filtrowania")
    elif choice == "7":
        interactive_csv_filter()
    else:
        print("❌ Nieprawidłowy wybór")

def get_enhanced_model_metadata_cached(force_refresh=False):
    """Wersja cached dla enhanced metadata"""
    detailed_models = get_all_models_with_detailed_metadata_cached(force_refresh)
    
    if not detailed_models:
        return []
    
    enhanced_models = []
    
    for model_data in detailed_models:
        # Podstawowe informacje
        enhanced_info = {
            'name': model_data.get('name', 'N/A'),
            'size_bytes': model_data.get('size', 0),
            'size_gb': round(model_data.get('size', 0) / (1024**3), 2),
            'modified_at': model_data.get('modified_at', 'N/A'),
            'digest': model_data.get('digest', 'N/A')[:12],  # Skrócona wersja
        }
        
        # Szczegóły z /api/tags
        details = model_data.get('details', {})
        enhanced_info.update({
            'family': details.get('family', 'N/A'),
            'parameter_size': details.get('parameter_size', 'N/A'),
            'quantization': details.get('quantization_level', 'N/A'),
            'format': details.get('format', 'N/A')
        })
        
        # Zaawansowane informacje z /api/show
        model_info = model_data.get('model_info', {})
        if model_info:
            # Architektura modelu
            enhanced_info.update({
                'architecture': model_info.get('general.architecture', 'N/A'),
                'context_length': model_info.get(f"{enhanced_info['family']}.context_length", 'N/A'),
                'embedding_length': model_info.get(f"{enhanced_info['family']}.embedding_length", 'N/A'),
                'layers_count': model_info.get(f"{enhanced_info['family']}.block_count", 'N/A'),
                'attention_heads': model_info.get(f"{enhanced_info['family']}.attention.head_count", 'N/A'),
                'parameter_count': model_info.get('general.parameter_count', 'N/A')
            })
            
            # Tokenizer info
            enhanced_info.update({
                'tokenizer_type': model_info.get('tokenizer.ggml.model', 'N/A'),
                'vocab_size': len(model_info.get('tokenizer.ggml.tokens', [])) if model_info.get('tokenizer.ggml.tokens') else 'N/A',
                'bos_token_id': model_info.get('tokenizer.ggml.bos_token_id', 'N/A'),
                'eos_token_id': model_info.get('tokenizer.ggml.eos_token_id', 'N/A')
            })
        
        # Capabilities
        enhanced_info['capabilities'] = model_data.get('capabilities', [])
        
        # Tensor statistics
        tensors = model_data.get('tensors', [])
        if tensors:
            enhanced_info.update({
                'tensor_count': len(tensors),
                'weight_types': list(set(t.get('type', 'Unknown') for t in tensors)),
                'total_parameters': sum(
                    reduce(lambda x, y: x * y, t.get('shape', [1]), 1) 
                    for t in tensors
                ) if tensors else 'N/A'
            })
        
        enhanced_models.append(enhanced_info)
    
    return enhanced_models

def display_enhanced_metadata_from_data(enhanced_data):
    """Wyświetla enhanced metadata z przekazanych danych"""
    if not enhanced_data:
        print("Brak danych o modelach.")
        return
    
    print("\n" + "="*100)
    print("ROZSZERZONE METADANE MODELI OLLAMA")
    print("="*100)
    
    for model in enhanced_data:
        print(f"\n🤖 MODEL: {model['name']}")
        print("-" * 80)
        
        # Podstawowe informacje
        print(f"📊 PODSTAWOWE:")
        print(f"   Rozmiar: {model['size_gb']} GB ({model['size_bytes']:,} bajtów)")
        print(f"   Rodzina: {model['family']}")
        print(f"   Parametry: {model['parameter_size']}")
        print(f"   Kwantyzacja: {model['quantization']}")
        print(f"   Format: {model['format']}")
        print(f"   Zmodyfikowano: {model['modified_at']}")
        
        # Architektura
        if model.get('architecture') != 'N/A':
            print(f"\n🏗️ ARCHITEKTURA:")
            print(f"   Typ: {model['architecture']}")
            print(f"   Warstwy: {model['layers_count']}")
            print(f"   Heads attention: {model['attention_heads']}")
            print(f"   Długość kontekstu: {model['context_length']}")
            print(f"   Embedding: {model['embedding_length']}")
            if model.get('parameter_count') != 'N/A':
                print(f"   Parametry (dokładne): {model['parameter_count']:,}")
        
        # Tokenizer
        if model.get('tokenizer_type') != 'N/A':
            print(f"\n🔤 TOKENIZER:")
            print(f"   Typ: {model['tokenizer_type']}")
            print(f"   BOS token ID: {model['bos_token_id']}")
            print(f"   EOS token ID: {model['eos_token_id']}")
        
        # Tensory
        if model.get('tensor_count'):
            print(f"\n⚙️ TENSORY:")
            print(f"   Liczba tensorów: {model['tensor_count']}")
            print(f"   Typy wag: {', '.join(model['weight_types'])}")
        
        # Możliwości
        if model.get('capabilities'):
            print(f"\n✨ MOŻLIWOŚCI: {', '.join(model['capabilities'])}")

# --- Kod główny ---
if __name__ == "__main__":
    print("=== TESTER MODELI LLM ===")
    print("1. Kompleksowy test wszystkich modeli (10 różnych zadań, z oceną AI sędziego Gemini)")
    print("2. Szybki test (5 podstawowych zadań, z oceną AI sędziego Gemini)")
    print("3. Własne pytanie do wszystkich modeli (bez oceny AI sędziego)")
    print("4. Wyświetl szczegółowe metadane wszystkich modeli Ollama")
    print("5. Wyświetl rozszerzone metadane wszystkich modeli Ollama")
    
    choice = input("\nWybierz opcję (1, 2, 3, 4 lub 5): ").strip()
    
    if choice == "1":
        run_test_with_judge(test_type="comprehensive")
    elif choice == "2":
        run_test_with_judge(test_type="quick")
    elif choice == "3":
        prompt = input("Wpisz swoje pytanie: ").strip()
        if prompt:
            ask_all_models(prompt)
        else:
            print("Nie podano pytania!")
    elif choice == "4":
        detailed_metadata = get_all_models_with_detailed_metadata()
        if detailed_metadata:
            print("\n--- SZCZEGÓŁOWE METADANE MODELI OLLAMA ---")
            for model_data in detailed_metadata:
                print(f"\nModel: {model_data.get('name', 'N/A')}")
                print(f"  Digest: {model_data.get('digest', 'N/A')}")
                print(f"  Rozmiar: {model_data.get('size', 'N/A')} bajtów")
                print(f"  Zmodyfikowano: {model_data.get('modified_at', 'N/A')}")
                
                details = model_data.get('details', {})
                print(f"  Rodzina: {details.get('family', 'N/A')}")
                print(f"  Rozmiar parametrów: {details.get('parameter_size', 'N/A')}")
                print(f"  Poziom kwantyzacji: {details.get('quantization_level', 'N/A')}")
                print(f"  Typ modelu: {details.get('model_type', 'N/A')}")
                print(f"  Format: {details.get('format', 'N/A')}")
                
                # Możesz dodać więcej pól z 'details' lub innych kluczy, jeśli są interesujące
                # np. print(f"  Modelfile: {model_data.get('modelfile', 'N/A')[:100]}...") # Skrócona wersja
        else:
            print("Nie udało się pobrać szczegółowych metadanych modeli Ollama.")
    elif choice == "5":
        display_enhanced_metadata_with_options()
    else:
        print("Nieprawidłowy wybór! Uruchamiam szybki test...")
        run_test_with_judge(test_type="quick")
