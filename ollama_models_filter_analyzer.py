#!/usr/bin/env python3
"""
Narzędzie do filtrowania modeli Ollama o podobnych parametrach
Usage: python filter_models.py [reference_model] [csv_file]
"""

import sys
import argparse
from pathlib import Path
from test4 import filter_similar_models_from_csv, filter_similar_models, get_enhanced_model_metadata_cached

def fetch_ollama_api_info():
    """
    Wykorzystuje lokalne API Ollama do pobrania informacji o systemie
    
    Returns:
        Informacje o dostępnych endpointach i statusie API
    """
    try:
        import requests
        
        print("🔧 SPRAWDZANIE API OLLAMA...")
        
        # Sprawdź czy Ollama działa
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        
        local_models = response.json().get('models', [])
        
        # Sprawdź uruchomione modele
        try:
            ps_response = requests.get("http://localhost:11434/api/ps", timeout=5)
            running_models = ps_response.json().get('models', []) if ps_response.status_code == 200 else []
        except:
            running_models = []
        
        print(f"✅ Ollama API działa - {len(local_models)} modeli lokalnych, {len(running_models)} uruchomionych")
        
        return {
            'status': 'active',
            'local_models_count': len(local_models),
            'running_models_count': len(running_models),
            'local_models': [m.get('name', 'N/A') for m in local_models],
            'running_models': [m.get('name', 'N/A') for m in running_models]
        }
        
    except requests.exceptions.ConnectionError:
        print("❌ Ollama API niedostępne - sprawdź czy Ollama jest uruchomiona")
        return {'status': 'offline'}
    except Exception as e:
        print(f"❌ Błąd API Ollama: {e}")
        return {'status': 'error', 'error': str(e)}

def pull_model_via_api(model_name, show_progress=True):
    """
    Pobiera model z biblioteki Ollama używając API /api/pull
    
    Args:
        model_name: Nazwa modelu do pobrania (np. 'llama3.2', 'gemma2:2b')
        show_progress: Czy pokazywać postęp pobierania
        
    Returns:
        bool: True jeśli pobieranie się powiodło, False w przeciwnym razie
    """
    try:
        import requests
        import json
        
        print(f"📥 POBIERANIE MODELU: {model_name}")
        
        payload = {
            "model": model_name,
            "stream": show_progress
        }
        
        response = requests.post(
            "http://localhost:11434/api/pull", 
            json=payload, 
            stream=show_progress,
            timeout=300  # 5 minut timeout
        )
        
        if not response.ok:
            print(f"❌ Błąd pobierania: {response.status_code} {response.text}")
            return False
        
        if show_progress:
            print("📊 Postęp pobierania:")
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        status = data.get('status', '')
                        
                        if 'pulling manifest' in status:
                            print("   📋 Pobieranie manifestu...")
                        elif 'downloading' in status:
                            total = data.get('total', 0)
                            completed = data.get('completed', 0)
                            if total > 0:
                                percent = (completed / total) * 100
                                print(f"   📁 {status}: {percent:.1f}% ({completed:,}/{total:,} bajtów)")
                            else:
                                print(f"   📁 {status}")
                        elif 'verifying' in status:
                            print("   ✅ Weryfikacja...")
                        elif 'success' in status:
                            print("   🎉 Pobieranie zakończone pomyślnie!")
                            return True
                        elif 'error' in status or data.get('error'):
                            print(f"   ❌ Błąd: {data.get('error', status)}")
                            return False
                    except json.JSONDecodeError:
                        continue
        else:
            # Bez streamingu - czekaj na zakończenie
            result = response.json()
            if result.get('status') == 'success':
                print(f"✅ Model {model_name} pobrany pomyślnie")
                return True
            else:
                print(f"❌ Błąd pobierania: {result}")
                return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Brak połączenia z API Ollama")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout podczas pobierania modelu")
        return False
    except Exception as e:
        print(f"❌ Błąd podczas pobierania: {e}")
        return False

def fetch_ollama_library_models_enhanced():
    """
    Pobiera listę modeli z biblioteki Ollama i łączy z informacjami z API
    
    Returns:
        Lista modeli z informacjami o dostępności lokalnej
    """
    try:
        # Najpierw sprawdź API
        api_info = fetch_ollama_api_info()
        local_models = set(api_info.get('local_models', []))
        
        # Następnie pobierz listę z biblioteki (użyj prostego parsowania lub hardcoded listę)
        library_models = fetch_ollama_library_models()
        
        # Wzbogać informacje o dostępność lokalną
        for model in library_models:
            model_name = model.get('name', '')
            model['is_local'] = any(local_name.startswith(model_name) for local_name in local_models)
            model['local_variants'] = [name for name in local_models if name.startswith(model_name)]
            
            # Dodaj informacje o możliwości pobrania
            model['can_pull'] = True  # Wszystkie modele z biblioteki można pobrać
            model['pull_command'] = f"ollama pull {model_name}"
        
        return library_models
        
    except Exception as e:
        print(f"❌ Błąd podczas pobierania rozszerzonych informacji: {e}")
        return []

def interactive_model_pull():
    """
    Interaktywne pobieranie modeli z biblioteki Ollama
    """
    print("\n📥 INTERAKTYWNE POBIERANIE MODELI")
    
    # Sprawdź API
    api_info = fetch_ollama_api_info()
    if api_info.get('status') != 'active':
        print("❌ API Ollama niedostępne - nie można pobierać modeli")
        return
    
    # Pobierz listę modeli z biblioteki
    library_models = fetch_ollama_library_models_enhanced()
    
    if not library_models:
        print("❌ Nie udało się pobrać listy modeli z biblioteki")
        return
    
    # Pokaż dostępne modele
    available_models = [m for m in library_models if not m.get('is_local', False)]
    
    if not available_models:
        print("✅ Wszystkie modele z biblioteki są już dostępne lokalnie!")
        return
    
    print(f"\n📚 DOSTĘPNE DO POBRANIA ({len(available_models)} modeli):")
    for i, model in enumerate(available_models[:20], 1):  # Pokaż pierwsze 20
        name = model.get('name', 'N/A')
        description = model.get('description', 'N/A')[:50] + '...'
        sizes = model.get('available_sizes', [])
        sizes_str = f" [{', '.join(sizes[:3])}]" if sizes else ""
        print(f"{i:2d}. {name:20s} | {description}{sizes_str}")
    
    if len(available_models) > 20:
        print(f"    ... i {len(available_models) - 20} więcej")
    
    try:
        choice = input(f"\nWybierz numer modelu do pobrania (1-{min(20, len(available_models))}) lub 'q' aby wyjść: ").strip()
        
        if choice.lower() == 'q':
            return
        
        model_idx = int(choice) - 1
        if 0 <= model_idx < min(20, len(available_models)):
            selected_model = available_models[model_idx]
            model_name = selected_model.get('name')
            
            # Sprawdź czy model ma różne rozmiary
            sizes = selected_model.get('available_sizes', [])
            if sizes:
                print(f"\nDostępne rozmiary dla {model_name}:")
                for i, size in enumerate(sizes, 1):
                    print(f"{i}. {model_name}:{size}")
                
                size_choice = input(f"Wybierz rozmiar (1-{len(sizes)}) lub Enter dla domyślnego: ").strip()
                if size_choice and size_choice.isdigit():
                    size_idx = int(size_choice) - 1
                    if 0 <= size_idx < len(sizes):
                        model_name = f"{model_name}:{sizes[size_idx]}"
            
            # Pobierz model
            print(f"\n🚀 Rozpoczynanie pobierania: {model_name}")
            success = pull_model_via_api(model_name, show_progress=True)
            
            if success:
                print(f"✅ Model {model_name} został pobrany pomyślnie!")
                print(f"💡 Możesz go teraz używać: ollama run {model_name}")
            else:
                print(f"❌ Nie udało się pobrać modelu {model_name}")
        else:
            print("❌ Nieprawidłowy numer modelu")
            
    except ValueError:
        print("❌ Wprowadź prawidłowy numer")
    except KeyboardInterrupt:
        print("\n⏹️ Przerwano przez użytkownika")

