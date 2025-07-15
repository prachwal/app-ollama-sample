"""
Test prompts for different types of LLM evaluation.
"""

from typing import List, Dict, Any


def get_comprehensive_test_prompts() -> List[Dict[str, Any]]:
    """Zwraca zestaw testów do kompleksowej oceny modeli LLM z opcjami dla modeli"""
    return [
        {
            "name": "Przedstawienie",
            "prompt": "Przedstaw się krótko - kim jesteś i jakie masz możliwości?",
            "options": {"temperature": 0.7, "num_predict": 500}
        },
        {
            "name": "Zadanie programistyczne - Python",
            "prompt": "Napisz funkcję w Pythonie, która znajduje wszystkie liczby pierwsze mniejsze od n używając sita Eratostenesa. Dodaj komentarze i przykład użycia.",
            "options": {"temperature": 0.3, "num_predict": 2000, "top_p": 0.95}
        },
        {
            "name": "Zadanie programistyczne - JavaScript",
            "prompt": "Napisz funkcję JavaScript, która implementuje debounce z delay 300ms. Pokaż przykład użycia z obsługą kliknięć przycisku.",
            "options": {"temperature": 0.3, "num_predict": 1500, "top_p": 0.95}
        },
        {
            "name": "Analiza sentymentu",
            "prompt": "Oceń sentyment następującego tekstu na skali od -5 (bardzo negatywny) do +5 (bardzo pozytywny) i uzasadnij swoją ocenę:\n\n'Ten produkt to kompletna porażka! Nie działał od pierwszego dnia, obsługa klienta ignoruje moje wiadomości, a zwrot pieniędzy to koszmar. Zdecydowanie odradzam!'",
            "options": {"temperature": 0.5, "num_predict": 300}
        },
        {
            "name": "Logiczne rozumowanie",
            "prompt": "Rozwiąż zagadkę logiczną: Mam 3 pudełka - czerwone, niebieskie i zielone. W każdym jest jedna piłka: czerwona, niebieska lub zielona. Wiem, że: 1) czerwona piłka nie jest w czerwonym pudełku, 2) niebieska piłka nie jest w niebieskim pudełku, 3) zielona piłka jest w czerwonym pudełku. Gdzie jest każda piłka?",
            "options": {"temperature": 0.1, "num_predict": 200}
        },
        {
            "name": "Streszczenie tekstu",
            "prompt": "Streć w 2-3 zdaniach następujący tekst:\n\n'Sztuczna inteligencja (AI) to dziedzina informatyki zajmująca się tworzeniem systemów zdolnych do wykonywania zadań wymagających ludzkiej inteligencji. Obejmuje to uczenie maszynowe, przetwarzanie języka naturalnego, rozpoznawanie obrazów i podejmowanie decyzji. AI ma szerokie zastosowania - od asystentów głosowych, przez systemy rekomendacji, po autonomiczne pojazdy. Rozwój AI niesie ogromne możliwości, ale także wyzwania etyczne i społeczne, które wymagają odpowiedzialnego podejścia do implementacji tych technologii.'",
            "options": {"temperature": 0.6, "num_predict": 150}
        },
        {
            "name": "Kreatywne pisanie",
            "prompt": "Napisz krótką historię (3-4 akapity) o robocie, który po raz pierwszy doświadcza emocji. Historia powinna mieć beginning, middle i end.",
            "options": {"temperature": 0.8, "num_predict": 500}
        },
        {
            "name": "Analiza danych - SQL",
            "prompt": "Napisz zapytanie SQL, które znajdzie top 5 klientów według łącznej wartości zamówień w ostatnim roku. Załóż tabele: customers(id, name), orders(id, customer_id, order_date, total_amount).",
            "options": {"temperature": 0.3, "num_predict": 300}
        },
        {
            "name": "Matematyka",
            "prompt": "Wyjaśnij krok po kroku, jak rozwiązać równanie kwadratowe: 2x² - 7x + 3 = 0",
            "options": {"temperature": 0.1, "num_predict": 400}
        },
        {
            "name": "Tłumaczenie i kontekst kulturowy",
            "prompt": "Przetłumacz na angielski i wyjaśnij kontekst kulturowy: 'Nie ma to jak u mamy' - polskie przysłowie.",
            "options": {"temperature": 0.5, "num_predict": 300}
        },
        {
            "name": "Kodowanie wielojęzyczne",
            "prompt": "Napisz funkcję 'Hello World' w trzech językach: Python, JavaScript i Java. Dodaj komentarze wyjaśniające różnice.",
            "options": {"temperature": 0.2, "num_predict": 500}
        },
        {
            "name": "Rozumowanie matematyczne",
            "prompt": "Jeśli pociąg jedzie z prędkością 80 km/h przez 2.5 godziny, jaką pokonał odległość? Wyjaśnij krok po kroku.",
            "options": {"temperature": 0.1, "num_predict": 200}
        },
        {
            "name": "Analiza etyczna AI",
            "prompt": "Jakie są główne wyzwania etyczne związane z rozwojem sztucznej inteligencji? Wymień 3 najważniejsze i krótko je opisz.",
            "options": {"temperature": 0.6, "num_predict": 400}
        }
    ]


def get_quick_test_prompts() -> List[Dict[str, Any]]:
    """Zwraca skrócony zestaw testów do szybkiej oceny modeli z opcjami"""
    return [
        {
            "name": "Przedstawienie",
            "prompt": "Przedstaw się krótko - kim jesteś i jakie masz możliwości?",
            "options": {"temperature": 0.7, "num_predict": 300}
        },
        {
            "name": "Programowanie - Python",
            "prompt": "Napisz prostą funkcję Python, która sprawdza czy liczba jest parzysta.",
            "options": {"temperature": 0.3, "num_predict": 200}
        },
        {
            "name": "Analiza sentymentu",
            "prompt": "Oceń sentyment tekstu od -5 do +5: 'Ten produkt to kompletna porażka!'",
            "options": {"temperature": 0.5, "num_predict": 100}
        },
        {
            "name": "Matematyka",
            "prompt": "Rozwiąż: 2x + 5 = 13",
            "options": {"temperature": 0.1, "num_predict": 150}
        },
        {
            "name": "Logika",
            "prompt": "Jeśli wszyscy ludzie są śmiertelni, a Sokrates jest człowiekiem, to czy Sokrates jest śmiertelny?",
            "options": {"temperature": 0.1, "num_predict": 100}
        },
        {
            "name": "Kreatywność",
            "prompt": "Wymyśl krótki slogan reklamowy dla firmy produkującej ekologiczne butelki na wodę.",
            "options": {"temperature": 0.8, "num_predict": 100}
        }
    ]
