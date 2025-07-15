# Ollama Advanced Testing Suite 🚀

**Kompleksowy system testowania modeli LLM z interfejsem graficznym i wielojęzyczną obsługą**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-green.svg)](https://ollama.ai/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

## 📋 Przegląd projektu

Zaawansowana platforma do testowania i porównywania modeli LLM z obsługą Ollama API. Oferuje zarówno graficzny jak i konsolowy interfejs użytkownika z funkcjami automatyzacji, wielojęzyczności i szczegółowej analizy wyników.

### 🌟 Główne funkcjonalności

- 💬 **Interaktywny chat** z modelami LLM
- 🧪 **Komprehensywne testy** z oceną AI sędziego (Gemini)
- 🌍 **Obsługa wielojęzyczna** (Polski/English)
- 📊 **Analiza i filtrowanie** modeli po parametrach
- 🎨 **Graficzny interfejs użytkownika** (Tkinter)
- 🔍 **System eksportu** wyników (JSON/CSV/Markdown)
- 🧹 **Automatyczne czyszczenie** projektu
- 📁 **Modułowa architektura** dla łatwego rozwoju

## 🚀 Szybki Start

### 1. Uruchomienie GUI (Zalecane)
```bash
# Metoda 1: Plik wsadowy Windows
start_gui.bat

# Metoda 2: Python launcher
python launch_gui.py

# Metoda 3: Bezpośrednio
python ollama_basic_chat_gui.py
```

### 2. Uruchomienie CLI wielojęzycznego
```bash
python ollama_multilingual_cli.py
```

### 3. Czyszczenie projektu
```powershell
# PowerShell - zaawansowany z opcjami
.\cleanup.ps1 -DryRun        # Podgląd
.\cleanup.ps1 -Force         # Automatyczne

# PowerShell - szybki
.\quick-cleanup.ps1

# Windows Batch
cleanup.bat
```

## 🏗️ Architektura Projektu

```
app-ollama-sample/
├── 🎨 GUI APLIKACJE
│   ├── ollama_basic_chat_gui.py      # Główny interfejs graficzny
│   ├── launch_gui.py                 # Launcher z walidacją
│   └── start_gui.bat                # Windows starter
│
├── 💻 CLI APLIKACJE  
│   └── ollama_multilingual_cli.py    # Wielojęzyczny interfejs konsolowy
│
├── 🧹 AUTOMATYZACJA
│   ├── cleanup.ps1                   # Zaawansowane czyszczenie PowerShell
│   ├── quick-cleanup.ps1            # Szybkie czyszczenie PowerShell
│   └── cleanup.bat                  # Czyszczenie Windows Batch
│
├── 📁 MODUŁOWA ARCHITEKTURA
│   └── src/
│       ├── api/                     # Klienty API (Ollama, Gemini)
│       ├── utils/                   # Narzędzia i prompty testowe
│       ├── testers/                 # Moduły testowe
│       └── config.py               # Centralna konfiguracja
│
├── 📚 DOKUMENTACJA
│   ├── README.md                    # Ten plik - główny przegląd
│   ├── README_GUI.md               # Szczegóły interfejsu graficznego
│   ├── README_MULTILINGUAL.md      # Wielojęzyczność i testy
│   ├── README_CLEANUP.md           # Skrypty czyszczenia
│   ├── README_FILTERING.md         # Filtrowanie modeli
│   └── README_REFACTORING.md       # Historia refaktoryzacji
│
└── ⚙️ KONFIGURACJA
    ├── .gitignore                  # Ignorowane pliki Git
    ├── .vscode/launch.json         # Konfiguracja debug VS Code
    └── cache/                      # Cache metadanych modeli
```

## 🎯 Aplikacje i Narzędzia

### 🎨 GUI - Interfejs Graficzny

**Plik:** `ollama_basic_chat_gui.py`

**Funkcjonalności:**
- ✅ **Zakładki** dla różnych funkcji (Chat/Testy)
- ✅ **🆕 Tryby systemowe** - 9 predefiniowanych persona + własne prompty
- ✅ **Wybór języka testów** (Polski/English dropdown)
- ✅ **Interaktywny chat** z wybranymi modelami
- ✅ **Testy szybkie i kompletne** z paskiem postępu
- ✅ **Zarządzanie plikami** chat'ów (zapis/odczyt)
- ✅ **Monitoring w czasie rzeczywistym** testów
- ✅ **Status przerwania testów** z przyciskiem Stop

```bash
python ollama_basic_chat_gui.py
```

### 💻 CLI - Wielojęzyczny Interfejs Konsolowy

**Plik:** `ollama_multilingual_cli.py`

**Funkcjonalności:**
- ✅ **Wybór języka przy starcie** (Polski/English)
- ✅ **13 testów komprehensywnych** w wybranym języku
- ✅ **6 testów szybkich** dla podstawowej oceny
- ✅ **Własne pytania** do wszystkich modeli jednocześnie
- ✅ **Ocena AI sędziego** (Gemini) z punktacją 1-10
- ✅ **Eksport wyników** do plików z timestamp

```bash
python ollama_multilingual_cli.py
```

### 🔍 Filtrowanie Modeli

**Funkcjonalność:** Znajdowanie modeli o podobnych parametrach

```bash
# Filtruj podobne do gemma2:2b (domyślnie)
python -c "from src.utils.model_filter import filter_similar_models; filter_similar_models()"

# Wyświetl wszystkie dostępne modele
python -c "from src.api.ollama_client import get_available_models; print(get_available_models())"
```

**Kryteria filtrowania:**
- **Rozmiar pliku**: ±0.5 GB
- **Liczba parametrów**: ±1B
- **Długość kontekstu**: ±50,000 tokenów  
- **Liczba warstw**: ±5 warstw

## 🌍 Wielojęzyczność

### Obsługiwane języki testów:
- 🇵🇱 **Polski** - Oryginalny zestaw 19 testów
- 🇬🇧 **English** - Pełne tłumaczenia wszystkich testów

### Typy testów:
1. **Testy komprehensywne** (13): Matematyka, Logika, Kreatywność, Programowanie, Etyka AI, itp.
2. **Testy szybkie** (6): Podstawowe zadania dla szybkiej oceny
3. **Własne pytania**: Zadawanie dowolnych pytań wszystkim modelom

### Ocena wyników:
- **AI Sędzia**: Gemini-1.5-flash ocenia odpowiedzi w skali 1-10
- **Szczegółowa analiza**: Mocne i słabe strony każdego modelu
- **Ranking modeli**: Sortowanie według średniej punktacji

## 🧹 Automatyzacja i Czyszczenie

### PowerShell (Zaawansowany)
```powershell
.\cleanup.ps1 -DryRun     # Podgląd bez usuwania
.\cleanup.ps1             # Interaktywne czyszczenie
.\cleanup.ps1 -Force      # Automatyczne bez pytań
```

### PowerShell (Szybki)
```powershell
.\quick-cleanup.ps1       # Szybkie czyszczenie bez opcji
```

### Windows Batch
```cmd
cleanup.bat               # Kompatybilny z wszystkimi Windows
```

**Co usuwa:**
- ✅ Cache Python (`__pycache__`, `.pyc`)
- ✅ Pliki testów (`*test*.txt`, `chat_*.txt`)
- ✅ Pliki tymczasowe (`.tmp`, `.bak`, `.old`)
- ✅ Pliki systemu (`.DS_Store`, `Thumbs.db`)
- ✅ Cache IDE (`.vscode/settings.json`, `*.swp`)

## ⚙️ Konfiguracja

### Wymagania systemowe:
- **Python 3.7+**
- **Tkinter** (wbudowany w Python)
- **Działający serwer Ollama** (`http://localhost:11434`)
- **Klucz API Gemini** (dla funkcji sędziego AI)

### Konfiguracja środowiska:
```bash
# Ustaw klucz API Gemini (opcjonalne)
export GEMINI_API_KEY="your-api-key-here"

# Lub ustaw w pliku .env
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

### Centralna konfiguracja (`src/config.py`):
```python
OLLAMA_API_URL = "http://localhost:11434"
GEMINI_JUDGE_MODEL_NAME = "gemini-1.5-flash"
DEFAULT_TIMEOUT_PER_MODEL = 180
DEFAULT_SLEEP_BETWEEN_MODELS = 2
```

## 📊 Przykładowe wyniki

### Test wielojęzyczny (Polski):
```
📊 WYNIKI TESTÓW KOMPREHENSYWNYCH:
====================================
🥇 qwen2.5:7b        - Średnia: 8.2/10 (Doskonały)
🥈 llama3.2:3b       - Średnia: 7.8/10 (Bardzo dobry)  
🥉 gemma2:2b         - Średnia: 7.1/10 (Dobry)

💎 NAJLEPSZE WYNIKI:
- Matematyka: qwen2.5:7b (9.5/10)
- Kreatywność: llama3.2:3b (9.0/10)
- Programowanie: qwen2.5:7b (8.8/10)
```

### Filtrowanie modeli:
```
📋 MODELE PODOBNE DO gemma2:2b:
================================
1. qwen3:1.7b         - Podobieństwo: 4/4 (Doskonałe)
2. llama3.2:3b        - Podobieństwo: 3/4 (Bardzo dobre)
3. qwen2.5-coder:1.5b - Podobieństwo: 2/4 (Dobre)
```

## 🛠️ Rozwój i Rozszerzanie

### Dodawanie nowych testów:
```python
# src/utils/test_prompts.py (polski)
COMPREHENSIVE_TESTS = {
    "nowy_test": {
        "prompt": "Twój prompt testowy...",
        "judge_prompt": "Kryteria oceny...",
        "category": "Kategoria"
    }
}

# src/utils/multilingual_prompts.py (angielski)
COMPREHENSIVE_TESTS_EN = {
    "new_test": {
        "prompt": "Your test prompt...",
        "judge_prompt": "Evaluation criteria...",
        "category": "Category"
    }
}
```

### Dodawanie nowych testerów:
```python
from src.testers.base_tester import BaseTester

class MyCustomTester(BaseTester):
    def run_custom_test(self):
        # Twoja implementacja
        pass
```

## 🤝 Wkład w projekt

Miłe widziane:
- 🐛 **Zgłaszanie błędów** via Issues
- ✨ **Propozycje funkcjonalności**
- 🔧 **Pull requesty** z poprawkami
- 📚 **Udoskonalenia dokumentacji**
- 🌍 **Tłumaczenia** na nowe języki

## 📋 Roadmapa

### 🔄 W trakcie:
- [ ] **Baza danych** dla historii testów
- [ ] **Tematy UI** (ciemny/jasny)
- [ ] **Wykres wydajności** modeli
- [ ] **API REST** dla zdalnych testów

### 🔮 Planowane:
- [ ] **Docker containers** dla łatwego wdrożenia
- [ ] **Plugin system** dla rozszerzeń
- [ ] **Web dashboard** React/Vue
- [ ] **Integracja z MLflow** dla śledzenia eksperymentów
- [ ] **Rozproszone testy** na wielu maszynach

## 🆘 Rozwiązywanie problemów

### GUI się nie uruchamia:
```bash
python -c "import tkinter; print('Tkinter OK')"
```

### Brak modeli Ollama:
```bash
# Sprawdź status Ollama
curl http://localhost:11434/api/tags

# Pobierz model testowy
ollama pull gemma2:2b
```

### Błędy API Gemini:
```bash
# Sprawdź klucz API
echo $GEMINI_API_KEY

# Test połączenia
python -c "from src.api.gemini_client import test_connection; test_connection()"
```

---

## 📄 Licencja

MIT License - Zobacz plik LICENSE dla szczegółów.

## 🙏 Podziękowania

- **Ollama** - Za doskonałe API i modele LLM
- **Google Gemini** - Za inteligentną ocenę wyników
- **Społeczność Open Source** - Za inspirację i wsparcie

---

**💡 Tip:** Dla najlepszych wyników upewnij się, że Ollama jest uruchomiony z załadowanymi modelami przed rozpoczęciem testów.

**📞 Wsparcie:** Jeśli masz pytania lub problemy, sprawdź dokumentację w plikach `README_*.md` lub utwórz Issue w repozytorium.
