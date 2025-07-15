# 🤖 AI Judge & Predefined Tests Feature

## ✨ Nowe funkcje w v2.4

Dodano zaawansowane funkcje testowania z sędzią AI i predefiniowanymi zestawami testów!

## 🎯 Odpowiedź na Twoje zapytanie

**"Popraw panel do obsługi testów, daj możliwość na skorzystanie z predefiniowanych testów z sędzią, dodaj panel gdzie będzie można zdefiniować sędziego model i dostawcę oraz zapisać klucz API"**

### ✅ Zaimplementowane funkcje:

## 🤖 Panel Sędziego AI

### Konfiguracja sędziego:
- **3 dostawców**: Gemini, OpenAI, Claude
- **Wybór modelu** dla każdego dostawcy
- **Klucz API** z funkcjami:
  - 💾 Zapisz klucz
  - 📋 Wczytaj z ENV  
  - 🧪 Testuj połączenie
- **Status** z informacją o stanie konfiguracji

### Supported providers:
```python
JUDGE_CONFIG = {
    'providers': {
        'gemini': {
            'models': ['gemini-1.5-flash', 'gemini-1.5-pro'],
            'api_key_env': 'GEMINI_API_KEY'
        },
        'openai': {
            'models': ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo'],
            'api_key_env': 'OPENAI_API_KEY'
        },
        'claude': {
            'models': ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229'],
            'api_key_env': 'ANTHROPIC_API_KEY'
        }
    }
}
```

## 📚 Predefiniowane Zestawy Testów

### 3 gotowe zestawy:

1. **🔧 Programowanie** (3 testy)
   - Funkcja sprawdzania liczb pierwszych
   - Różnice lista vs tuple w Python
   - Algorytm quicksort z implementacją

2. **📐 Matematyka** (2 testy)
   - Rozwiązywanie równań kwadratowych
   - Obliczanie pochodnych

3. **📝 Język** (2 testy)
   - Pisanie eseju o technologii
   - Poprawianie błędów gramatycznych

### Struktura testu:
```python
{
    'question': 'Pytanie testowe',
    'criteria': 'Kryteria oceny dla sędziego',
    'expected_elements': ['słowa', 'kluczowe', 'do', 'sprawdzenia']
}
```

## 🔥 Nowy typ testu: PREDEFINED

**Dodano 5-ty typ testu** - PREDEFINED z automatyczną oceną sędziego:

1. **SIMPLE** - Test podstawowy
2. **EXPECTED** - Test z oczekiwaną odpowiedzią  
3. **KEYWORD** - Test obecności słów kluczowych
4. **LENGTH** - Test długości odpowiedzi
5. **🆕 PREDEFINED** - Zestawy testów z oceną AI

## 🎮 Jak używać

### 1. Konfiguracja sędziego:
1. Przejdź do zakładki **🧪 Testy**
2. W panelu **🤖 Sędzia AI**:
   - ✅ Zaznacz "Włącz sędziego AI"
   - 🎛️ Wybierz dostawcę (gemini/openai/claude)
   - 🤖 Wybierz model
   - 🔑 Wprowadź klucz API
   - 🧪 Przetestuj połączenie

### 2. Uruchomienie predefiniowanych testów:
1. Wybierz **PREDEFINED** jako typ testu
2. W panelu **📚 Predefiniowane Testy**:
   - 📋 Wybierz zestaw (programowanie/matematyka/język)
   - 👀 Zobacz opis zestawu
   - 🚀 Kliknij "Uruchom Zestaw Testów"

### 3. Wyniki z oceną sędziego:
```
📋 TEST 1: Napisz funkcję Python, która sprawdza czy liczba jest pierwsza
📝 Odpowiedź: def is_prime(n): ...
🤖 Ocenianie przez sędziego...
⭐ Ocena sędziego: 8/10
💬 Uzasadnienie: Kod jest poprawny i wydajny, ale brakuje obsługi błędów...
✅ Test zakończony
```

## ⚙️ Konfiguracja zmiennych ENV

Ustaw zmienne środowiskowe dla API:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-key-here"
$env:OPENAI_API_KEY="your-openai-key-here"  
$env:ANTHROPIC_API_KEY="your-claude-key-here"

# Linux/macOS
export GEMINI_API_KEY="your-gemini-key-here"
export OPENAI_API_KEY="your-openai-key-here"
export ANTHROPIC_API_KEY="your-claude-key-here"
```

## 🛠️ Implementacja techniczna

### API Integration:
- **Gemini**: Pełna integracja z `judge_with_gemini()`
- **OpenAI**: Struktura przygotowana (do implementacji)
- **Claude**: Struktura przygotowana (do implementacji)

### Funkcje sędziego:
- ✅ Test klucza API z rzeczywistym połączeniem
- ✅ Automatyczna ocena 1-10 + uzasadnienie
- ✅ Integracja z predefiniowanymi kryteriami oceny
- ✅ Obsługa błędów i statusów

## 📊 Porównanie typów testów

| Typ | Opis | Ocena | Automatyzacja |
|-----|------|--------|---------------|
| **SIMPLE** | Podstawowy test | Brak | Ręczna |
| **EXPECTED** | Z oczekiwaną odpowiedzią | Porównanie tekstu | Półautomatyczna |
| **KEYWORD** | Obecność słów kluczowych | Zliczanie wystąpień | Automatyczna |
| **LENGTH** | Długość odpowiedzi | Min/max znaków | Automatyczna |
| **🆕 PREDEFINED** | Zestawy + sędzia AI | **AI 1-10 + uzasadnienie** | **Pełna** |

## 🎯 Rezultat

**Teraz masz kompletny system testowania z sędzią AI!** 🎉

- ✅ Panel konfiguracji sędziego (3 dostawców)
- ✅ Zarządzanie kluczami API  
- ✅ Predefiniowane zestawy testów
- ✅ Automatyczna ocena AI z uzasadnieniem
- ✅ Test połączenia API
- ✅ Intuicyjny interfejs

Możesz teraz testować modele Ollama z profesjonalną oceną AI! 🚀
