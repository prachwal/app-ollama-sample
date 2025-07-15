import requests
import json
import os

# WAŻNE: Nie umieszczaj klucza API bezpośrednio w kodzie produkcyjnym!
# Najlepiej pobierać go ze zmiennych środowiskowych lub bezpiecznego magazynu.
# Na potrzeby tego przykładu użyjemy zmiennej, ale pamiętaj o bezpieczeństwie.
api_key = os.getenv('GEMINI_API_KEY', 'TWOJ_KLUCZ_API_GEMINI_TUTAJ') # Zastąp 'TWOJ_KLUCZ_API_GEMINI_TUTAJ' swoim prawdziwym kluczem

url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite-preview-06-17:generateContent?key={api_key}'

# Przykład bardziej rozbudowanego promptu dla sędziego, zgodnego z logiką testera
judge_prompt_example = '''Oceń jakość poniższej odpowiedzi na oryginalne pytanie.
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
Przedstaw się krótko - kim jesteś i jakie masz możliwości?

---
ODPOWIEDŹ DO OCENY:
Cześć, jestem AI.
'''

payload = {
    'contents': [{'role': 'user', 'parts': [{'text': judge_prompt_example}]}],
    'generationConfig': {'temperature': 0.2, 'maxOutputTokens': 2000}
}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status() # Sprawdza, czy status kodu odpowiedzi to błąd (4xx lub 5xx)
    
    result_data = response.json()
    
    print('Status:', response.status_code)
    print('Pełna odpowiedź JSON:')
    print(json.dumps(result_data, indent=2, ensure_ascii=False))
    print('---')
    
    # Bezpieczne parsowanie odpowiedzi
    if result_data and 'candidates' in result_data and len(result_data['candidates']) > 0:
        if 'content' in result_data['candidates'][0] and 'parts' in result_data['candidates'][0]['content'] and len(result_data['candidates'][0]['content']['parts']) > 0:
            gemini_response_text = result_data['candidates'][0]['content']['parts'][0]['text']
            print('Odpowiedź Gemini:', gemini_response_text)
        else:
            print('Błąd: Brak treści w odpowiedzi Gemini.')
    else:
        print('Błąd: Nieprawidłowa struktura odpowiedzi Gemini.')

except requests.exceptions.RequestException as e:
    print(f'Błąd zapytania: {e}')
except json.JSONDecodeError:
    print('Błąd: Odpowiedź nie jest poprawnym JSONem.')
except Exception as e:
    print(f'Wystąpił nieoczekiwany błąd: {e}')
