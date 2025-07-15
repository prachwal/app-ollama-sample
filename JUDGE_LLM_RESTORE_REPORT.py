#!/usr/bin/env python3
"""
PRZYWRÓCENIE SĘDZIEGO LLM DO GUI
===============================

Funkcjonalność sędziego AI (Gemini) została pomyślnie przywrócona do GUI v2.1

🤖 DODANE FUNKCJONALNOŚCI:
=========================

### 1. Panel Kontrolny Sędziego AI:
- ✅ Checkbox "🤖 Sędzia AI (Gemini)" w panelu bocznym
- ✅ Przycisk "🔑 Klucz API" do konfiguracji 
- ✅ Opcja włączania/wyłączania sędziego

### 2. Dialog Konfiguracji:
- ✅ Bezpieczne wprowadzanie klucza API (maskowane pole)
- ✅ Informacje o tym jak uzyskać klucz API
- ✅ Opcje zapisywania/wyłączania sędziego
- ✅ Walidacja wprowadzonego klucza

### 3. Integracja z Testami:
- ✅ Automatyczna ocena każdej odpowiedzi modelu (1-5)
- ✅ Wyświetlanie oceny w czasie rzeczywistym ⭐4/5
- ✅ Obsługa błędów sędziego z komunikatami
- ✅ Dodawanie ocen do statystyk podsumowania

### 4. Funkcjonalności Sędziego:
- ✅ Ocena poprawności odpowiedzi
- ✅ Ocena kompletności
- ✅ Ocena zrozumiałości  
- ✅ Zgodność z instrukcją
- ✅ Skala 1-5 z uzasadnieniem

🔧 IMPLEMENTACJA TECHNICZNA:
===========================

### Dodane Zmienne:
```python
self.use_judge = tk.BooleanVar(value=True)  # Włączanie sędziego
self.gemini_api_key = ""                    # Klucz API Gemini
```

### Dodane Funkcje:
- `on_judge_changed()` - Obsługa zmiany stanu sędziego
- `configure_gemini_api()` - Dialog konfiguracji API key

### Aktualizowane Funkcje:
- `run_test()` - Dodana ocena przez sędziego AI
- Wyświetlanie wyników z oceną ⭐X/5

### API Integration:
```python
from src.api import judge_with_gemini

rating, justification = judge_with_gemini(
    result['response'],     # Odpowiedź modelu
    test['prompt'],         # Oryginalne pytanie  
    self.gemini_api_key     # Klucz API
)
```

🎯 SPOSÓB UŻYCIA:
================

### Krok 1: Konfiguracja
1. Uruchom GUI: `python ollama_basic_chat_gui.py`
2. W panelu bocznym kliknij "🔑 Klucz API"
3. Wprowadź klucz API Gemini z https://makersuite.google.com/app/apikey
4. Kliknij "💾 Zapisz klucz"

### Krok 2: Testowanie z Sędzią
1. Upewnij się że checkbox "🤖 Sędzia AI (Gemini)" jest zaznaczony
2. Wybierz język testów (polski/angielski)
3. Uruchom "🚀 Szybki test" lub "🔬 Test kompletny"
4. Obserwuj oceny w czasie rzeczywistym: ⭐4/5

### Krok 3: Analiza Wyników
- Każda odpowiedź otrzymuje ocenę 1-5
- Średnie oceny są pokazane w podsumowaniu
- Szczegółowe uzasadnienia są zapisywane w pliku wyników

📊 PRZYKŁAD DZIAŁANIA:
=====================

```
📝 Zadanie 1: Przedstawienie
  🤖 llama3.2:1b: 🔄 Ocena AI... ⭐4/5 [szczegóły]
  🤖 qwen2.5:0.5b: 🔄 Ocena AI... ⭐3/5 [szczegóły]
  🤖 gemma2:2b: 🔄 Ocena AI... ⭐5/5 [szczegóły]

📊 PODSUMOWANIE:
Średnie oceny sędziego AI:
- llama3.2:1b: 4.2/5
- qwen2.5:0.5b: 3.8/5  
- gemma2:2b: 4.6/5
```

🔒 BEZPIECZEŃSTWO:
=================

- ✅ Klucz API jest maskowany podczas wprowadzania
- ✅ Klucz jest przechowywany tylko w sesji (nie zapisywany na dysk)
- ✅ Bezpieczna komunikacja z API Gemini
- ✅ Obsługa błędów sieci i API

⚡ WYDAJNOŚĆ:
=============

- ✅ Ocena sędziego działa równolegle z zapisem wyników
- ✅ Timeout protection dla API calls
- ✅ Graceful degradation przy błędach sędziego
- ✅ Non-blocking UI podczas oceniania

🎉 STATUS: SĘDZIA LLM PRZYWRÓCONY I GOTOWY!
==========================================

GUI v2.1 teraz zawiera pełną funkcjonalność sędziego AI z:
- Wielojęzycznym wsparciem (PL/EN)
- Konfiguracją przez GUI
- Oceną w czasie rzeczywistym
- Integrację ze statystykami

Wszystkie funkcjonalności są w pełni funkcjonalne i przetestowane! 🚀
"""
