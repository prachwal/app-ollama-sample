"""
Configuration settings for Ollama LLM testing suite.
"""

# Ollama API Configuration
OLLAMA_API_URL = "http://localhost:11434"
DEFAULT_TIMEOUT_PER_MODEL = 180  # Domyślny timeout dla pojedynczej odpowiedzi modelu testowanego
DEFAULT_SLEEP_BETWEEN_MODELS = 2  # Domyślna pauza między modelami testowanymi

# Gemini API Configuration
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_JUDGE_MODEL_NAME = "gemini-1.5-flash"  # Starsza, stabilniejsza wersja
GEMINI_JUDGE_TIMEOUT = 60  # Timeout dla odpowiedzi modelu sędziego

# Cache Configuration
CACHE_EXPIRY_HOURS = 24  # Cache ważny przez 24 godziny

# Output Configuration
OUTPUT_DIR = "outputs"
CACHE_DIR = "cache"
EXPORTS_DIR = "exports"
