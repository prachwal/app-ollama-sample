import requests
import json
import time
import os
from datetime import datetime
import signal

def print_progress_bar(current, total, prefix='Progress:', suffix='Complete', length=50):
    """Wyświetla pasek postępu"""
    percent = "{0:.1f}".format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
    if current == total:
        print()  # Nowa linia po zakończeniu

# --- Konfiguracja (można przenieść do osobnego pliku config.py/json) ---
OLLAMA_API_URL = "http://localhost:11434"
DEFAULT_TIMEOUT_PER_MODEL = 180 # Domyślny timeout dla pojedynczej odpowiedzi modelu testowanego
DEFAULT_SLEEP_BETWEEN_MODELS = 2 # Domyślna pauza między modelami testowanymi

# Konfiguracja dla modelu sędziego (Gemini)
# Upewnij się, że masz klucz API do Gemini. Nie umieszczaj go tutaj na stałe!
# Zostanie poproszony o niego w trakcie działania skryptu.
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_JUDGE_MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17" # Nowy model - lite preview
GEMINI_JUDGE_TIMEOUT = 60 # Timeout dla odpowiedzi modelu sędziego
# --- Koniec konfiguracji ---

def get_available_models():
    """Pobiera listę dostępnych modeli z Ollama"""
    url = f"{OLLAMA_API_URL}/api/tags"
    try:
        response = requests.get(url)
        response.raise_for_status() # Wyrzuć wyjątek dla statusów 4xx/5xx
        data = response.json()
        return [model['name'] for model in data.get('models', [])]
    except requests.exceptions.ConnectionError:
        print(f"Błąd połączenia z Ollama na {OLLAMA_API_URL}. Upewnij się, że Ollama jest uruchomiona.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Błąd pobierania modeli: {e}")
        return []

