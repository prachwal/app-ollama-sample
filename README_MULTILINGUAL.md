# Ollama Multilingual Testing Suite 🌍

Zaawansowany system testowania modeli LLM z obsługą wielojęzyczności, oferujący zarówno interfejs graficzny jak i konsolowy.

## 🚀 Najnowsze funkcje v2.2

### ✨ Wybór języka testów
- **Polski** - Oryginalny zestaw testów w języku polskim  
- **English** - Kompletne tłumaczenia wszystkich testów na język angielski
- **Wielojęzyczny interfejs** - GUI i CLI automatycznie dostosowują się do wybranego języka

### 🎯 Uspójniony interfejs GUI
- **Unified test controls** - Wszystkie przyciski testów w jednej zakładce
- **Dropdown wyboru języka** - Łatwa zmiana języka testów
- **Konsystentny stan przycisków** - Brak duplikatów, wszystko działa synchronicznie  
- **Improved stop functionality** - Możliwość przerwania testów w dowolnym momencie

### 📁 Struktura projektu

```
app-ollama-sample/
├── src/                              # Modułowa architektura
│   ├── api/                         # Komunikacja z modelami
│   │   ├── __init__.py
│   │   └── ollama_client.py
│   ├── config/                      # Konfiguracja
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── testers/                     # Moduły testowe
│   │   ├── __init__.py
│   │   ├── comprehensive_tester.py
│   │   └── quick_tester.py
│   └── utils/                       # Narzędzia pomocnicze
│       ├── __init__.py
│       ├── file_utils.py
│       ├── test_prompts.py          # Polskie testy
│       └── multilingual_prompts.py  # Angielskie testy
├── ollama_basic_chat_gui.py         # GUI v2.1 z wyborem języka
├── ollama_multilingual_cli.py       # CLI v2.1 z wyborem języka
├── test_exporter.py                 # Eksporter testów
└── exported_tests/                  # Wyeksportowane testy
    ├── all_tests_export.json       # JSON (21,806 bytes)
    ├── all_tests_export.md         # Markdown (18,114 bytes)
    └── all_tests_export.csv        # CSV (9,877 bytes)
```

## 🎯 Dostępne aplikacje

### 1. **GUI Application** (`ollama_basic_chat_gui.py`)
Profesjonalny interfejs graficzny z zakładkami:
- **Chat interaktywny** - Rozmowa z wybranym modelem
- **Centrum testowe** - Uruchamianie testów ze wskaźnikami postępu
- **Zarządzanie plikami** - Przeglądanie wyników testów
- **🆕 Wybór języka** - Dropdown do wyboru języka testów

```bash
python ollama_basic_chat_gui.py
```

### 2. **Multilingual CLI** (`ollama_multilingual_cli.py`)
Konsolowy interfejs z pełną obsługą języków:
- **Wybór języka przy starcie** - Polski/English
- **Interaktywny czat** - Rozmowa z modelami
- **Testy komprehensywne** - 13 zadań w wybranym języku
- **Testy szybkie** - 6 podstawowych zadań
- **Własne pytania** - Do wszystkich modeli jednocześnie

```bash
python ollama_multilingual_cli.py
```

### 3. **Test Exporter** (`test_exporter.py`)
Eksportuje wszystkie testy do różnych formatów:
- **48 total tests** (24 PL + 24 EN)
- **JSON, Markdown, CSV** formats
- **Metadane testów** - Kategorie, trudność, judge prompts

```bash
python test_exporter.py
```

## 📊 Zestawy testów

### 🇵🇱 **Polskie testy** (Oryginalne)
#### Testy komprehensywne (13):
1. **Matematyka** - Rozwiązywanie równań
2. **Logika** - Zagadki logiczne  
3. **Analiza tekstu** - Interpretacja literatury
4. **Kreatywność** - Pisanie opowiadań
5. **Wiedza ogólna** - Pytania encyklopedyczne
6. **Programowanie** - Zadania kodowania
7. **Etyka AI** - Dylematy moralne
8. **Analiza danych** - Interpretacja wykresów
9. **Tłumaczenie** - Przekład tekstów
10. **Podsumowanie** - Streszczanie artykułów
11. **Klasyfikacja** - Kategoryzacja obiektów
12. **Wnioskowanie** - Dedukcja logiczna
13. **Problem solving** - Rozwiązywanie problemów

#### Testy szybkie (6):
1. **Podstawowa matematyka**
2. **Proste tłumaczenie**
3. **Krótkie podsumowanie**
4. **Podstawowa logika**
5. **Ogólna wiedza**
6. **Prosty problem**

### 🇬🇧 **English tests** (Tłumaczenia)
#### Comprehensive tests (13):
1. **Mathematics** - Equation solving
2. **Logic** - Logic puzzles
3. **Text Analysis** - Literature interpretation
4. **Creativity** - Story writing
5. **General Knowledge** - Encyclopedia questions
6. **Programming** - Coding tasks
7. **AI Ethics** - Moral dilemmas
8. **Data Analysis** - Chart interpretation
9. **Translation** - Text translation
10. **Summarization** - Article summaries
11. **Classification** - Object categorization
12. **Reasoning** - Logical deduction
13. **Problem Solving** - Problem resolution

