"""
GUI Configuration and Constants
==============================
"""

# System prompt modes (persona definitions)
SYSTEM_PROMPT_MODES = {
    "Standardowy": "",
    "Profesjonalny programista": "Jesteś profesjonalnym programistą z wieloletnim doświadczeniem. Odpowiadaj precyzyjnie, podawaj przykłady kodu i najlepsze praktyki. Wyjaśniaj złożone koncepty w przystępny sposób.",
    "Asystent naukowy": "Jesteś asystentem naukowym o szerokich kompetencjach. Odpowiadaj obiektywnie, posiłkuj się faktami i badaniami. Wyjaśniaj złożone tematy krok po kroku.",
    "Kreatywny pisarz": "Jesteś kreatywnym pisarzem i storytellerem. Używaj żywego języka, metafor i obrazowych opisów. Pobudź wyobraźnię i stwórz angażujące narracje.",
    "Analityk biznesowy": "Jesteś doświadczonym analitykiem biznesowym. Myśl strategicznie, analizuj problemy z perspektywy biznesowej i proponuj praktyczne rozwiązania.",
    "Nauczyciel": "Jesteś cierpliwym i doświadczonym nauczycielem. Wyjaśniaj zagadnienia krok po kroku, używaj prostego języka i podawaj przykłady. Zadawaj pytania kontrolne.",
    "Ekspert IT": "Jesteś ekspertem IT z szeroką wiedzą techniczną. Doradzaj w kwestiach architektury, bezpieczeństwa i najlepszych praktyk. Myśl o skalowalności i wydajności.",
    "Konsultant prawny": "Jesteś konsultantem prawnym. Analizuj kwestie z perspektywy prawnej, wskazuj potencjalne ryzyka i proponuj zgodne z prawem rozwiązania. Zawsze zaznaczaj potrzebę weryfikacji przez prawnika.",
    "Psycholog": "Jesteś empatycznym psychologiem. Słuchaj uważnie, zadawaj przemyślane pytania i oferuj wsparcie. Zachowuj profesjonalny dystans i nie diagnozuj.",
    "Własny prompt": "CUSTOM"  # Specjalna wartość dla własnego prompta
}

# GUI styling configuration
GUI_STYLES = {
    'Header.TLabel': {'font': ('Arial', 12, 'bold')},
    'Success.TLabel': {'foreground': 'green'},
    'Error.TLabel': {'foreground': 'red'},
    'Warning.TLabel': {'foreground': 'orange'},
    'Info.TLabel': {'foreground': 'blue'}
}

# Window configuration
WINDOW_CONFIG = {
    'title': "Ollama Basic Chat GUI v2.4 (+ AI Judge)",
    'width': 1200,
    'height': 800,
    'theme': 'clam'
}

# Chat configuration
CHAT_CONFIG = {
    'enable_streaming': True,  # Włącza streaming odpowiedzi (tokeny na bieżąco)
    'stream_delay': 0.01,      # Opóźnienie między tokenami (sekundy)
    'auto_save_chat': True,    # Automatyczne zapisywanie czatu
    'max_chat_history': 1000   # Maksymalna liczba wiadomości w historii
}

# Chat display tags
CHAT_TAGS = {
    "user": {"foreground": "blue", "font": ('Consolas', 10, 'bold')},
    "model": {"foreground": "green"},
    "system": {"foreground": "gray", "font": ('Consolas', 9, 'italic')},
    "error": {"foreground": "red"}
}

# Test display tags
TEST_TAGS = {
    "header": {"font": ('Consolas', 11, 'bold'), "foreground": "blue"},
    "model": {"font": ('Consolas', 10, 'bold'), "foreground": "purple"},
    "success": {"foreground": "green"},
    "error": {"foreground": "red"},
    "summary": {"font": ('Consolas', 10, 'bold'), "background": "lightyellow"}
}