def ask_ollama(model, prompt, test_name="", output_file=None, timeout=None, **model_options):
    """
    Zadaje pytanie do modelu Ollama z pełną obsługą błędów i logowaniem.
    
    Args:
        model (str): Nazwa modelu do testowania
        prompt (str): Tekst pytania
        test_name (str): Nazwa testu dla logowania
        output_file (str): Ścieżka do pliku wyników
        timeout (int): Timeout w sekundach
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
            "maxOutputTokens": 2000 # Zwiększony limit dla stabilnych odpowiedzi
        }
    }

    try:
        headers = {'Content-Type': 'application/json'}
        judge_response = requests.post(api_url, headers=headers, json=payload, timeout=GEMINI_JUDGE_TIMEOUT)
        judge_response.raise_for_status() # Sprawdź błędy HTTP
        
        result_data = judge_response.json()
        
        # Debug: wypisz surową odpowiedź
        print(f"\n[DEBUG] Status kod: {judge_response.status_code}")
        print(f"[DEBUG] Surowa odpowiedź: {result_data}")
        
        # Parsowanie odpowiedzi Gemini
        if result_data and 'candidates' in result_data and len(result_data['candidates']) > 0:
            if 'content' in result_data['candidates'][0] and 'parts' in result_data['candidates'][0]['content'] and len(result_data['candidates'][0]['content']['parts']) > 0:
                judge_full_response = result_data['candidates'][0]['content']['parts'][0]['text']
            else:
                judge_full_response = "Brak treści odpowiedzi od sędziego."
        else:
            judge_full_response = "Nieprawidłowa struktura odpowiedzi od sędziego."
        
        # Debug: wypisz odpowiedź sędziego (tylko pierwsze 200 znaków)
        print(f"\n[DEBUG] Odpowiedź sędziego: {judge_full_response[:200]}...")
        
        # Parsowanie oceny i uzasadnienia z tekstu odpowiedzi sędziego
        rating = 0
        justification = "Brak uzasadnienia."
        
        # Próbuj znaleźć ocenę w różnych formatach
        lines = judge_full_response.split('\n')
        for line in lines:
            line = line.strip()
            # Szukaj wzorców: "OCENA: X", "Ocena: X", "Rating: X", "Score: X"
            if any(keyword in line.upper() for keyword in ["OCENA:", "RATING:", "SCORE:"]):
                try:
                    # Wyciągnij liczbę z linii
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        potential_rating = int(numbers[0])
                        if 1 <= potential_rating <= 5:
                            rating = potential_rating
                except (ValueError, IndexError):
                    continue
            elif any(keyword in line.upper() for keyword in ["UZASADNIENIE:", "JUSTIFICATION:", "EXPLANATION:"]):
                justification = line.split(":", 1)[1].strip() if ":" in line else line
        
        # Jeśli nie znaleziono oceny w standardowy sposób, spróbuj znaleźć liczbę w całym tekście
        if rating == 0:
            import re
            # Szukaj wzorców jak "5/5", "4 z 5", "ocena 3"
            patterns = [
                r'(\d)/5',
                r'(\d)\s*z\s*5',
                r'ocena\s*(\d)',
                r'rating\s*(\d)',
                r'score\s*(\d)'
            ]
            for pattern in patterns:
                matches = re.findall(pattern, judge_full_response.lower())
                if matches:
                    try:
                        potential_rating = int(matches[0])
                        if 1 <= potential_rating <= 5:
                            rating = potential_rating
                            break
                    except ValueError:
                        continue
                
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
            "name": "Logiczne rozumowanie",
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
        },
        {
            "name": "Kodowanie wielojęzyczne",
            "prompt": "Napisz funkcję 'Hello World' w trzech językach: Python, JavaScript i Java. Dodaj komentarze wyjaśniające różnice.",
            "options": {"temperature": 0.2, "num_predict": 500}
        },
        {
            "name": "Rozumowanie matematyczne",
            "prompt": "Jeśli pociąg jedzie z prędkością 80 km/h przez 2.5 godziny, jaką pokonał odległość? Wyjaśnij krok po kroku.",
            "options": {"temperature": 0.1, "num_predict": 200}
        },
        {
            "name": "Analiza etyczna AI",
            "prompt": "Jakie są główne wyzwania etyczne związane z rozwojem sztucznej inteligencji? Wymień 3 najważniejsze i krótko je opisz.",
            "options": {"temperature": 0.6, "num_predict": 400}
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
        },
        {
            "name": "Kreatywność",
            "prompt": "Wymyśl krótki slogan reklamowy dla firmy produkującej ekologiczne butelki na wodę.",
            "options": {"temperature": 0.8, "num_predict": 100}
        }
    ]

def ask_all_models(prompt):
    """Zadaje to samo pytanie wszystkim dostępnym modelom (funkcja kompatybilna wstecz)"""
    models = get_available_models()
    
    if not models:
        print("Nie znaleziono dostępnych modeli.")
        return
    
    print(f"Znaleziono {len(models)} modeli: {', '.join(models)}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"single_test_{timestamp}.txt"
    
    for model in models:
        # Tutaj nie ma oceny sędziego, bo to pojedyncze pytanie
        ask_ollama(model, prompt, "Pojedyncze pytanie", output_file)
        time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)


def run_test_with_judge(test_type="comprehensive"):
    """Uruchamia test wszystkich modeli z oceną AI sędziego."""
    models = get_available_models()
    
    if not models:
        print("Nie znaleziono dostępnych modeli.")
        return

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
    total_tests = len(test_prompts) * len(models)
    current_test = 0
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n{'#'*60}")
        print(f"TEST {i}/{len(test_prompts)}: {test['name']}")
        print(f"{'#'*60}")
        
        for j, model in enumerate(models, 1):
            current_test += 1
            print_progress_bar(current_test, total_tests, 
                             prefix=f'Model {j}/{len(models)} ({model}):', 
                             suffix=f'({current_test}/{total_tests})')
            
            # Użyj timeoutu z opcji promptu, lub domyślnego
            timeout_for_task = test.get('options', {}).get('timeout', DEFAULT_TIMEOUT_PER_MODEL)
            result = ask_ollama(model, test['prompt'], test['name'], output_file, timeout=timeout_for_task, **test.get('options', {}))
            
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
    
    summary += "🏆 RANKING SZYBKOŚCI (pierwszy token - niżej = lepiej):\n"
    summary += "-" * 60 + "\n"
    
    model_speed = {}
    for model in models:
        model_results = [r for r in results if r['model'] == model]
        if model_results:
            model_speed[model] = sum(r['first_token_time'] for r in model_results) / len(model_results)
    
    sorted_models_speed = sorted(model_speed.items(), key=lambda x: x[1])
    for i, (model, speed) in enumerate(sorted_models_speed, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        summary += f"{medal} {i}. {model}: {speed:.2f}s\n"

    summary += f"\n🎖️ RANKING JAKOŚCI (ocena sędziego AI - wyżej = lepiej):\n"
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

if __name__ == "__main__":
    print("=== TESTER MODELI LLM ===")
    print("1. Kompleksowy test wszystkich modeli (10 różnych zadań, z oceną AI sędziego Gemini)")
    print("2. Szybki test (5 podstawowych zadań, z oceną AI sędziego Gemini)")
    print("3. Własne pytanie do wszystkich modeli (bez oceny AI sędziego)")
    
    choice = input("\nWybierz opcję (1, 2 lub 3): ").strip()
    
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
    else:
        print("Nieprawidłowy wybór! Uruchamiam szybki test...")
        run_test_with_judge(test_type="quick")
