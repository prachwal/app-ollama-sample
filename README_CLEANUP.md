# 🧹 Skrypty Czyszczenia Projektu

## Przegląd

Projekt zawiera 3 skrypty do czyszczenia zbędnych plików:

| Skrypt | Opis | Użycie |
|--------|------|---------|
| `cleanup.ps1` | Zaawansowany skrypt PowerShell z pełną kontrolą | Deweloperzy PowerShell |
| `quick-cleanup.ps1` | Prosty skrypt PowerShell do szybkiego czyszczenia | Codzienne użycie |
| `cleanup.bat` | Skrypt Batch dla użytkowników Windows | Użytkownicy bez PowerShell |

---

## 📋 cleanup.ps1 (Zaawansowany)

### Funkcje:
- **Tryb podglądu** (`-DryRun`) - pokazuje co zostanie usunięte
- **Tryb wymuszony** (`-Force`) - usuwa bez pytań
- **Kolorowe wyświetlanie** z ikonami
- **Szczegółowe raportowanie** rozmiaru plików
- **Interaktywne potwierdzenia**

### Przykłady użycia:

```powershell
# Podgląd co zostanie usunięte
.\cleanup.ps1 -DryRun

# Interaktywne czyszczenie z pytaniami
.\cleanup.ps1

# Automatyczne czyszczenie bez pytań
.\cleanup.ps1 -Force
```

### Co usuwa:
- ✅ Pliki cache Python (`.pyc`, `__pycache__`)
- ✅ Pliki testów i logów (`*test*.txt`, `chat_*.txt`)  
- ✅ Pliki tymczasowe systemu (`.DS_Store`, `Thumbs.db`)
- ✅ Pliki tymczasowe IDE (`.vscode/settings.json`, `*.swp`)
- ✅ Pliki backupów (`*.bak`, `*.backup`, `*.old`)
- ✅ Środowisko wirtualne Python (`venv/`)
- ✅ Podejrzane pliki Python (`*_old.py`, `*_test.py`)
- ✅ Pliki eksportów (`exports/*.json`, `exports/*.csv`)
- ✅ Cache metadanych (`cache/*.pkl`)

---

## ⚡ quick-cleanup.ps1 (Prosty)

### Funkcje:
- **Szybkie wykonanie** bez pytań
- **Podstawowe czyszczenie** najczęstszych śmieci
- **Raport rozmiaru** projektu po czyszczeniu

### Użycie:
```powershell
.\quick-cleanup.ps1
```

### Co usuwa:
- ✅ Cache Python
- ✅ Pliki testów podstawowe
- ✅ Pliki tymczasowe

---

## 🖥️ cleanup.bat (Windows Batch)

### Funkcje:
- **Kompatybilność** z wszystkimi wersjami Windows
- **Nie wymaga PowerShell**
- **Automatyczne wykonanie**
- **Lista pozostałych plików**

### Użycie:
```cmd
cleanup.bat
```

Lub kliknij dwukrotnie w Eksploratorze Windows.

---

## 📊 Przykładowy Wynik Czyszczenia

```
🧹 Skrypt czyszczenia projektu Ollama Basic Chat
==================================================

🔍 Szukanie: Pliki cache Python (.pyc, __pycache__)
   📁 Znaleziono: 3 plików
   ✅ Usunięto: 3 plików

🔍 Szukanie: Pliki testów i logów
   📁 Znaleziono: 5 plików  
   ✅ Usunięto: 5 plików

📊 PODSUMOWANIE:
✅ Usunięto plików: 9
⏱️  Czas wykonania: 4.34 sekund
📦 Całkowity rozmiar projektu: 210.06 KB
🎉 Czyszczenie zakończone pomyślnie!
```

---

## 🛡️ Bezpieczeństwo

### Pliki chronione (nigdy nie są usuwane):
- ✅ `ollama_basic_chat_gui.py` - główna aplikacja
- ✅ `ollama_multilingual_cli.py` - CLI wielojęzyczne  
- ✅ `src/` - modułowa architektura
- ✅ `README*.md` - dokumentacja
- ✅ `.vscode/launch.json` - konfiguracja debugowania

### Pliki usuwane bezpiecznie:
- 🗑️ Cache Python (`*.pyc`, `__pycache__`)
- 🗑️ Logi i testy (`*test*.txt`, `*.log`)
- 🗑️ Pliki tymczasowe (`.tmp`, `.temp`)
- 🗑️ Backupy (`*.bak`, `*.old`)

---

## 💡 Zalecenia

### Codzienne użycie:
```powershell
.\quick-cleanup.ps1
```

### Przed commitowaniem do git:
```powershell
.\cleanup.ps1 -Force
```

### Sprawdzenie co zostanie usunięte:
```powershell
.\cleanup.ps1 -DryRun
```

### Dla użytkowników bez PowerShell:
```cmd
cleanup.bat
```

---

## 🔧 Rozwiązywanie problemów

### Błąd: "cannot be loaded because running scripts is disabled"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Błąd: "Access denied"
- Uruchom PowerShell jako Administrator
- Lub użyj `cleanup.bat`

### Skrypt nie znajduje plików projektu
- Upewnij się, że jesteś w katalogu z `ollama_basic_chat_gui.py`
- Sprawdź ścieżkę: `Get-Location`

---

## 📈 Statystyki projektu po czyszczeniu

Po uruchomieniu skryptów czyszczenia typowy projekt zawiera:

| Typ pliku | Ilość | Rozmiar |
|-----------|-------|---------|
| Pliki Python główne | 2-3 | ~80 KB |
| Moduły src/ | 15-20 | ~60 KB |
| Dokumentacja | 5-8 | ~40 KB |
| Konfiguracja | 2-3 | ~5 KB |
| **TOTAL** | **~30** | **~185 KB** |

🎯 **Docelowy rozmiar projektu**: ~200 KB (bez śmieci)