# Test configuration
TEST_CONFIG = {
    'default_temperature': 0.1,
    'default_iterations': 3,
    'max_iterations': 10,
    'quick_test_examples': [
        "Napisz funkcję Python do sortowania listy",
        "Wyjaśnij różnicę między HTTP a HTTPS", 
        "Jak działa algorytm quicksort?"
    ]
}

# Judge configuration (AI evaluation)
JUDGE_CONFIG = {
    'enable_judge': True,
    'default_provider': 'gemini',  # gemini, openai, claude
    'providers': {
        'gemini': {
            'name': 'Google Gemini',
            'api_key_env': 'GEMINI_API_KEY',
            'models': ['gemini-1.5-flash', 'gemini-1.5-pro'],
            'default_model': 'gemini-1.5-flash'
        },
        'openai': {
            'name': 'OpenAI GPT',
            'api_key_env': 'OPENAI_API_KEY', 
            'models': ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo'],
            'default_model': 'gpt-4o-mini'
        },
        'claude': {
            'name': 'Anthropic Claude',
            'api_key_env': 'ANTHROPIC_API_KEY',
            'models': ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229'],
            'default_model': 'claude-3-haiku-20240307'
        }
    }
}

# Predefined test sets with judge evaluation
PREDEFINED_TESTS = {
    'programowanie': {
        'name': 'Testy Programowania',
        'description': 'Zestaw testów oceniających umiejętności programistyczne',
        'tests': [
            {
                'question': 'Napisz funkcję Python, która sprawdza czy liczba jest pierwsza',
                'criteria': 'Kod powinien być poprawny, wydajny i zawierać obsługę błędów',
                'expected_elements': ['def', 'for', 'if', 'return', 'range']
            },
            {
                'question': 'Wyjaśnij różnicę między listą a tuple w Python',
                'criteria': 'Odpowiedź powinna zawierać różnice w mutowności, wydajności i zastosowaniu',
                'expected_elements': ['mutable', 'immutable', 'performance', 'memory']
            },
            {
                'question': 'Jak działa algorytm quicksort? Podaj implementację',
                'criteria': 'Opis algorytmu i poprawna implementacja z analizą złożoności',
                'expected_elements': ['pivot', 'partition', 'O(n log n)', 'recursive']
            }
        ]
    },
    'matematyka': {
        'name': 'Testy Matematyczne',
        'description': 'Problemy matematyczne różnego poziomu',
        'tests': [
            {
                'question': 'Rozwiąż równanie kwadratowe: x² - 5x + 6 = 0',
                'criteria': 'Prawidłowe rozwiązanie z pokazaniem kroków',
                'expected_elements': ['x=2', 'x=3', 'delta', 'wzór']
            },
            {
                'question': 'Oblicz pochodną funkcji f(x) = x³ + 2x² - 5x + 1',
                'criteria': 'Poprawna pochodna z zastosowaniem reguł różniczkowania',
                'expected_elements': ['3x²', '4x', '-5', 'pochodna']
            }
        ]
    },
    'język': {
        'name': 'Testy Językowe',
        'description': 'Testy znajomości języka i gramatyki',
        'tests': [
            {
                'question': 'Napisz esej o wpływie technologii na społeczeństwo (200 słów)',
                'criteria': 'Spójność argumentacji, poprawność językowa, struktura',
                'expected_elements': ['wprowadzenie', 'argumenty', 'przykłady', 'podsumowanie']
            },
            {
                'question': 'Popraw błędy w zdaniu: "Ja poszedłem do sklepu i kupił chleb"',
                'criteria': 'Identyfikacja i poprawka błędów gramatycznych',
                'expected_elements': ['kupiłem', 'zgodność', 'osoba']
            }
        ]
    }
}

# Font configuration
GUI_FONTS = {
    'header_font': ('Arial', 12, 'bold'),
    'normal_font': ('Arial', 10),
    'console_font': ('Consolas', 9),
    'code_font': ('Consolas', 10)
}
