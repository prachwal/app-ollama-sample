#!/usr/bin/env python3
"""
Test trybu systemowego dla Ollama GUI
"""

import sys
import os

# Dodaj src do PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import ask_ollama

def test_system_prompt():
    """Test prompta systemowego"""
    
    print("🧪 Test trybu systemowego")
    print("=" * 50)
    
    # Test podstawowy bez system prompt
    print("\n1. Test bez prompta systemowego:")
    result1 = ask_ollama(
        model="qwen2.5:1.5b",
        prompt="Napisz krótki kod Python do sortowania listy",
        test_name="Test bez system prompt",
        timeout=30
    )
    
    if result1:
        print(f"✅ Odpowiedź otrzymana ({len(result1['response'])} znaków)")
    else:
        print("❌ Brak odpowiedzi")
    
    print("\n" + "-" * 50)
    
    # Test z promptem systemowym programisty
    print("\n2. Test z promptem systemowym (Programista):")
    system_prompt = "Jesteś profesjonalnym programistą z wieloletnim doświadczeniem. Odpowiadaj precyzyjnie, podawaj przykłady kodu i najlepsze praktyki. Wyjaśniaj złożone koncepty w przystępny sposób."
    
    result2 = ask_ollama(
        model="qwen2.5:1.5b",
        prompt="Napisz krótki kod Python do sortowania listy",
        test_name="Test z system prompt - Programista",
        system_prompt=system_prompt,
        timeout=30
    )
    
    if result2:
        print(f"✅ Odpowiedź otrzymana ({len(result2['response'])} znaków)")
        print("🎭 Prompt systemowy zastosowany")
    else:
        print("❌ Brak odpowiedzi")
    
    print("\n" + "=" * 50)
    print("🎉 Test zakończony!")
    
    if result1 and result2:
        print(f"\nPorównanie długości odpowiedzi:")
        print(f"  - Bez system prompt: {len(result1['response'])} znaków")
        print(f"  - Z system prompt: {len(result2['response'])} znaków")
        
        # Proste porównanie różnic
        if abs(len(result1['response']) - len(result2['response'])) > 50:
            print("📊 System prompt prawdopodobnie wpłynął na odpowiedź")
        else:
            print("📊 Podobne długości odpowiedzi")

if __name__ == "__main__":
    try:
        test_system_prompt()
    except KeyboardInterrupt:
        print("\n🛑 Test przerwany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd podczas testu: {e}")
