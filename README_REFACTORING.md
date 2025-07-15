# Ollama LLM Testing Suite v2.2

Ujednolicony framework do testowania modeli LLM z oceną AI sędziego i wielojęzyczną obsługą.

## 🏗️ Najnowsza Architektura Modułowa (v2.2)

Projekt przeszedł przez kompletną refaktoryzację, wprowadzając:
- ✅ **Uspójniony interfejs GUI** - usunięto duplikaty przycisków
- ✅ **Wielojęzyczną obsługę** - Polski/English w GUI i CLI  
- ✅ **Modułową architekturę** - eliminacja duplikacji kodu
- ✅ **Automatyzację czyszczenia** - PowerShell i Batch scripts
- ✅ **Comprehensive .gitignore** - dla projektów Python

### 📁 Struktura Projektu

```
src/
├── __init__.py                 # Główny moduł pakietu
├── config.py                   # Centralna konfiguracja
├── api/                        # Moduły komunikacji API
│   ├── __init__.py
│   ├── ollama_client.py        # Klient Ollama API
│   └── gemini_client.py        # Klient Gemini API (sędzia AI)
├── utils/                      # Funkcje pomocnicze
│   ├── __init__.py
│   ├── helpers.py              # Ogólne funkcje pomocnicze
│   ├── test_prompts.py         # Zestawy testów
│   └── analysis.py             # Analiza i podsumowania wyników
└── testers/                    # Implementacje testerów
    ├── __init__.py
    └── base_tester.py          # Bazowa klasa dla testerów
```

## 🔄 Migracja z Poprzedniej Wersji

### Przed refaktoryzacją:
- ❌ **8 plików** z duplikowanymi funkcjami
- ❌ **Powtarzany kod** w każdym skrypcie
- ❌ **Różne implementacje** tych samych funkcji
- ❌ **Nieopisowe nazwy** (test*.py)

### Po refaktoryzacji:
- ✅ **Modułowa architektura** z wspólnymi komponentami
- ✅ **Centralna konfiguracja** w jednym miejscu
- ✅ **Ujednolicone API** dla wszystkich funkcji
- ✅ **Opisowe nazwy** plików i funkcji
- ✅ **Łatwa rozszerzalność** nowych testerów

## 🚀 Nowe Pliki

### Główne Aplikacje

| Plik | Opis | Status |
|------|------|--------|
| `ollama_unified_benchmark.py` | **NOWY** - Główny tester używający nowej architektury | ✅ Gotowy |
| `ollama_basic_chat_v2.py` | **NOWY** - Zmigrowany chat z nową architekturą | ✅ Gotowy |

### Istniejące Pliki (Przemianowane)

| Stara nazwa | Nowa nazwa | Opis |
|-------------|------------|------|
| `connect.py` | `ollama_basic_chat.py` | Podstawowy chat z modelami |
| `test2.py` | `ollama_comprehensive_benchmark.py` | Kompleksowe testy z sędzią AI |
| `test3.py` | `gemini_api_test.py` | Testy API Gemini |
| `test4.py` | `ollama_advanced_benchmark_with_cache.py` | Zaawansowane testy z cache |
| `test5.py` | `ollama_benchmark_with_progress.py` | Testy z paskiem postępu |
| `test6.py` | `ollama_tools_function_calling_tester.py` | Tester wywołań funkcji (naprawiony sędzia AI) |
| `debug_metadata.py` | `ollama_metadata_debugger.py` | Debug metadanych modeli |
| `filter_models.py` | `ollama_models_filter_analyzer.py` | Analiza i filtrowanie modeli |

## 💡 Korzyści z Refaktoryzacji

### 1. **Eliminacja Duplikacji Kodu**
- Funkcje `get_available_models()`, `ask_ollama()`, `judge_with_gemini()` są teraz w jednym miejscu
- Wszystkie skrypty korzystają z tych samych, przetestowanych implementacji

### 2. **Centralna Konfiguracja**
```python
# src/config.py
OLLAMA_API_URL = "http://localhost:11434"
GEMINI_JUDGE_MODEL_NAME = "gemini-1.5-flash"  # Jedna wersja dla wszystkich
DEFAULT_TIMEOUT_PER_MODEL = 180
```