#### Quick tests (6):
1. **Basic Mathematics**
2. **Simple Translation**
3. **Short Summary**
4. **Basic Logic**
5. **General Knowledge**
6. **Simple Problem**

## 🤖 Obsługiwane modele

System automatycznie wykrywa wszystkie dostępne modele Ollama:
- `llama3.2:latest`
- `qwen2.5:latest`
- `phi3:latest`
- `mistral:latest`
- `codellama:latest`
- `deepseek-coder:latest`
- `gemma2:latest`
- i inne...

## 📈 Wyniki testów

### Automatyczne zapisywanie:
- **Chat logs** - `chat_model_timestamp.txt`
- **Test results** - `test_type_language_timestamp.txt`
- **Single questions** - `single_test_language_timestamp.txt`

### Podsumowania testów:
- Czas wykonania
- Liczba successful/failed responses
- Statystyki wydajności
- Porównanie modeli

## 🛠️ Instalacja i konfiguracja

### Wymagania:
```bash
# 1. Zainstaluj Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pobierz modele
ollama pull llama3.2
ollama pull qwen2.5
ollama pull phi3

# 3. Sprawdź dostępne modele
ollama list
```

### Uruchomienie:
```bash
# GUI z wyborem języka
python ollama_basic_chat_gui.py

# CLI wielojęzyczny  
python ollama_multilingual_cli.py

# Eksport testów
python test_exporter.py
```

## 🔧 Konfiguracja

Edytuj `src/config/settings.py`:
```python
DEFAULT_SLEEP_BETWEEN_MODELS = 1.0  # Przerwa między modelami
DEFAULT_TEMPERATURE = 0.7           # Losowość odpowiedzi
DEFAULT_MAX_TOKENS = 1000           # Maksymalna długość
```

## 📝 Przykłady użycia

### GUI - Wybór języka testów:
1. Uruchom aplikację GUI
2. W panelu bocznym wybierz język z dropdown "Język testów"
3. Uruchom test - wszystkie prompty będą w wybranym języku
4. Wyniki automatycznie zawierają informację o języku

### CLI - Wielojęzyczny workflow:
1. Start aplikacji → wybór języka (Polski/English)
2. Menu dynamicznie dostosowuje się do języka
3. Wszystkie testy używają wybranych promptów
4. Pliki wyników zawierają suffix `_english` dla ang

### Test Exporter - Pełny eksport:
```bash
python test_exporter.py
# Tworzy: all_tests_export.json (48 tests)
#         all_tests_export.md   (formatted)  
#         all_tests_export.csv  (tabular)
```

## 🌟 Najważniejsze ulepszenia

### v2.1 - Multilingual Support:
- ✅ **Wybór języka w GUI** - Dropdown widget
- ✅ **Wielojęzyczny CLI** - Menu w wybranym języku  
- ✅ **Angielskie testy** - Pełne tłumaczenia wszystkich promptów
- ✅ **Language-aware file naming** - `test_english_timestamp.txt`
- ✅ **Dynamic UI adaptation** - Interfejs dostosowuje się do języka

### v2.0 - GUI & Architecture:
- ✅ **Modułowa architektura** - Struktura src/
- ✅ **Pełny GUI** - Profesjonalny interfejs graficzny
- ✅ **Test Exporter** - Eksport do JSON/MD/CSV
- ✅ **Eliminacja duplikacji** - Unified codebase
- ✅ **Threading** - Responsywny interfejs

## 📊 Statystyki projektu

### Struktura kodu:
- **Total lines**: ~30,000
- **Files**: 15+ modules
- **Tests**: 48 (24 PL + 24 EN)
- **Export formats**: 3 (JSON, MD, CSV)
- **Languages**: 2 (Polish, English)

### Export files:
- `all_tests_export.json` - 21,806 bytes
- `all_tests_export.md` - 18,114 bytes  
- `all_tests_export.csv` - 9,877 bytes

## 🚀 Następne kroki

Planowane funkcje:
- [ ] **Więcej języków** - Niemiecki, francuski, hiszpański
- [ ] **Custom test sets** - Własne zestawy testów
- [ ] **Model comparison** - Porównanie side-by-side
- [ ] **Test scheduling** - Automatyczne testy cykliczne
- [ ] **API integration** - REST API dla zewnętrznych systemów

---

## 💡 Tips & Tricks

### Optymalizacja wydajności:
- Dostosuj `DEFAULT_SLEEP_BETWEEN_MODELS` w zależności od mocy systemu
- Używaj testów szybkich do wstępnej oceny modeli
- Eksportuj testy przed dużymi zmianami w promptach

### Zarządzanie językami:
- CLI automatycznie wykrywa preferowany język systemu
- GUI zapamiętuje ostatni wybór języka w sesji
- Pliki wyników zawierają metadane języka

### Best practices:
- Uruchamiaj testy komprehensywne w godzinach nocnych
- Regularnie eksportuj testy jako backup
- Monitoruj logi dla błędów modeli

**Happy Testing! 🤖✨**
