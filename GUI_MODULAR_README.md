# GUI Modular Structure

## Struktura katalogów

```
gui/
├── __init__.py              # Główny moduł GUI
├── config.py                # Konfiguracja i stałe
├── main_window.py           # Główne okno aplikacji
├── components/              # Komponenty GUI
│   ├── __init__.py
│   ├── chat_component.py    # Komponent czatu
│   └── testing_component.py # Komponent testów
└── dialogs/                 # Dialogi
    ├── __init__.py
    ├── system_prompt_dialog.py    # Dialog edycji promptu systemowego
    ├── quick_test_dialog.py       # Dialog szybkiego testu
    └── custom_test_dialog.py      # Dialog własnego testu
```

## Opis plików

### `main_window.py` (280 linii)
- Główna klasa `OllamaGUI`
- Konfiguracja okna i menu
- Zarządzanie modelami
- Pasek statusu i postępu

### `components/chat_component.py` (320 linii) 
- Komponent obsługujący czat
- Tryby systemowe (persony)
- Wysyłanie wiadomości
- Zarządzanie historią czatu

### `components/testing_component.py` (390 linii)
- Komponent testów
- Testy szybkie i własne
- Wyświetlanie wyników
- Parametry testowania

### `dialogs/` (3 pliki, łącznie 330 linii)
- **system_prompt_dialog.py**: Dialog edycji promptu systemowego
- **quick_test_dialog.py**: Dialog wprowadzania pytania testowego  
- **custom_test_dialog.py**: Dialog tworzenia zaawansowanych testów

### `config.py` (100 linii)
- Tryby systemowe (persony)
- Konfiguracja stylów GUI
- Ustawienia okna
- Tagi kolorowania tekstu

## Porównanie z monolityczną wersją

| Metryka | Monolityczna | Modularna | Poprawa |
|---------|--------------|-----------|---------|
| **Liczba linii** | 1599 | 1422 | -177 linii |
| **Liczba plików** | 1 | 8 | +7 plików |
| **Czytelność** | Niska | Wysoka | ✅ |
| **Łatwość modyfikacji** | Niska | Wysoka | ✅ |
| **Ponowne użycie** | Brak | Wysokie | ✅ |

## Uruchamianie

```bash
# Nowa modułowa wersja
python ollama_modular_gui.py

# Oryginalna wersja (nadal dostępna)
python ollama_basic_chat_gui.py
```

## Korzyści modularyzacji

1. **Łatwość nawigacji** - każdy komponent w osobnym pliku
2. **Izolacja funkcjonalności** - czat i testy są niezależne
3. **Łatwość testowania** - komponenty można testować osobno
4. **Możliwość rozbudowy** - nowe komponenty bez wpływu na istniejące
5. **Czysty kod** - separacja logiki biznesowej od GUI
6. **Lepsze zarządzanie** - konfiguracja wydzielona do osobnego pliku

## Funkcjonalność

Modułowa wersja implementuje wszystkie kluczowe funkcje:

- ✅ Czat z modelami Ollama
- ✅ Tryby systemowe (9 predefiniowanych + własny)
- ✅ Testy szybkie i zaawansowane  
- ✅ Zapisywanie/wczytywanie czatów
- ✅ Zapisywanie/wczytywanie testów
- ✅ Pasek postępu i statusu
- ✅ Menu i skróty klawiszowe

Pominięte funkcje (dostępne w oryginalnej wersji):
- Wybór języka testów
- Sędzia LLM (Gemini API)
- Zaawansowane funkcje testowania językowego