### 3. **Lepsze Parsowanie Odpowiedzi Gemini**
```python
# src/api/gemini_client.py - ujednolicone dla wszystkich
def _extract_response_text(result_data: dict) -> str:
    """Obsługuje różne formaty odpowiedzi Gemini API"""
    # Inteligentne parsowanie z fallbackami
```

### 4. **Spójna Obsługa Błędów**
- Ujednolicone komunikaty błędów
- Consistent timeout handling
- Standardowe logowanie

### 5. **Łatwa Rozszerzalność**
```python
from src.testers import BaseTester

class MyCustomTester(BaseTester):
    def run_my_test(self):
        # Twoja implementacja
        pass
```

## 🔧 Użycie Nowej Architektury

### Podstawowe użycie:
```bash
python ollama_unified_benchmark.py      # Nowy, ujednolicony tester
python ollama_basic_chat_v2.py          # Zmigrowany chat
```

### Import w kodzie:
```python
from src.api import get_available_models, ask_ollama, judge_with_gemini
from src.utils import get_comprehensive_test_prompts, generate_summary
from src.testers import BaseTester
```

## 🔍 Rozwiązane Problemy

### 1. **Problem Sędziego AI w test6.py** ✅ ROZWIĄZANE
- **Błąd**: Gemini 2.5 Flash miał inne formaty odpowiedzi
- **Rozwiązanie**: Przejście na stabilny `gemini-1.5-flash` + ulepszony parsing

### 2. **Duplikacja Judge Functions** ✅ ROZWIĄZANE
- **Błąd**: 6 różnych implementacji funkcji sędziego
- **Rozwiązanie**: Jedna implementacja w `src/api/gemini_client.py`

### 3. **Niekonsystentne Timeouty** ✅ ROZWIĄZANE
- **Błąd**: Różne wartości timeout w każdym pliku
- **Rozwiązanie**: Centralna konfiguracja w `src/config.py`

### 4. **Różne Wersje Gemini API** ✅ ROZWIĄZANE
- **Błąd**: Niektóre pliki używały `gemini-2.5-flash`, inne `gemini-1.5-flash`
- **Rozwiązanie**: Standardowa wersja `gemini-1.5-flash` dla wszystkich

## 📈 Statystyki Refaktoryzacji

- **Przed**: ~2000 linii zduplikowanego kodu
- **Po**: ~800 linii w modułach + ~200 linii w aplikacjach = **50% redukcja**
- **Funkcji wspólnych**: `get_available_models`, `ask_ollama`, `judge_with_gemini`, `generate_summary`
- **Ujednoliconych formatów**: Timeouty, struktura odpowiedzi, error handling

## 🎯 Plan Kolejnych Kroków

1. ✅ **Faza 1**: Refaktoryzacja architektury (UKOŃCZONA)
2. 🔄 **Faza 2**: Migracja pozostałych plików do nowej architektury
3. 📋 **Faza 3**: Testy integracyjne nowej struktury
4. 🗑️ **Faza 4**: Usunięcie starych, duplikowanych plików

## 🤝 Kompatybilność Wsteczna

Stare pliki nadal działają, ale zachęcamy do przejścia na:
- `ollama_unified_benchmark.py` zamiast `ollama_comprehensive_benchmark.py`
- `ollama_basic_chat_v2.py` zamiast `ollama_basic_chat.py`

## 📚 Dokumentacja API

### Główne klasy:
- `BaseTester` - Bazowa klasa dla wszystkich testerów
- `ComprehensiveBenchmarkTester` - Implementacja w `ollama_unified_benchmark.py`

### Główne funkcje:
- `get_available_models()` - Lista modeli Ollama
- `ask_ollama()` - Komunikacja z modelem
- `judge_with_gemini()` - Ocena AI sędziego
- `generate_summary()` - Podsumowania wyników

---

**Ollama Testing Suite v2.0** - Profesjonalny framework do testowania LLM z oceną AI sędziego.
