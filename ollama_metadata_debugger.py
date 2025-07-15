import requests
import json

OLLAMA_API_URL = "http://localhost:11434"

def debug_model_metadata(model_name):
    """Debug funkcja do sprawdzenia pełnej struktury metadanych modelu"""
    
    # 1. Sprawdź /api/tags
    print(f"=== API TAGS dla {model_name} ===")
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags")
        data = response.json()
        models = data.get('models', [])
        for model in models:
            if model['name'] == model_name:
                print("Dane z /api/tags:")
                print(json.dumps(model, indent=2, ensure_ascii=False))
                break
    except Exception as e:
        print(f"Błąd /api/tags: {e}")
    
    # 2. Sprawdź /api/show  
    print(f"\n=== API SHOW dla {model_name} ===")
    try:
        response = requests.post(f"{OLLAMA_API_URL}/api/show", json={"name": model_name})
        data = response.json()
        print("Dane z /api/show:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Błąd /api/show: {e}")

if __name__ == "__main__":
    # Sprawdźmy jeden model dokładnie
    debug_model_metadata("gemma2:2b")
