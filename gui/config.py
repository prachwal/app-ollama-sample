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
    'title': "Ollama Basic Chat GUI v2.2",
    'width': 1200,
    'height': 800,
    'theme': 'clam'
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

# Font configuration
GUI_FONTS = {
    'header_font': ('Arial', 12, 'bold'),
    'normal_font': ('Arial', 10),
    'console_font': ('Consolas', 9),
    'code_font': ('Consolas', 10)
}
