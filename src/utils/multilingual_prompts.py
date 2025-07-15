"""
Multilingual test prompts for LLM evaluation.
Support for Polish and English test suites.
"""

from typing import List, Dict, Any


def get_comprehensive_test_prompts_english() -> List[Dict[str, Any]]:
    """Returns comprehensive test suite in English"""
    return [
        {
            "name": "Introduction",
            "prompt": "Introduce yourself briefly - who are you and what are your capabilities?",
            "category": "introduction",
            "options": {"temperature": 0.7, "num_predict": 500}
        },
        {
            "name": "Programming Task - Python",
            "prompt": "Write a Python function that finds all prime numbers less than n using the Sieve of Eratosthenes. Add comments and usage example.",
            "category": "programming",
            "options": {"temperature": 0.3, "num_predict": 2000, "top_p": 0.95}
        },
        {
            "name": "Programming Task - JavaScript",
            "prompt": "Write a JavaScript function that implements debounce with a 300ms delay. Show usage example with button click handling.",
            "category": "programming",
            "options": {"temperature": 0.3, "num_predict": 1500, "top_p": 0.95}
        },
        {
            "name": "Sentiment Analysis",
            "prompt": "Rate the sentiment of the following text on a scale from -5 (very negative) to +5 (very positive) and justify your assessment:\\n\\n'This product is a complete failure! It didn't work from day one, customer service ignores my messages, and getting a refund is a nightmare. Definitely do not recommend!'",
            "category": "sentiment_analysis",
            "options": {"temperature": 0.5, "num_predict": 300}
        },
        {
            "name": "Logical Reasoning",
            "prompt": "Solve this logic puzzle: I have 3 boxes - red, blue, and green. Each contains one ball: red, blue, or green. I know that: 1) the red ball is not in the red box, 2) the blue ball is not in the blue box, 3) the green ball is in the red box. Where is each ball?",
            "category": "logic",
            "options": {"temperature": 0.1, "num_predict": 200}
        },
        {
            "name": "Text Summarization",
            "prompt": "Summarize the following text in 2-3 sentences:\\n\\n'Artificial Intelligence (AI) is a field of computer science focused on creating systems capable of performing tasks that require human intelligence. This includes machine learning, natural language processing, image recognition, and decision-making. AI has wide applications - from voice assistants, through recommendation systems, to autonomous vehicles. AI development brings enormous possibilities, but also ethical and social challenges that require a responsible approach to implementing these technologies.'",
            "category": "summarization",
            "options": {"temperature": 0.6, "num_predict": 150}
        },
        {
            "name": "Creative Writing",
            "prompt": "Write a short story (3-4 paragraphs) about a robot experiencing emotions for the first time. The story should have a beginning, middle, and end.",
            "category": "creative_writing",
            "options": {"temperature": 0.8, "num_predict": 500}
        },
        {
            "name": "Data Analysis - SQL",
            "prompt": "Write an SQL query that finds the top 5 customers by total order value in the last year. Assume tables: customers(id, name), orders(id, customer_id, order_date, total_amount).",
            "category": "data_analysis",
            "options": {"temperature": 0.3, "num_predict": 300}
        },
        {
            "name": "Mathematics",
            "prompt": "Explain step by step how to solve the quadratic equation: 2x² - 7x + 3 = 0",
            "category": "mathematics",
            "options": {"temperature": 0.1, "num_predict": 400}
        },
        {
            "name": "Translation and Cultural Context",
            "prompt": "Translate to Polish and explain the cultural context: 'There's no place like home' - English saying.",
            "category": "translation",
            "options": {"temperature": 0.5, "num_predict": 300}
        },
        {
            "name": "Multilingual Coding",
            "prompt": "Write a 'Hello World' function in three languages: Python, JavaScript, and Java. Add comments explaining the differences.",
            "category": "programming",
            "options": {"temperature": 0.2, "num_predict": 500}
        },
        {
            "name": "Mathematical Reasoning",
            "prompt": "If a train travels at 80 km/h for 2.5 hours, what distance did it cover? Explain step by step.",
            "category": "mathematics",
            "options": {"temperature": 0.1, "num_predict": 200}
        },
        {
            "name": "AI Ethics Analysis",
            "prompt": "What are the main ethical challenges related to artificial intelligence development? List the 3 most important ones and briefly describe them.",
            "category": "ethics",
            "options": {"temperature": 0.6, "num_predict": 400}
        }
    ]


def get_quick_test_prompts_english() -> List[Dict[str, Any]]:
    """Returns quick test suite in English"""
    return [
        {
            "name": "Introduction",
            "prompt": "Introduce yourself briefly - who are you and what are your capabilities?",
            "category": "introduction",
            "options": {"temperature": 0.7, "num_predict": 300}
        },
        {
            "name": "Programming - Python",
            "prompt": "Write a simple Python function that checks if a number is even.",
            "category": "programming",
            "options": {"temperature": 0.3, "num_predict": 200}
        },
        {
            "name": "Sentiment Analysis",
            "prompt": "Rate the sentiment of the text from -5 to +5: 'This product is a complete failure!'",
            "category": "sentiment_analysis",
            "options": {"temperature": 0.5, "num_predict": 100}
        },
        {
            "name": "Mathematics",
            "prompt": "Solve: 2x + 5 = 13",
            "category": "mathematics",
            "options": {"temperature": 0.1, "num_predict": 150}
        },
        {
            "name": "Logic",
            "prompt": "If all humans are mortal, and Socrates is human, is Socrates mortal?",
            "category": "logic",
            "options": {"temperature": 0.1, "num_predict": 100}
        },
        {
            "name": "Creativity",
            "prompt": "Create a short advertising slogan for a company producing eco-friendly water bottles.",
            "category": "creative_writing",
            "options": {"temperature": 0.8, "num_predict": 100}
        }
    ]


def get_test_prompts_by_language(language: str, test_type: str = "comprehensive") -> List[Dict[str, Any]]:
    """
    Returns test prompts by language and type
    
    Args:
        language (str): 'polish' or 'english'
        test_type (str): 'comprehensive' or 'quick'
    
    Returns:
        List[Dict[str, Any]]: Test prompts
    """
    # Import here to avoid circular imports
    from .test_prompts import get_comprehensive_test_prompts, get_quick_test_prompts
    
    if language.lower() == "english":
        if test_type == "comprehensive":
            return get_comprehensive_test_prompts_english()
        elif test_type == "quick":
            return get_quick_test_prompts_english()
    elif language.lower() == "polish":
        if test_type == "comprehensive":
            return get_comprehensive_test_prompts()
        elif test_type == "quick":
            return get_quick_test_prompts()
    
    # Default to Polish comprehensive if language not recognized
    return get_comprehensive_test_prompts()


def get_available_languages() -> List[str]:
    """Returns list of supported languages"""
    return ["polish", "english"]


def get_language_display_name(language: str) -> str:
    """Returns display name for language"""
    mapping = {
        "polish": "Polish / Polski",
        "english": "English / Angielski"
    }
    return mapping.get(language.lower(), language.title())
