# Filtrowanie Modeli Ollama

Narzędzie do filtrowania modeli Ollama o podobnych parametrach do wybranego modelu referencyjnego.

## 🚀 Szybki Start

### Podstawowe użycie (z API Ollama)
```bash
python filter_models.py                    # Filtruj podobne do gemma2:2b
python filter_models.py qwen3:1.7b         # Filtruj podobne do qwen3:1.7b
python filter_models.py llama3.2:3b --export --verbose  # Z eksportem i szczegółami
```

### Filtrowanie z pliku CSV
```bash
python filter_models.py gemma2:2b exports/models_metadata.csv --export
```

### Wyświetl dostępne modele
```bash
python filter_models.py --list-models
```

## 📊 Kryteria Filtrowania

System porównuje modele na podstawie 4 kryteriów:

1. **Rozmiar pliku**: ±0.5 GB od modelu referencyjnego
2. **Liczba parametrów**: ±1B parametrów
3. **Długość kontekstu**: ±50,000 tokenów
4. **Liczba warstw**: ±5 warstw

Model jest uznawany za podobny, jeśli spełnia **przynajmniej 2 z 4 kryteriów**.

## 📈 Wynik Podobieństwa

- **4/4**: Doskonała zgodność (wszystkie kryteria spełnione)
- **3/4**: Bardzo podobny
- **2/4**: Podobny (minimalny próg)

## 💾 Formaty Eksportu

- **JSON**: Strukturalne dane z wszystkimi metadanymi
- **CSV**: Tabelaryczne dane do analizy w Excel/Pandas

## 🛠️ Interfejs Interaktywny

Uruchom główny program:
```bash
python test4.py
```

Wybierz opcję **5** → **5** (Filtruj modele podobne do gemma2:2b)

## 📋 Przykładowe Wyniki

Dla modelu `gemma2:2b` (2.6B parametrów, 1.52 GB):

```
📋 ZNALEZIONO 4 PODOBNYCH MODELI:
1. qwen3:1.7b         - Wynik: 4/4 (Doskonała zgodność)
2. llama3.2:3b        - Wynik: 3/4 (Bardzo podobny)
3. qwen2.5-coder:1.5b - Wynik: 2/4 (Podobny)
4. qwen2.5:1.5b       - Wynik: 2/4 (Podobny)
```

## 🔧 Rozszerzone Opcje

### Z głównego programu (test4.py)
- **Opcja 5**: Filtrowanie z cache/API
  - **5**: Filtruj podobne do gemma2:2b
  - **6**: Wybierz własny model referencyjny
  - **7**: Filtruj z pliku CSV

### Cache i Performance
- System automatycznie cachuje metadane (24h)
- Eksport do `exports/` z timestamp
- Obsługa pandas dla zaawansowanego przetwarzania CSV

## 📁 Struktura Plików

```
app-ollama-sample/
├── test4.py                 # Główny program z rozszerzonymi opcjami
├── filter_models.py         # Narzędzie linii poleceń
├── cache/
│   └── models_metadata.pkl  # Cache metadanych
└── exports/
    ├── models_metadata_*.csv      # Pełny eksport metadanych
    ├── models_metadata_*.json     # Pełny eksport metadanych
    └── filtered_models_*.csv      # Przefiltrowane wyniki
```

## 🎯 Przypadki Użycia

1. **Znajdowanie alternatyw**: Szukanie modeli o podobnej wydajności
2. **Optymalizacja zasobów**: Modele o podobnym rozmiarze ale innych możliwościach
3. **Analiza porównawcza**: Eksport do CSV dla dalszej analizy
4. **Automatyzacja**: Integracja z pipelines CI/CD

## ⚙️ Wymagania

- Python 3.7+
- requests (do API Ollama)
- pandas (opcjonalne, do pracy z CSV)
- Ollama uruchomiona na localhost:11434
