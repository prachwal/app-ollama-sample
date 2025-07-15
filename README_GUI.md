# Ollama Basic Chat GUI

🤖 **Pełny interfejs graficzny dla aplikacji Ollama Basic Chat**

## 📋 Opis

Graficzny interfejs użytkownika (GUI) dla aplikacji ollama_basic_chat, zbudowany z wykorzystaniem tkinter. Oferuje przyjazny interfejs do:

- 💬 **Interaktywnego czatu** z wybranymi modelami LLM
- 🧪 **Uruchamiania testów** (szybkich i kompletnych)  
- 📊 **Monitorowania wyników** w czasie rzeczywistym
- 📁 **Zarządzania plikami czatu** (zapisywanie/wczytywanie)

## 🚀 Uruchomienie

### Metoda 1: Plik wsadowy (Windows)
```cmd
start_gui.bat
```

### Metoda 2: Launcher Python
```bash
python launch_gui.py
```

### Metoda 3: Bezpośrednio
```bash
python ollama_basic_chat_gui.py
```

## 🎯 Funkcjonalności

### 💬 Czat
- **Wybór modelu** z listy dostępnych
- **🆕 Tryb systemowy (Persona)** - Predefiniowane role i własne prompty systemowe
- **Interaktywny czat** z wybranymi modelami
- **Historia rozmów** z kolorowaniem składni
- **Zapisywanie czatów** do plików tekstowych
- **Wczytywanie** wcześniejszych rozmów

#### 🎭 Dostępne tryby systemowe:
- **Standardowy** - Brak prompta systemowego
- **Profesjonalny programista** - Ekspert programowania z najlepszymi praktykami
- **Asystent naukowy** - Obiektywne, bazowane na faktach odpowiedzi
- **Kreatywny pisarz** - Żywy język, metafory i storytelling
- **Analityk biznesowy** - Strategiczne myślenie i rozwiązania biznesowe
- **Nauczyciel** - Wyjaśnienia krok po kroku z przykładami
- **Ekspert IT** - Architektura, bezpieczeństwo, wydajność
- **Konsultant prawny** - Analiza prawna z zaznaczeniem limitów
- **Psycholog** - Empatyczne wsparcie i przemyślane pytania
- **Własny prompt** - Możliwość zdefiniowania własnej persona

### 🧪 Testy
- **🆕 Wybór języka testów** - Polski/English dropdown
- **Szybki test** - 6 podstawowych zadań dla wszystkich modeli
- **Test kompletny** - 13 rozszerzonych testów wydajności
- **Własne pytania** - zadawanie pytań wszystkim modelom
- **Monitoring postępu** w czasie rzeczywistym z możliwością przerwania
- **Szczegółowe wyniki** z oceną AI sędziego (Gemini)
- **Eksport wyników** do plików z timestamp

### 🎨 Interfejs
- **Zakładki** dla różnych funkcji (Czat/Testy)
- **🆕 Unified Test Controls** - Wszystkie przyciski testów w jednej zakładce
- **Panel boczny** z ustawieniami i akcjami (bez duplikatów przycisków)
- **Pasek postępu** dla długotrwałych operacji z przyciskiem Stop
- **Kolorowanie składni** dla lepszej czytelności
- **Responsywny design** dostosowujący się do okna
- **Status messages** z informacjami o postępie

## 📁 Struktura

```
├── ollama_basic_chat_gui.py    # Główna aplikacja GUI
├── launch_gui.py               # Launcher z sprawdzaniem wymagań
├── start_gui.bat              # Plik wsadowy dla Windows
├── src/                       # Moduły modułowej architektury
│   ├── api/                   # Klienty API (Ollama, Gemini)
│   ├── utils/                 # Narzędzia pomocnicze
│   └── config.py              # Konfiguracja centralna
└── README_GUI.md              # Ta dokumentacja
```

## ⚙️ Wymagania

- **Python 3.7+**
- **Tkinter** (zwykle wbudowany w Python)
- **Modułowa architektura** z folderu `src/`
- **Działający serwer Ollama**

## 🔧 Konfiguracja

Aplikacja używa centralnej konfiguracji z `src/config.py`:

```python
OLLAMA_API_URL = "http://localhost:11434"
DEFAULT_SLEEP_BETWEEN_MODELS = 2
GEMINI_JUDGE_MODEL_NAME = "gemini-1.5-flash"
```

## 📱 Skróty klawiszowe

- **Ctrl+Enter** - Wyślij wiadomość w czacie
- **Escape** - Zamknij dialogi / Przerwij test
- **F5** - Odśwież listę modeli
- **📝 Edytuj** - Otwórz dialog edycji trybu systemowego
- **🗑️ Reset** - Przywróć tryb standardowy

## 🔧 Najnowsze poprawki

### ✅ v2.2 Tryby systemowe (Persona):
- **🎭 Predefiniowane role** - 9 gotowych persona (programista, nauczyciel, pisarz, etc.)
- **📝 Własne prompty** - Możliwość zdefiniowania własnego trybu systemowego
- **🔄 Łatwa zmiana** - Dropdown z trybami + przyciski edycji/reset
- **💾 Zapisywanie** - Własne prompty są zapamiętywane w sesji
- **🎯 Kontekst rozmowy** - System prompt wpływa na wszystkie odpowiedzi modelu

### ✅ v2.1 Uspójnienie interfejsu:
- **Usunięto duplikaty przycisków** - Wszystkie kontrolki testów tylko w zakładce "Testy"
- **Synchronizacja stanu** - Przyciski działają konsekwentnie
- **Improved stop functionality** - Możliwość przerwania testów w dowolnym momencie
- **Better error handling** - Lepsze komunikaty błędów i statusu

## 💡 Przykłady użycia trybów systemowych

### 🧑‍💻 Programista
```
Tryb: Profesjonalny programista
Pytanie: "Jak zoptymalizować ten kod Python?"
Odpowiedź: Otrzymasz szczegółową analizę z najlepszymi praktykami, 
przykładami kodu i wyjaśnieniami wydajności.
```

### 🎨 Kreatywny pisarz  
```
Tryb: Kreatywny pisarz
Pytanie: "Opisz zachód słońca nad morzem"
Odpowiedź: Otrzymasz poetycki, obrazowy opis z metaforami 
i emocjonalnym językiem.
```

### 🎓 Nauczyciel
```
Tryb: Nauczyciel
Pytanie: "Wyjaśnij kwantową fizykę"
Odpowiedź: Otrzymasz wyjaśnienie krok po kroku, z prostymi przykładami
i pytaniami kontrolnymi.
```

## 🐛 Rozwiązywanie problemów

### GUI się nie uruchamia
```bash
python -c "import tkinter; print('Tkinter OK')"
```

### Brak modeli
- Sprawdź czy Ollama jest uruchomiony
- Sprawdź URL w konfiguracji
- Użyj przycisku "🔄 Odśwież modele"

### Błędy podczas testów
- Sprawdź połączenie z Ollama
- Sprawdź logi w terminalu
- Sprawdź dostęp do API Gemini (dla AI judge)

## 📈 Rozwój

### Planowane funkcjonalności
- [ ] **Eksport wyników** do różnych formatów
- [ ] **Ustawienia zaawansowane** w GUI
- [ ] **Tematy kolorystyczne**
- [ ] **Plugins system**
- [ ] **Historia czatów** z bazą danych
- [ ] **Porównania modeli** side-by-side

### Architektura
Aplikacja GUI wykorzystuje:
- **Threading** dla nieblokujących operacji
- **Queue** dla komunikacji między wątkami  
- **Modułowa architektura** z `src/`
- **Event-driven design** dla responsywności

## 🤝 Wkład

Kod źródłowy jest dostępny w repozytorium. Miłe widziane:
- 🐛 Zgłaszanie błędów
- ✨ Propozycje funkcjonalności  
- 🔧 Pull requesty
- 📚 Udoskonalenia dokumentacji

## 📄 Licencja

Ten projekt wykorzystuje tę samą licencję co projekt główny ollama_basic_chat.

---
💡 **Tip**: Dla najlepszych wyników upewnij się, że Ollama jest uruchomiony i ma załadowane modele przed uruchomieniem GUI.
