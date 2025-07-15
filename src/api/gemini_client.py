"""
Gemini API communication module for AI judge functionality.
"""

import requests
import re
from typing import Tuple

from ..config import GEMINI_API_URL, GEMINI_JUDGE_MODEL_NAME, GEMINI_JUDGE_TIMEOUT


def judge_with_gemini(
    model_response: str, 
    original_prompt: str, 
    gemini_api_key: str, 
    judge_model_name: str = GEMINI_JUDGE_MODEL_NAME
) -> Tuple[int, str]:
    """
    Wykorzystuje zewnętrzny model LLM (Gemini) jako sędziego do oceny jakości odpowiedzi.
    
    Args:
        model_response (str): Odpowiedź modelu do oceny
        original_prompt (str): Oryginalne pytanie
        gemini_api_key (str): Klucz API Gemini
        judge_model_name (str): Nazwa modelu sędziego
        
    Returns:
        Tuple[int, str]: Ocena (1-5) i uzasadnienie
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
            "temperature": 0.2,  # Niższa temperatura dla bardziej deterministycznych ocen
            "maxOutputTokens": 2000  # Zwiększony limit dla stabilnych odpowiedzi
        }
    }

    try:
        headers = {'Content-Type': 'application/json'}
        judge_response = requests.post(api_url, headers=headers, json=payload, timeout=GEMINI_JUDGE_TIMEOUT)
        judge_response.raise_for_status()  # Sprawdź błędy HTTP
        
        result_data = judge_response.json()
        
        # Debug: wypisz surową odpowiedź
        print(f"\n[DEBUG] Status kod: {judge_response.status_code}")
        print(f"[DEBUG] Surowa odpowiedź: {result_data}")
        
        # Parsowanie odpowiedzi Gemini
        judge_full_response = _extract_response_text(result_data)
        
        # Debug: wypisz odpowiedź sędziego (tylko pierwsze 200 znaków)
        print(f"\n[DEBUG] Odpowiedź sędziego: {judge_full_response[:200]}...")
        
        # Parsowanie oceny i uzasadnienia z tekstu odpowiedzi sędziego
        rating, justification = _parse_judge_response(judge_full_response)
        
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


def _extract_response_text(result_data: dict) -> str:
    """
    Wyciąga tekst odpowiedzi z różnych formatów odpowiedzi Gemini API.
    
    Args:
        result_data (dict): Odpowiedź z API Gemini
        
    Returns:
        str: Wyciągnięty tekst odpowiedzi
    """
    if not result_data or 'candidates' not in result_data or len(result_data['candidates']) == 0:
        return "Nieprawidłowa struktura odpowiedzi od sędziego."
    
    candidate = result_data['candidates'][0]
    
    # Sprawdź standardową strukturę z content.parts
    if 'content' in candidate:
        content = candidate['content']
        
        # Standardowa struktura z parts
        if 'parts' in content and len(content['parts']) > 0:
            # Możliwe, że parts jest listą z różnymi typami
            for part in content['parts']:
                if 'text' in part:
                    return part['text']
        # Alternatywna struktura
        elif 'text' in content:
            return content['text']
        # Jeśli role model bez tekstu, może być problem z API
        elif content.get('role') == 'model':
            if 'thoughtsTokenCount' in result_data.get('usageMetadata', {}):
                return "Model generował odpowiedź ale token limit został przekroczony."
            else:
                return "Model nie wygenerował tekstu odpowiedzi."
    
    # Sprawdź starszą strukturę z text bezpośrednio w candidate
    elif 'text' in candidate:
        return candidate['text']
    
    return "Brak treści odpowiedzi od sędziego."


def _parse_judge_response(judge_full_response: str) -> Tuple[int, str]:
    """
    Parsuje odpowiedź sędziego aby wyciągnąć ocenę i uzasadnienie.
    
    Args:
        judge_full_response (str): Pełna odpowiedź sędziego
        
    Returns:
        Tuple[int, str]: Ocena (0-5) i uzasadnienie
    """
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