def fetch_ollama_library_models():
    """
    Pobiera listę modeli z biblioteki Ollama (ollama.com/library)
    Używa Beautiful Soup do lepszego parsowania HTML
    
    Returns:
        Lista słowników z informacjami o modelach z biblioteki
    """
    try:
        import requests
        from datetime import datetime
        
        print("🌐 POBIERANIE LISTY MODELI Z OLLAMA.COM/LIBRARY...")
        
        url = "https://ollama.com/library"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        models = []
        
        try:
            # Spróbuj użyć Beautiful Soup jeśli dostępne
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Szukaj linków do modeli
            model_links = soup.find_all('a', href=lambda x: x and '/library/' in x)
            
            for link in model_links:
                href = link.get('href', '')
                if '/library/' in href:
                    # Wyciągnij nazwę modelu
                    model_name = href.split('/library/')[-1].strip('/')
                    if model_name and model_name not in [m.get('name') for m in models]:
                        
                        # Szukaj dodatkowych informacji w kontekście linku
                        parent = link.find_parent()
                        text_content = parent.get_text() if parent else link.get_text()
                        
                        model_info = {
                            'name': model_name,
                            'description': f'Model {model_name} z biblioteki Ollama',
                            'capabilities': [],
                            'available_sizes': [],
                            'pulls_count': 0,
                            'pulls_formatted': 'N/A',
                            'tags_count': 0,
                            'last_updated': 'N/A',
                            'library_url': f"https://ollama.com/library/{model_name}",
                            'fetched_at': datetime.now().isoformat()
                        }
                        
                        # Analiza tekstu dla dodatkowych informacji
                        if text_content:
                            text_lower = text_content.lower()
                            
                            # Możliwości
                            if 'vision' in text_lower:
                                model_info['capabilities'].append('vision')
                            if 'tools' in text_lower or 'function' in text_lower:
                                model_info['capabilities'].append('tools')
                            if 'embed' in text_lower:
                                model_info['capabilities'].append('embedding')
                            if 'code' in text_lower or 'coding' in text_lower:
                                model_info['capabilities'].append('coding')
                            
                            # Rozmiary modeli
                            import re
                            size_pattern = r'\b(\d+(?:\.\d+)?[bmk])\b'
                            sizes = re.findall(size_pattern, text_lower)
                            if sizes:
                                model_info['available_sizes'] = list(set(sizes))
                            
                            # Liczba pobrań
                            pulls_pattern = r'([\d.]+[kmb]?\s+pulls?)'
                            pulls_match = re.search(pulls_pattern, text_lower)
                            if pulls_match:
                                model_info['pulls_formatted'] = pulls_match.group(1)
                        
                        models.append(model_info)
            
            print(f"✅ Beautiful Soup: Pobrano {len(models)} modeli")
            
        except ImportError:
            print("📋 Beautiful Soup niedostępne, używanie prostego parsowania...")
            # Fallback do prostego parsowania regex
            import re
            pattern = r'href="[^"]*?/library/([^"/]+)"'
            model_names = list(set(re.findall(pattern, response.text)))
            
            for name in model_names:
                models.append({
                    'name': name,
                    'description': f'Model {name} z biblioteki Ollama',
                    'capabilities': [],
                    'available_sizes': [],
                    'pulls_count': 0,
                    'pulls_formatted': 'N/A',
                    'tags_count': 0,
                    'last_updated': 'N/A',
                    'library_url': f"https://ollama.com/library/{name}",
                    'fetched_at': datetime.now().isoformat()
                })
            
            print(f"✅ Regex parsing: Pobrano {len(models)} modeli")
        
        # Jeśli nadal brak modeli, użyj listy popularnych
        if not models:
            print("🔄 Używanie listy popularnych modeli...")
            popular_models = [
                'llama3.2', 'gemma2', 'qwen2.5', 'qwen2.5-coder', 'mistral', 'phi3', 
                'codellama', 'llama3.1', 'llama2', 'mixtral', 'gemma', 'qwen2',
                'deepseek-coder', 'starcoder2', 'tinyllama', 'vicuna', 'orca-mini',
                'dolphin-mistral', 'wizardcoder', 'nous-hermes2', 'openchat',
                'neural-chat', 'starling-lm', 'solar', 'yarn-llama2', 'falcon',
                'llama3:8b', 'llama3:70b', 'gemma2:2b', 'gemma2:9b', 'gemma2:27b'
            ]
            
            for name in popular_models:
                models.append({
                    'name': name,
                    'description': f'Popularny model {name} z biblioteki Ollama',
                    'capabilities': [],
                    'available_sizes': [],
                    'pulls_count': 0,
                    'pulls_formatted': 'N/A',
                    'tags_count': 0,
                    'last_updated': 'N/A',
                    'library_url': f"https://ollama.com/library/{name.split(':')[0]}",
                    'fetched_at': datetime.now().isoformat()
                })
        
        return models
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd połączenia z ollama.com: {e}")
        return []
    except Exception as e:
        print(f"❌ Błąd podczas pobierania listy modeli: {e}")
        return []

def display_library_models(library_models, show_details=False):
    """
    Wyświetla modele z biblioteki Ollama w czytelnym formacie
    
    Args:
        library_models: Lista modeli z biblioteki
        show_details: Czy pokazać szczegółowe informacje
    """
    if not library_models:
        print("❌ Brak modeli do wyświetlenia")
        return
    
    print(f"\n📚 MODELE Z BIBLIOTEKI OLLAMA ({len(library_models)}):")
    print("=" * 80)
    
    # Sortuj według popularności (liczba pobrań)
    sorted_models = sorted(library_models, key=lambda x: x.get('pulls_count', 0), reverse=True)
    
    for i, model in enumerate(sorted_models, 1):
        name = model.get('name', 'N/A')
        description = model.get('description', 'N/A')
        capabilities = model.get('capabilities', [])
        sizes = model.get('available_sizes', [])
        pulls = model.get('pulls_formatted', 'N/A')
        tags = model.get('tags_count', 0)
        updated = model.get('last_updated', 'N/A')
        
        print(f"\n{i:3d}. 🏷️ {name}")
        
        if show_details:
            print(f"     📝 {description}")
            if capabilities:
                print(f"     ✨ Możliwości: {', '.join(capabilities)}")
            if sizes:
                print(f"     📏 Rozmiary: {', '.join(sizes[:5])}{'...' if len(sizes) > 5 else ''}")
            print(f"     📊 Pobrania: {pulls} | Tags: {tags} | Aktualizacja: {updated}")
            print(f"     🔗 {model.get('library_url', 'N/A')}")
        else:
            # Kompaktowy format
            capabilities_str = f" ({', '.join(capabilities[:2])})" if capabilities else ""
            sizes_str = f" [{', '.join(sizes[:3])}]" if sizes else ""
            print(f"     📊 {pulls} | {description[:60]}{'...' if len(description) > 60 else ''}{capabilities_str}{sizes_str}")

def compare_local_vs_library_models():
    """
    Porównuje modele lokalne (z Ollama API) z modelami dostępnymi w bibliotece
    """
    print("🔄 PORÓWNANIE MODELI LOKALNYCH Z BIBLIOTEKĄ OLLAMA...")
    
    # Pobierz modele lokalne
    local_models = get_enhanced_model_metadata_cached()
    local_names = {model.get('name', '').split(':')[0] for model in local_models} if local_models else set()
    
    # Pobierz modele z biblioteki
    library_models = fetch_ollama_library_models()
    library_names = {model.get('name', '') for model in library_models}
    
    if not local_models and not library_models:
        print("❌ Nie udało się pobrać żadnych danych")
        return
    
    print(f"\n📊 STATYSTYKI:")
    print(f"   🏠 Modele lokalne: {len(local_models) if local_models else 0}")
    print(f"   📚 Modele w bibliotece: {len(library_models)}")
    
    if local_names and library_names:
        # Znajdź modele wspólne
        common = local_names.intersection(library_names)
        # Modele tylko lokalne
        only_local = local_names - library_names
        # Modele tylko w bibliotece
        only_library = library_names - local_names
        
        print(f"   🤝 Wspólne: {len(common)}")
        print(f"   🏠 Tylko lokalne: {len(only_local)}")
        print(f"   📚 Dostępne do pobrania: {len(only_library)}")
        
        if common:
            print(f"\n✅ WSPÓLNE MODELE ({len(common)}):")
            for name in sorted(common):
                print(f"   • {name}")
        
        if only_local:
            print(f"\n🏠 TYLKO LOKALNE ({len(only_local)}):")
            for name in sorted(only_local):
                print(f"   • {name}")
        
        if only_library and len(only_library) <= 20:
            print(f"\n📚 POPULARNE DOSTĘPNE DO POBRANIA ({min(20, len(only_library))}):")
            # Pokaż najpopularniejsze
            available_models = [m for m in library_models if m.get('name') in only_library]
            available_models.sort(key=lambda x: x.get('pulls_count', 0), reverse=True)
            for model in available_models[:20]:
                name = model.get('name')
                pulls = model.get('pulls_formatted', 'N/A')
                sizes = model.get('available_sizes', [])
                sizes_str = f" [{', '.join(sizes[:3])}]" if sizes else ""
                print(f"   • {name:20s} | {pulls:>10s}{sizes_str}")

def main():
    parser = argparse.ArgumentParser(
        description="Filtrowanie modeli Ollama o podobnych parametrach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python filter_models.py                                    # Filtruj z API, model ref: gemma2:2b
  python filter_models.py qwen3:1.7b                        # Filtruj z API, model ref: qwen3:1.7b
  python filter_models.py gemma2:2b exports/models.csv     # Filtruj z CSV, model ref: gemma2:2b
  python filter_models.py --list-models                     # Pokaż dostępne modele lokalne
  python filter_models.py --api-info                        # Info o API Ollama i lokalnych modelach
  python filter_models.py --api-detailed                    # Szczegółowe parametry lokalnych modeli z API
  python filter_models.py --find-similar-api gemma2:2b      # Znajdź podobne modele używając TYLKO API
  python filter_models.py --fetch-library                   # Pobierz listę z biblioteki Ollama
  python filter_models.py --detailed-params                 # Pobierz szczegółowe parametry ze stron WWW
  python filter_models.py --find-similar-detailed gemma2:2b # Znajdź podobne modele używając danych ze stron
  python filter_models.py --compare-library                 # Porównaj lokalne z biblioteką
  python filter_models.py --pull llama3.2:1b               # Pobierz konkretny model z biblioteki
  python filter_models.py --interactive-pull                # Interaktywny wybór i pobieranie modeli
        """
    )
    
    parser.add_argument(
        "reference_model", 
        nargs="?",
        default="gemma2:2b",
        help="Model referencyjny (domyślnie: gemma2:2b)"
    )
    
    parser.add_argument(
        "csv_file",
        nargs="?",
        help="Ścieżka do pliku CSV z metadanymi (opcjonalne, domyślnie pobiera z API)"
    )
    
    parser.add_argument(
        "--export",
        action="store_true",
        help="Eksportuj wyniki do plików JSON i CSV"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Wyświetl listę dostępnych modeli"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Szczegółowe informacje"
    )
    
    parser.add_argument(
        "--fetch-library",
        action="store_true",
        help="Pobierz listę modeli z biblioteki Ollama (ollama.com/library)"
    )
    
    parser.add_argument(
        "--compare-library",
        action="store_true", 
        help="Porównaj lokalne modele z biblioteką Ollama"
    )
    
    parser.add_argument(
        "--library-details",
        action="store_true",
        help="Pokaż szczegółowe informacje o modelach z biblioteki"
    )
    
    parser.add_argument(
        "--api-info",
        action="store_true",
        help="Pokaż informacje o API Ollama i lokalnych modelach"
    )
    
    parser.add_argument(
        "--pull",
        type=str,
        help="Pobierz model z biblioteki (np. --pull llama3.2:1b)"
    )
    
    parser.add_argument(
        "--interactive-pull",
        action="store_true",
        help="Interaktywny wybór i pobieranie modeli z biblioteki"
    )
    
    parser.add_argument(
        "--detailed-params",
        action="store_true",
        help="Pobierz szczegółowe parametry modeli z ich dedykowanych stron"
    )
    
    parser.add_argument(
        "--find-similar-detailed",
        type=str,
        help="Znajdź modele podobne używając szczegółowych parametrów (np. --find-similar-detailed gemma2:2b)"
    )
    
    parser.add_argument(
        "--api-detailed",
        action="store_true",
        help="Pokaż szczegółowe parametry wszystkich modeli lokalnych z API"
    )
    
    parser.add_argument(
        "--find-similar-api",
        type=str,
        help="Znajdź podobne modele używając TYLKO API Ollama (np. --find-similar-api gemma2:2b)"
    )
    
    args = parser.parse_args()
    
    if args.api_info:
        api_info = fetch_ollama_api_info()
        print(f"\n🔧 INFORMACJE O API OLLAMA:")
        print(f"   Status: {api_info.get('status', 'N/A')}")
        if api_info.get('status') == 'active':
            print(f"   Modele lokalne: {api_info.get('local_models_count', 0)}")
            print(f"   Modele uruchomione: {api_info.get('running_models_count', 0)}")
            if api_info.get('local_models'):
                print(f"   Dostępne lokalnie: {', '.join(api_info['local_models'][:5])}{'...' if len(api_info['local_models']) > 5 else ''}")
            if api_info.get('running_models'):
                print(f"   Obecnie uruchomione: {', '.join(api_info['running_models'])}")
        return
    
    if args.pull:
        success = pull_model_via_api(args.pull, show_progress=True)
        if success:
            print(f"✅ Model {args.pull} został pobrany pomyślnie!")
        else:
            print(f"❌ Nie udało się pobrać modelu {args.pull}")
        return
    
    if args.interactive_pull:
        interactive_model_pull()
        return
    
    if args.api_detailed:
        enhanced_models = fetch_enhanced_models_from_api()
        if enhanced_models:
            print(f"\n📊 SZCZEGÓŁOWE PARAMETRY Z API ({len(enhanced_models)} modeli):")
            print("=" * 120)
            
            for i, model in enumerate(enhanced_models, 1):
                name = model.get('name', 'N/A')
                params = model.get('parameter_count_formatted', model.get('parameter_size', 'N/A'))
                size = f"{model.get('size_gb', 0):.2f}GB"
                context = model.get('context_length_formatted', 'N/A')
                family = model.get('family', 'N/A')
                quant = model.get('quantization_level', 'N/A')
                caps = ', '.join(model.get('all_capabilities', [])[:3])
                
                print(f"{i:2d}. {name:25s} | {params:>8s} | {size:>8s} | {context:>6s} | {family:>10s} | {quant:>6s} | {caps}")
        else:
            print("❌ Nie udało się pobrać szczegółowych danych z API")
        return
    
    if args.find_similar_api:
        similar_models = find_similar_models_api_only(
            args.find_similar_api,
            param_tolerance=1.5,
            size_tolerance=1.0
        )
        
        if similar_models:
            print(f"\n✅ ZNALEZIONO {len(similar_models)} PODOBNYCH MODELI (API):")
            print("=" * 100)
            
            for i, model in enumerate(similar_models, 1):
                name = model.get('name', 'N/A')
                score = model.get('similarity_score', 0)
                details = model.get('similarity_details', [])
                params = model.get('parameter_count_formatted', 'N/A')
                size = f"{model.get('size_gb', 0):.2f}GB"
                family = model.get('family', 'N/A')
                
                print(f"\n{i:2d}. 🏷️ {name}")
                print(f"    📊 Wynik podobieństwa: {score:.1f}/10")
                print(f"    📈 {params} | {size} | {family}")
                
                if details:
                    print(f"    ✨ Podobieństwa:")
                    for detail in details:
                        print(f"       • {detail}")
                
                # Sprawdź czy można uruchomić
                capabilities = model.get('capabilities', [])
                if 'completion' in capabilities:
                    print(f"    💡 Uruchom: ollama run {name}")
        else:
            print(f"❌ Nie znaleziono modeli podobnych do {args.find_similar_api}")
        
        return
    
    if args.detailed_params:
        all_variants = fetch_all_models_with_detailed_params()
        if all_variants:
            print(f"\n📊 SZCZEGÓŁOWE PARAMETRY MODELI ({len(all_variants)} wariantów):")
            print("=" * 100)
            
            for i, variant in enumerate(all_variants, 1):
                name = variant.get('name', 'N/A')
                params = variant.get('parameter_size', 'N/A')
                size = variant.get('size_gb', 'N/A')
                context = variant.get('context_length', 'N/A')
                capabilities = variant.get('capabilities', [])
                
                size_str = f"{size:.1f}GB" if isinstance(size, (int, float)) else str(size)
                context_str = f"{context:,}" if isinstance(context, int) else str(context)
                caps_str = f" [{', '.join(capabilities)}]" if capabilities else ""
                
                print(f"{i:3d}. {name:25s} | {params:>6s} | {size_str:>8s} | {context_str:>8s}{caps_str}")
        else:
            print("❌ Nie udało się pobrać szczegółowych parametrów")
        return
    
    if args.find_similar_detailed:
        print(f"🔍 WYSZUKIWANIE MODELI PODOBNYCH DO: {args.find_similar_detailed}")
        
        # Pobierz szczegółowe dane
        all_variants = fetch_all_models_with_detailed_params()
        
        if not all_variants:
            print("❌ Nie udało się pobrać szczegółowych danych")
            return
        
        # Znajdź podobne modele
        similar_models = find_similar_models_by_params(
            args.find_similar_detailed, 
            all_variants,
            param_tolerance=1.5,  # 50% tolerancja parametrów
            size_tolerance=1.0    # 1GB tolerancja rozmiaru
        )
        
        if similar_models:
            print(f"\n✅ ZNALEZIONO {len(similar_models)} PODOBNYCH MODELI:")
            print("=" * 100)
            
            for i, model in enumerate(similar_models, 1):
                name = model.get('name', 'N/A')
                score = model.get('similarity_score', 0)
                details = model.get('similarity_details', [])
                params = model.get('parameter_size', 'N/A')
                size = model.get('size_gb', 'N/A')
                
                size_str = f"{size:.1f}GB" if isinstance(size, (int, float)) else str(size)
                
                print(f"\n{i:2d}. 🏷️ {name}")
                print(f"    📊 Wynik podobieństwa: {score:.1f}/10")
                print(f"    📈 Parametry: {params} | Rozmiar: {size_str}")
                
                if details:
                    print(f"    ✨ Podobieństwa:")
                    for detail in details:
                        print(f"       • {detail}")
                
                # Pokaż komendę do pobrania
                model_url = model.get('model_url', '')
                if model_url:
                    print(f"    💡 Pobierz: ollama pull {name}")
        else:
            print(f"❌ Nie znaleziono modeli podobnych do {args.find_similar_detailed}")
        
        return
    
    if args.list_models:
        print("📋 POBIERANIE LISTY MODELI...")
        enhanced_data = get_enhanced_model_metadata_cached()
        if enhanced_data:
            print(f"\n📊 DOSTĘPNE MODELE ({len(enhanced_data)}):")
            for i, model in enumerate(enhanced_data, 1):
                size_gb = model.get('size_gb', 'N/A')
                params = model.get('parameter_size', 'N/A')
                size_str = f"{size_gb:.2f}" if isinstance(size_gb, (int, float)) else str(size_gb)
                params_str = str(params)
                print(f"{i:2d}. {model.get('name', 'N/A'):20s} | {size_str:>6s} GB | {params_str:>6s}")
        else:
            print("❌ Nie udało się pobrać listy modeli")
        return
    
    if args.fetch_library:
        # Użyj ulepszonej funkcji która łączy API z biblioteką
        library_models = fetch_ollama_library_models_enhanced()
        if library_models:
            display_library_models(library_models, show_details=args.library_details)
            
            # Pokaż dodatkowe informacje o dostępności lokalnej
            local_count = sum(1 for m in library_models if m.get('is_local', False))
            available_count = len(library_models) - local_count
            print(f"\n📊 PODSUMOWANIE:")
            print(f"   🏠 Dostępne lokalnie: {local_count}")
            print(f"   📥 Do pobrania: {available_count}")
            
            if available_count > 0:
                print(f"   💡 Użyj --interactive-pull aby pobrać modele interaktywnie")
                print(f"   💡 Lub --pull <nazwa_modelu> aby pobrać konkretny model")
        else:
            print("❌ Nie udało się pobrać modeli z biblioteki")
        return
    
    if args.compare_library:
        compare_local_vs_library_models()
        return
    
    print(f"🎯 MODEL REFERENCYJNY: {args.reference_model}")
    
    if args.csv_file:
        # Filtrowanie z pliku CSV
        csv_path = Path(args.csv_file)
        if not csv_path.exists():
            print(f"❌ Plik CSV nie istnieje: {csv_path}")
            return
        
        print(f"📁 FILTROWANIE Z PLIKU CSV: {csv_path}")
        similar_models = filter_similar_models_from_csv(
            str(csv_path), 
            args.reference_model, 
            export_results=args.export
        )
    else:
        # Filtrowanie z API
        print("🔄 POBIERANIE DANYCH Z API OLLAMA...")
        enhanced_data = get_enhanced_model_metadata_cached()
        if not enhanced_data:
            print("❌ Nie udało się pobrać danych z API")
            return
        
        similar_models = filter_similar_models(enhanced_data, args.reference_model)
        
        if args.export and similar_models:
            # Eksport dla danych z API
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            import json
            json_filename = f"filtered_models_similar_to_{args.reference_model.replace(':', '_')}_{timestamp}.json"
            json_path = export_dir / json_filename
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(similar_models, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Wyniki wyeksportowane do: {json_path}")
    
    if args.verbose and similar_models:
        print(f"\n📈 SZCZEGÓŁOWE STATYSTYKI:")
        sizes = [m.get('size_gb', 0) for m in similar_models if m.get('size_gb')]
        if sizes:
            print(f"   Rozmiary: {min(sizes):.2f} - {max(sizes):.2f} GB (średnia: {sum(sizes)/len(sizes):.2f} GB)")
        
        similarities = [m.get('similarity_score', 0) for m in similar_models]
        if similarities:
            print(f"   Wyniki podobieństwa: {min(similarities)} - {max(similarities)}/4")
    
    print(f"\n✅ Znaleziono {len(similar_models)} podobnych modeli")

def fetch_model_details_from_page(model_name):
    """
    Pobiera szczegółowe parametry modelu z jego dedykowanej strony Ollama
    
    Args:
        model_name: Nazwa modelu (np. 'gemma2', 'llama3.2')
        
    Returns:
        Lista wariantów modelu z parametrami
    """
    try:
        import requests
        import re
        from datetime import datetime
        
        base_name = model_name.split(':')[0]  # Usuń tag jeśli jest
        url = f"https://ollama.com/library/{base_name}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"  📄 Pobieranie szczegółów dla {base_name}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        variants = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Szukaj tabeli z modelami
            tables = soup.find_all('table') or []
            model_table = None
            
            for table in tables:
                # Sprawdź czy tabela zawiera kolumny Name, Size, Context, Input
                headers_row = table.find('tr')
                if headers_row:
                    headers_text = headers_row.get_text().lower()
                    if 'name' in headers_text and 'size' in headers_text:
                        model_table = table
                        break
            
            if model_table:
                rows = model_table.find_all('tr')[1:]  # Pomiń nagłówek
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # Wyciągnij dane z komórek
                        name_cell = cells[0]
                        size_cell = cells[1] if len(cells) > 1 else None
                        context_cell = cells[2] if len(cells) > 2 else None
                        input_cell = cells[3] if len(cells) > 3 else None
                        
                        # Nazwa modelu i link
                        model_link = name_cell.find('a')
                        if model_link:
                            full_name = model_link.get_text().strip()
                            model_url = model_link.get('href', '')
                            if model_url.startswith('/'):
                                model_url = f"https://ollama.com{model_url}"
                        else:
                            full_name = name_cell.get_text().strip()
                            model_url = url
                        
                        # Rozmiar
                        size_text = size_cell.get_text().strip() if size_cell else 'N/A'
                        
                        # Context length
                        context_text = context_cell.get_text().strip() if context_cell else 'N/A'
                        
                        # Typ wejścia
                        input_text = input_cell.get_text().strip() if input_cell else 'Text'
                        
                        # Wyciągnij liczbę parametrów z nazwy modelu
                        param_match = re.search(r'(\d+(?:\.\d+)?)[bmk]?(?=\s|:|$)', full_name.lower())
                        parameter_size = param_match.group(1) if param_match else 'Unknown'
                        
                        # Konwertuj rozmiar na GB
                        size_gb = 'Unknown'
                        if size_text and size_text.lower() != 'n/a':
                            size_match = re.search(r'([\d.]+)\s*(gb|mb|kb)?', size_text.lower())
                            if size_match:
                                size_num = float(size_match.group(1))
                                unit = size_match.group(2) or 'gb'
                                if unit == 'mb':
                                    size_gb = size_num / 1000
                                elif unit == 'kb':
                                    size_gb = size_num / 1000000
                                else:
                                    size_gb = size_num
                        
                        # Konwertuj context na liczbę
                        context_length = 'Unknown'
                        if context_text and context_text.lower() != 'n/a':
                            context_match = re.search(r'(\d+)\s*k?', context_text.lower())
                            if context_match:
                                context_num = int(context_match.group(1))
                                if 'k' in context_text.lower():
                                    context_length = context_num * 1000
                                else:
                                    context_length = context_num
                        
                        # Możliwości z typu wejścia i nazwy
                        capabilities = []
                        if 'vision' in full_name.lower() or 'vision' in input_text.lower():
                            capabilities.append('vision')
                        if 'code' in full_name.lower():
                            capabilities.append('coding')
                        if 'embed' in full_name.lower():
                            capabilities.append('embedding')
                        if 'tools' in input_text.lower() or 'function' in input_text.lower():
                            capabilities.append('tools')
                        
                        variant = {
                            'name': full_name,
                            'base_model': base_name,
                            'parameter_size': parameter_size,
                            'size_gb': size_gb,
                            'context_length': context_length,
                            'input_type': input_text,
                            'capabilities': capabilities,
                            'model_url': model_url,
                            'raw_size': size_text,
                            'raw_context': context_text,
                            'fetched_at': datetime.now().isoformat(),
                            'source': 'ollama_page_table'
                        }
                        
                        variants.append(variant)
                
                print(f"    ✅ Znaleziono {len(variants)} wariantów dla {base_name}")
            else:
                print(f"    ⚠️ Nie znaleziono tabeli z modelami dla {base_name}")
                
        except ImportError:
            # Fallback bez Beautiful Soup - użyj regex
            print(f"    📋 Beautiful Soup niedostępne, używanie regex dla {base_name}")
            
            # Szukaj wzorców tabel w HTML
            table_pattern = r'<tr[^>]*>.*?<td[^>]*>.*?([^<]+(?::\w+)?)</a>.*?</td>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>'
            matches = re.findall(table_pattern, response.text, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                if len(match) >= 3:
                    full_name = match[0].strip()
                    size_text = match[1].strip()
                    context_text = match[2].strip()
                    input_text = match[3].strip() if len(match) > 3 else 'Text'
                    
                    # Parsowanie podobne jak wyżej
                    param_match = re.search(r'(\d+(?:\.\d+)?)[bmk]?(?=\s|:|$)', full_name.lower())
                    parameter_size = param_match.group(1) if param_match else 'Unknown'
                    
                    variant = {
                        'name': full_name,
                        'base_model': base_name,
                        'parameter_size': parameter_size,
                        'size_gb': 'Unknown',
                        'context_length': 'Unknown',
                        'input_type': input_text,
                        'capabilities': [],
                        'model_url': url,
                        'raw_size': size_text,
                        'raw_context': context_text,
                        'fetched_at': datetime.now().isoformat(),
                        'source': 'ollama_page_regex'
                    }
                    
                    variants.append(variant)
        
        return variants
        
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Błąd pobierania strony {base_name}: {e}")
        return []
    except Exception as e:
        print(f"    ❌ Błąd parsowania strony {base_name}: {e}")
        return []

def fetch_all_models_with_detailed_params():
    """
    Pobiera szczegółowe parametry dla wszystkich modeli z biblioteki Ollama
    
    Returns:
        Lista wszystkich wariantów modeli z dokładnymi parametrami
    """
    print("🔍 POBIERANIE SZCZEGÓŁOWYCH PARAMETRÓW MODELI...")
    
    # Najpierw pobierz listę wszystkich modeli
    base_models = fetch_ollama_library_models()
    
    if not base_models:
        print("❌ Nie udało się pobrać listy modeli")
        return []
    
    all_variants = []
    model_names = [model.get('name', '') for model in base_models[:20]]  # Limit dla testów
    
    print(f"📊 Pobieranie szczegółów dla {len(model_names)} modeli...")
    
    for i, model_name in enumerate(model_names, 1):
        print(f"[{i}/{len(model_names)}] {model_name}")
        
        variants = fetch_model_details_from_page(model_name)
        
        if variants:
            all_variants.extend(variants)
        else:
            # Jeśli nie udało się pobrać ze strony, użyj podstawowych danych
            fallback_variant = {
                'name': model_name,
                'base_model': model_name,
                'parameter_size': 'Unknown',
                'size_gb': 'Unknown',
                'context_length': 'Unknown',
                'input_type': 'Text',
                'capabilities': [],
                'model_url': f"https://ollama.com/library/{model_name}",
                'source': 'fallback'
            }
            all_variants.append(fallback_variant)
        
        # Małe opóźnienie żeby nie przeciążać serwera
        import time
        time.sleep(0.5)
    
    print(f"✅ Pobrano szczegółowe dane dla {len(all_variants)} wariantów modeli")
    return all_variants

def find_similar_models_by_params(reference_model="gemma2:2b", all_variants=None, param_tolerance=0.5, size_tolerance=1.0):
    """
    Znajduje modele podobne do referencyjnego na podstawie szczegółowych parametrów
    
    Args:
        reference_model: Model referencyjny (np. "gemma2:2b")
        all_variants: Lista wszystkich wariantów modeli (jeśli None, pobierze automatycznie)
        param_tolerance: Tolerancja dla liczby parametrów (wielokrotność)
        size_tolerance: Tolerancja dla rozmiaru w GB
        
    Returns:
        Lista podobnych modeli posortowana według podobieństwa
    """
    if all_variants is None:
        all_variants = fetch_all_models_with_detailed_params()
    
    if not all_variants:
        print("❌ Brak danych o modelach")
        return []
    
    # Znajdź model referencyjny
    reference = None
    for variant in all_variants:
        if variant.get('name', '').lower() == reference_model.lower():
            reference = variant
            break
    
    if not reference:
        print(f"❌ Nie znaleziono modelu referencyjnego: {reference_model}")
        return []
    
    print(f"🎯 MODEL REFERENCYJNY: {reference_model}")
    print(f"   📊 Parametry: {reference.get('parameter_size', 'N/A')}")
    print(f"   💾 Rozmiar: {reference.get('size_gb', 'N/A')} GB")
    print(f"   📝 Kontekst: {reference.get('context_length', 'N/A')}")
    print(f"   ✨ Możliwości: {', '.join(reference.get('capabilities', []))}")
    
    # Pobierz parametry referencyjne
    ref_params = reference.get('parameter_size', 'Unknown')
    ref_size = reference.get('size_gb', 'Unknown')
    ref_context = reference.get('context_length', 'Unknown')
    ref_capabilities = set(reference.get('capabilities', []))
    
    similar_models = []
    
    for variant in all_variants:
        if variant.get('name', '').lower() == reference_model.lower():
            continue  # Pomiń model referencyjny
        
        similarity_score = 0
        similarity_details = []
        
        # Porównaj liczbę parametrów
        variant_params = variant.get('parameter_size', 'Unknown')
        if ref_params != 'Unknown' and variant_params != 'Unknown':
            try:
                ref_p = float(ref_params)
                var_p = float(variant_params)
                
                param_ratio = max(ref_p, var_p) / min(ref_p, var_p)
                if param_ratio <= param_tolerance:
                    similarity_score += 3
                    similarity_details.append(f"Parametry: {variant_params} (~{ref_params})")
                elif param_ratio <= param_tolerance * 2:
                    similarity_score += 1
                    similarity_details.append(f"Parametry: {variant_params} (podobne do {ref_params})")
            except (ValueError, ZeroDivisionError):
                pass
        
        # Porównaj rozmiar
        variant_size = variant.get('size_gb', 'Unknown')
        if ref_size != 'Unknown' and variant_size != 'Unknown':
            try:
                ref_s = float(ref_size)
                var_s = float(variant_size)
                
                size_diff = abs(ref_s - var_s)
                if size_diff <= size_tolerance:
                    similarity_score += 2
                    similarity_details.append(f"Rozmiar: {variant_size:.1f}GB (~{ref_size:.1f}GB)")
                elif size_diff <= size_tolerance * 2:
                    similarity_score += 1
                    similarity_details.append(f"Rozmiar: {variant_size:.1f}GB (podobny do {ref_size:.1f}GB)")
            except (ValueError, TypeError):
                pass
        
        # Porównaj długość kontekstu
        variant_context = variant.get('context_length', 'Unknown')
        if ref_context != 'Unknown' and variant_context != 'Unknown':
            try:
                ref_c = int(ref_context)
                var_c = int(variant_context)
                
                if ref_c == var_c:
                    similarity_score += 1
                    similarity_details.append(f"Kontekst: {variant_context} (={ref_context})")
                elif abs(ref_c - var_c) <= ref_c * 0.5:  # 50% tolerancja
                    similarity_score += 0.5
                    similarity_details.append(f"Kontekst: {variant_context} (~{ref_context})")
            except (ValueError, TypeError):
                pass
        
        # Porównaj możliwości
        variant_capabilities = set(variant.get('capabilities', []))
        common_capabilities = ref_capabilities.intersection(variant_capabilities)
        if common_capabilities:
            similarity_score += len(common_capabilities) * 0.5
            similarity_details.append(f"Możliwości: {', '.join(common_capabilities)}")
        
        # Dodaj do listy jeśli podobny
        if similarity_score >= 1.0:  # Minimum 1 punkt podobieństwa
            variant_copy = variant.copy()
            variant_copy['similarity_score'] = similarity_score
            variant_copy['similarity_details'] = similarity_details
            similar_models.append(variant_copy)
    
    # Sortuj według podobieństwa
    similar_models.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
    
    return similar_models

def fetch_enhanced_models_from_api():
    """
    Pobiera szczegółowe parametry wszystkich modeli lokalnych używając TYLKO API Ollama
    
    Returns:
        Lista modeli z pełnymi parametrami z API
    """
    try:
        import requests
        
        print("🔧 POBIERANIE SZCZEGÓŁOWYCH DANYCH Z API OLLAMA...")
        
        # Sprawdź czy Ollama działa
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        response.raise_for_status()
        
        models_data = response.json().get('models', [])
        
        if not models_data:
            print("❌ Brak modeli lokalnych")
            return []
        
        enhanced_models = []
        
        print(f"📊 Przetwarzanie {len(models_data)} modeli lokalnych...")
        
        for i, model in enumerate(models_data, 1):
            model_name = model.get('name', 'Unknown')
            print(f"  [{i}/{len(models_data)}] {model_name}")
            
            # Podstawowe dane z /api/tags
            base_data = {
                'name': model_name,
                'size_bytes': model.get('size', 0),
                'size_gb': model.get('size', 0) / (1024**3) if model.get('size') else 0,
                'modified_at': model.get('modified_at', ''),
                'digest': model.get('digest', ''),
                'source': 'ollama_api'
            }
            
            # Szczegóły z sekcji details
            details = model.get('details', {})
            base_data.update({
                'format': details.get('format', 'unknown'),
                'family': details.get('family', 'unknown'),
                'families': details.get('families', []),
                'parameter_size': details.get('parameter_size', 'Unknown'),
                'quantization_level': details.get('quantization_level', 'unknown')
            })
            
            # Pobierz dodatkowe szczegóły z /api/show
            try:
                show_response = requests.post(
                    "http://localhost:11434/api/show",
                    json={"model": model_name},
                    timeout=15
                )
                
                if show_response.ok:
                    show_data = show_response.json()
                    
                    # model_info zawiera szczegółowe parametry architektury
                    model_info = show_data.get('model_info', {})
                    
                    # Wyciągnij kluczowe parametry architektoniczne
                    architecture_params = {}
                    for key, value in model_info.items():
                        if 'context_length' in key:
                            architecture_params['context_length'] = value
                        elif 'parameter_count' in key:
                            architecture_params['parameter_count'] = value
                        elif 'block_count' in key:
                            architecture_params['block_count'] = value
                        elif 'embedding_length' in key:
                            architecture_params['embedding_length'] = value
                        elif 'attention.head_count' in key and not 'kv' in key:
                            architecture_params['attention_heads'] = value
                        elif 'attention.head_count_kv' in key:
                            architecture_params['attention_heads_kv'] = value
                        elif 'feed_forward_length' in key:
                            architecture_params['feed_forward_length'] = value
                    
                    base_data.update(architecture_params)
                    
                    # Capabilities z show
                    base_data['capabilities'] = show_data.get('capabilities', [])
                    
                    # Template i parameters dla chatowych modeli
                    if show_data.get('template'):
                        base_data['has_chat_template'] = True
                    
                    # Licencja
                    if show_data.get('license'):
                        base_data['has_license'] = True
                        
                else:
                    print(f"    ⚠️ Nie udało się pobrać szczegółów dla {model_name}")
                    
            except requests.exceptions.Timeout:
                print(f"    ⏱️ Timeout dla {model_name}")
            except Exception as e:
                print(f"    ❌ Błąd dla {model_name}: {e}")
            
            # Dodatkowe obliczenia
            if base_data.get('parameter_count'):
                base_data['parameter_count_formatted'] = f"{base_data['parameter_count']/1e9:.1f}B"
            
            if base_data.get('context_length'):
                base_data['context_length_formatted'] = f"{base_data['context_length']/1000:.0f}K" if base_data['context_length'] >= 1000 else str(base_data['context_length'])
            
            # Możliwości na podstawie nazwy i rodziny
            inferred_capabilities = []
            name_lower = model_name.lower()
            family_lower = base_data.get('family', '').lower()
            
            if 'vision' in name_lower or 'llava' in name_lower:
                inferred_capabilities.append('vision')
            if 'code' in name_lower or family_lower in ['codellama', 'starcoder', 'codegemma']:
                inferred_capabilities.append('coding')
            if 'embed' in name_lower or 'embedding' in name_lower:
                inferred_capabilities.append('embedding')
            if 'instruct' in name_lower or 'chat' in name_lower:
                inferred_capabilities.append('chat')
            
            base_data['inferred_capabilities'] = inferred_capabilities
            base_data['all_capabilities'] = list(set(base_data.get('capabilities', []) + inferred_capabilities))
            
            enhanced_models.append(base_data)
        
        print(f"✅ Pobrano szczegółowe dane dla {len(enhanced_models)} modeli z API")
        return enhanced_models
        
    except requests.exceptions.ConnectionError:
        print("❌ Brak połączenia z API Ollama")
        return []
    except Exception as e:
        print(f"❌ Błąd podczas pobierania z API: {e}")
        return []

def find_similar_models_api_only(reference_model="gemma2:2b", param_tolerance=1.5, size_tolerance=1.0):
    """
    Znajduje modele podobne używając TYLKO danych z API Ollama
    
    Args:
        reference_model: Model referencyjny 
        param_tolerance: Tolerancja parametrów (wielokrotność)
        size_tolerance: Tolerancja rozmiaru w GB
        
    Returns:
        Lista podobnych modeli
    """
    print(f"🔍 WYSZUKIWANIE PODOBNYCH MODELI (API) DO: {reference_model}")
    
    # Pobierz wszystkie modele z API
    all_models = fetch_enhanced_models_from_api()
    
    if not all_models:
        print("❌ Nie udało się pobrać modeli z API")
        return []
    
    # Znajdź model referencyjny
    reference = None
    for model in all_models:
        if model.get('name', '').lower() == reference_model.lower():
            reference = model
            break
    
    if not reference:
        print(f"❌ Nie znaleziono modelu referencyjnego: {reference_model}")
        return []
    
    # Wyświetl parametry referencyjne
    print(f"\n🎯 MODEL REFERENCYJNY: {reference_model}")
    print(f"   📊 Parametry: {reference.get('parameter_size', 'N/A')} ({reference.get('parameter_count_formatted', 'N/A')})")
    print(f"   💾 Rozmiar: {reference.get('size_gb', 0):.2f} GB")
    print(f"   📝 Kontekst: {reference.get('context_length_formatted', 'N/A')}")
    print(f"   🏗️ Rodzina: {reference.get('family', 'N/A')}")
    print(f"   ⚙️ Kwantyzacja: {reference.get('quantization_level', 'N/A')}")
    print(f"   ✨ Możliwości: {', '.join(reference.get('all_capabilities', []))}")
    
    # Parametry referencyjne
    ref_param_count = reference.get('parameter_count', 0)
    ref_size_gb = reference.get('size_gb', 0)
    ref_context = reference.get('context_length', 0)
    ref_family = reference.get('family', '')
    ref_capabilities = set(reference.get('all_capabilities', []))
    
    similar_models = []
    
    for model in all_models:
        if model.get('name', '').lower() == reference_model.lower():
            continue  # Pomiń model referencyjny
        
        similarity_score = 0
        similarity_details = []
        
        # Porównaj liczbę parametrów (najważniejsze kryterium)
        model_param_count = model.get('parameter_count', 0)
        if ref_param_count > 0 and model_param_count > 0:
            param_ratio = max(ref_param_count, model_param_count) / min(ref_param_count, model_param_count)
            if param_ratio <= param_tolerance:
                similarity_score += 4
                similarity_details.append(f"Parametry: {model.get('parameter_count_formatted', 'N/A')} (~{reference.get('parameter_count_formatted', 'N/A')})")
            elif param_ratio <= param_tolerance * 1.5:
                similarity_score += 2
                similarity_details.append(f"Parametry: {model.get('parameter_count_formatted', 'N/A')} (podobne)")
        
        # Porównaj rozmiar
        model_size_gb = model.get('size_gb', 0)
        if ref_size_gb > 0 and model_size_gb > 0:
            size_diff = abs(ref_size_gb - model_size_gb)
            if size_diff <= size_tolerance:
                similarity_score += 2
                similarity_details.append(f"Rozmiar: {model_size_gb:.2f}GB (~{ref_size_gb:.2f}GB)")
            elif size_diff <= size_tolerance * 2:
                similarity_score += 1
                similarity_details.append(f"Rozmiar: {model_size_gb:.2f}GB (podobny)")
        
        # Porównaj rodzinę modeli
        model_family = model.get('family', '')
        if ref_family and model_family:
            if ref_family == model_family:
                similarity_score += 2
                similarity_details.append(f"Rodzina: {model_family} (identyczna)")
            elif any(fam in model.get('families', []) for fam in reference.get('families', [])):
                similarity_score += 1
                similarity_details.append(f"Rodzina: {model_family} (powiązana)")
        
        # Porównaj długość kontekstu
        model_context = model.get('context_length', 0)
        if ref_context > 0 and model_context > 0:
            if ref_context == model_context:
                similarity_score += 1
                similarity_details.append(f"Kontekst: {model.get('context_length_formatted', 'N/A')} (identyczny)")
            elif abs(ref_context - model_context) <= ref_context * 0.5:
                similarity_score += 0.5
                similarity_details.append(f"Kontekst: {model.get('context_length_formatted', 'N/A')} (podobny)")
        
        # Porównaj możliwości
        model_capabilities = set(model.get('all_capabilities', []))
        common_capabilities = ref_capabilities.intersection(model_capabilities)
        if common_capabilities:
            similarity_score += len(common_capabilities) * 0.5
            similarity_details.append(f"Możliwości: {', '.join(common_capabilities)}")
        
        # Dodaj jeśli wystarczająco podobny
        if similarity_score >= 2.0:  # Minimum 2 punkty podobieństwa
            model_copy = model.copy()
            model_copy['similarity_score'] = similarity_score
            model_copy['similarity_details'] = similarity_details
            similar_models.append(model_copy)
    
    # Sortuj według podobieństwa
    similar_models.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
    
    return similar_models

# ...existing code...
