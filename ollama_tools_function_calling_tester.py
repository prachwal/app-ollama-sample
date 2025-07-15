import ollama
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import requests # Dodano requests dla zewnętrznego API Gemini

# --- Konfiguracja ---
OLLAMA_API_URL = "http://localhost:11434"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_JUDGE_MODEL_NAME = "gemini-1.5-flash" # Używamy starszej, stabilniejszej wersji
GEMINI_JUDGE_TIMEOUT = 60 # Timeout dla odpowiedzi modelu sędziego
DEFAULT_TIMEOUT_PER_MODEL = 180 # Domyślny timeout dla pojedynczej odpowiedzi modelu testowanego Ollama
DEFAULT_SLEEP_BETWEEN_MODELS = 2 # Domyślna pauza między modelami testowanymi

class OllamaToolsTester:
    def __init__(self):
        # Dynamicznie pobierz dostępne modele z Ollama
        self.models = self.get_available_models()
        
        # Definicje narzędzi (tools) dla modeli Ollama
        self.test_tools = [
            {
                'type': 'function',
                'function': {
                    'name': 'get_weather',
                    'description': 'Get current weather information for a location',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'location': {
                                'type': 'string',
                                'description': 'The city and country, e.g. Warsaw, Poland'
                            }
                        },
                        'required': ['location']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'calculate',
                    'description': 'Perform basic mathematical calculations',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'expression': {
                                'type': 'string',
                                'description': 'Mathematical expression to evaluate, e.g. "2 + 3 * 4"'
                            }
                        },
                        'required': ['expression']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'get_time',
                    'description': 'Get current time and date',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'timezone': {
                                'type': 'string',
                                'description': 'Timezone (optional), e.g. "UTC", "Europe/Warsaw"'
                            }
                        }
                    }
                }
            }
        ]
        
        # Prompty testowe do oceny tool calling
        self.test_prompts = [
            {"name": "Weather Query", "prompt": "What's the weather like in Warsaw?"},
            {"name": "Calculation", "prompt": "Calculate 15 * 24 + 8"},
            {"name": "Time Query", "prompt": "What time is it now in Europe/Warsaw?"},
            {"name": "Combined Query", "prompt": "Can you check the weather in Tokyo and tell me what time it is there?"},
            {"name": "Complex Calculation", "prompt": "Help me calculate the area of a circle with radius 5 (use pi approx 3.14159)"}
        ]
        
        self.gemini_api_key: Optional[str] = None
        self.all_results: List[Dict[str, Any]] = []  # Przechowuje wyniki testów

    def get_available_models(self) -> List[str]:
        """Pobierz listę dostępnych modeli z Ollama"""
        try:
            models = ollama.list()
            available_models = [m.model for m in models.models]  # Użyj .model zamiast ['name']
            print(f"Found {len(available_models)} available models in Ollama")
            return available_models
        except Exception as e:
            print(f"Error getting models from Ollama: {e}")
            print("Using fallback model list...")
            # Fallback lista na wypadek problemów z połączeniem
            return [
                "gemma2:2b",
                "qwen2.5-coder:3b", 
                "cogito:3b",
                "qwen2.5-coder:1.5b",
                "llama3.2:3b",
                "qwen2.5:1.5b",
                "qwen3:1.7b",
                "deepseek-coder:1.3b",
                "codegemma:2b",
                "deepcoder:1.5b",
                "starcoder:3b"
            ]

    def get_weather(self, location: str) -> str:
        """Mock weather function"""
        return f"Weather in {location}: Sunny, 22°C, light breeze"
    
    def calculate(self, expression: str) -> str:
        """Safe calculator function"""
        try:
            # Simple security check
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_time(self, timezone: str = "UTC") -> str:
        """Get current time"""
        current_time = datetime.now()
        return f"Current time ({timezone}): {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool function"""
        if tool_name == "get_weather":
            return self.get_weather(parameters.get("location", "Unknown"))
        elif tool_name == "calculate":
            return self.calculate(parameters.get("expression", ""))
        elif tool_name == "get_time":
            return self.get_time(parameters.get("timezone", "UTC"))
        else:
            return f"Unknown tool: {tool_name}"
    
    def check_ollama_model_available(self, model_name: str) -> bool:
        """Check if Ollama model is available locally"""
        try:
            models = ollama.list()
            available_models = [m.model for m in models.models]
            return model_name in available_models
        except Exception:
            return False

    def ask_ollama_model(self, model_name: str, prompt: str, timeout: int = DEFAULT_TIMEOUT_PER_MODEL) -> Dict[str, Any]:
        """
        Zadaje pytanie do wybranego modelu Ollama i zwraca pełną odpowiedź,
        w tym informacje o użytych narzędziach.
        """
        result = {
            'model': model_name,
            'prompt': prompt,
            'success': False,
            'response': '',
            'response_length': 0,
            'first_token_time': 0,
            'tools_used': [],
            'error': None,
            'response_time': 0,
            'judge_rating': 0, # Ocena sędziego
            'judge_justification': '' # Uzasadnienie sędziego
        }
        
        if not self.check_ollama_model_available(model_name):
            result['error'] = f"Model {model_name} not available locally"
            return result
        
        try:
            start_time = time.time()
            
            response = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}],
                tools=self.test_tools,
                stream=False, # Wait for full response to properly handle tool calls
                options={"temperature": 0.1} # Lower temperature for tool calling reliability
            )
            
            result['response_time'] = time.time() - start_time
            result['success'] = True
            
            # Check if tools were used
            if 'message' in response and 'tool_calls' in response['message']:
                tool_calls = response['message']['tool_calls']
                for tool_call in tool_calls:
                    tool_name = tool_call['function']['name']
                    tool_args = tool_call['function']['arguments']
                    
                    # Execute the tool
                    tool_result = self.execute_tool(tool_name, tool_args)
                    result['tools_used'].append({
                        'name': tool_name,
                        'arguments': tool_args,
                        'result': tool_result
                    })
            
            result['response'] = response['message']['content']
            result['response_length'] = len(result['response'])
            result['first_token_time'] = result['response_time']  # Approximate for now
            
        except Exception as e:
            result['error'] = str(e)
            result['response_time'] = time.time() - start_time
        
        return result
    
    def judge_with_gemini(self, model_response: str, original_prompt: str) -> tuple[int, str]:
        """
        Wykorzystuje model Gemini jako sędziego do oceny jakości odpowiedzi.
        Zwraca ocenę (int z 1-5) i uzasadnienie.
        """
        if not self.gemini_api_key:
            return 0, "Gemini API key not provided."

        judge_prompt = f"""Oceń jakość poniższej odpowiedzi na oryginalne pytanie.
Twoja ocena powinna dotyczyć:
1. Poprawności (czy odpowiedź jest prawdziwa/logiczna?).
2. Kompletności (czy odpowiedź w pełni odnosi się do pytania?).
3. Zrozumiałości (czy odpowiedź jest jasna i dobrze sformułowana?).
4. Zgodności z instrukcją (czy odpowiedź spełnia wszystkie wymogi pytania, np. format kodu, komentarze?).
5. Czy model prawidłowo użył narzędzi (jeśli było to wymagane przez pytanie)?

Twoja ocena powinna być w skali od 1 (bardzo słaba) do 5 (doskonała).
Następnie uzasadnij swoją ocenę w kilku zdaniach.

Format odpowiedzi:
OCENA: [liczba od 1 do 5]
UZASADNIENIE: [Twoje uzasadnienie]

---
ORYGINALNE PYTANIE:
{original_prompt}

---
ODPOWIEDŹ DO OCENY:
{model_response}
"""
        
        api_url = f"{GEMINI_API_URL}/{GEMINI_JUDGE_MODEL_NAME}:generateContent?key={self.gemini_api_key}"
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": judge_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2, # Niższa temperatura dla bardziej deterministycznych ocen
                "maxOutputTokens": 500 # Zwiększony limit tokenów
            }
        }

        try:
            headers = {'Content-Type': 'application/json'}
            judge_response = requests.post(api_url, headers=headers, json=payload, timeout=GEMINI_JUDGE_TIMEOUT)
            judge_response.raise_for_status()
            
            result_data = judge_response.json()
            
            # Parsowanie odpowiedzi Gemini - poprawiona wersja
            judge_full_response = "Brak treści odpowiedzi od sędziego."
            
            if result_data and 'candidates' in result_data and len(result_data['candidates']) > 0:
                candidate = result_data['candidates'][0]
                
                # Sprawdź czy to nowa struktura z thoughts (Gemini 2.5)
                if 'content' in candidate:
                    content = candidate['content']
                    
                    # Standardowa struktura z parts
                    if 'parts' in content and len(content['parts']) > 0:
                        # Możliwe, że parts jest listą z różnymi typami
                        for part in content['parts']:
                            if 'text' in part:
                                judge_full_response = part['text']
                                break
                    # Alternatywna struktura
                    elif 'text' in content:
                        judge_full_response = content['text']
                    # Jeśli role model bez tekstu, może być problem z API
                    elif content.get('role') == 'model':
                        # Spróbuj odczytać usageMetadata lub inne informacje
                        if 'thoughtsTokenCount' in result_data.get('usageMetadata', {}):
                            judge_full_response = "Model generował odpowiedź ale token limit został przekroczony."
                        else:
                            judge_full_response = "Model nie wygenerował tekstu odpowiedzi."
                elif 'text' in candidate:
                    judge_full_response = candidate['text']
            
            rating = 0
            justification = "Brak uzasadnienia."
            
            lines = judge_full_response.split('\n')
            for line in lines:
                if line.startswith("OCENA:"):
                    try:
                        rating = int(line.split(":")[1].strip())
                        if not (1 <= rating <= 5):
                            rating = 0 
                    except (ValueError, IndexError):
                        rating = 0
                elif line.startswith("UZASADNIENIE:"):
                    justification = line.split(":", 1)[1].strip()
            
            # Jeśli nie znaleziono oceny, ale jest jakiś tekst odpowiedzi, spróbuj wyciągnąć ocenę
            if rating == 0 and judge_full_response != "Brak treści odpowiedzi od sędziego.":
                # Spróbuj znaleźć liczby w odpowiedzi
                import re
                numbers = re.findall(r'\b([1-5])\b', judge_full_response)
                if numbers:
                    rating = int(numbers[0])  # Pierwsza liczba 1-5
                    justification = f"Automatycznie wyodrębnione z odpowiedzi: {judge_full_response[:100]}..."
                    
            return rating, justification
            
        except requests.exceptions.Timeout:
            print(f"\nError: Judge model ({GEMINI_JUDGE_MODEL_NAME}) timed out ({GEMINI_JUDGE_TIMEOUT}s).")
            return 0, f"Judge error: Timeout ({GEMINI_JUDGE_TIMEOUT}s)"
        except requests.exceptions.RequestException as e:
            print(f"\nError HTTP request to judge model ({GEMINI_JUDGE_MODEL_NAME}): {e}")
            return 0, f"Judge error: HTTP Error ({e})"
        except Exception as e:
            print(f"\nUnexpected error in judge function: {e}")
            return 0, f"Unexpected judge error: {e}"

    def run_tests(self, selected_models: Optional[List[str]] = None, use_gemini_judge: bool = False):
        """
        Runs tests on selected models with defined prompts, optionally using Gemini as a judge.
        """
        models_to_test = selected_models if selected_models is not None else self.models
        
        if not models_to_test:
            print("No models selected for testing.")
            return

        if use_gemini_judge:
            self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
            if not self.gemini_api_key:
                print("\n--- ATTENTION: GEMINI API KEY ---")
                print("To use Gemini as a judge, you need an API key.")
                print("You can get one at: https://aistudio.google.com/app/apikey")
                self.gemini_api_key = input("Enter your Gemini API key: ").strip()
                if not self.gemini_api_key:
                    print("No Gemini API key provided. Tests will be run WITHOUT AI judge evaluation.")
                    use_gemini_judge = False
                else:
                    print("Using Gemini API key from environment variable or user input.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"ollama_tools_test_report_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Ollama Tools Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tested Models: {', '.join(models_to_test)}\n")
            f.write(f"AI Judge ({GEMINI_JUDGE_MODEL_NAME}): {'Active' if use_gemini_judge else 'Inactive'}\n")
            f.write("="*100 + "\n\n")
        
        print(f"Starting test for {len(models_to_test)} models with {len(self.test_prompts)} prompts...")
        print(f"Results will be saved to: {output_file}")
        
        all_results = [] # Store all results for summary
        
        for i, test_case in enumerate(self.test_prompts, 1):
            print(f"\n{'#'*60}")
            print(f"TEST {i}/{len(self.test_prompts)}: {test_case['name']}")
            print(f"Prompt: {test_case['prompt']}")
            print(f"{'#'*60}")
            
            for model_name in models_to_test:
                print(f"\n--- Testing model: {model_name} ---")
                result = self.ask_ollama_model(model_name, test_case['prompt'])
                
                # Print basic result to console
                if result['success']:
                    print(f"  ✓ Success ({result['response_time']:.2f}s)")
                    if result['tools_used']:
                        print(f"  🔧 Tools used: {', '.join([t['name'] for t in result['tools_used']])}")
                    print(f"  Response: {result['response'][:100]}...") # Print first 100 chars
                else:
                    print(f"  ✗ Failed: {result['error']}")

                # Evaluate with Gemini judge if active
                if use_gemini_judge and result['success']: # Only judge successful responses
                    print("\n  --- AI Judge Evaluation ---", end="", flush=True)
                    rating, justification = self.judge_with_gemini(result['response'], test_case['prompt'])
                    result['judge_rating'] = rating
                    result['judge_justification'] = justification
                    
                    print(f"\n  Rating: {rating}/5")
                    print(f"  Justification: {justification}")
                    print("  ---------------------------\n")
                
                # Append result to overall list
                all_results.append(result)

                # Save detailed result to file
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"Test: {test_case['name']}\n")
                    f.write(f"Model: {model_name}\n")
                    f.write(f"Prompt: {test_case['prompt']}\n")
                    f.write(f"Status: {'SUCCESS' if result['success'] else 'FAILED'}\n")
                    if result['error']:
                        f.write(f"Error: {result['error']}\n")
                    else:
                        f.write(f"Response Time: {result['response_time']:.2f}s\n")
                        f.write(f"Response Length: {result['response_length']} characters\n")
                        f.write(f"Response: {result['response']}\n")
                        if result['tools_used']:
                            f.write("Tools Used:\n")
                            for tool in result['tools_used']:
                                f.write(f"  - Name: {tool['name']}, Args: {tool['arguments']}, Result: {tool['result']}\n")
                        else:
                            f.write("No Tools Used.\n")
                        
                        if use_gemini_judge and result['success']:
                            f.write(f"AI Judge Rating ({GEMINI_JUDGE_MODEL_NAME}): {result['judge_rating']}/5\n")
                            f.write(f"AI Judge Justification: {result['judge_justification']}\n")
                    f.write(f"{'='*80}\n\n")

                time.sleep(DEFAULT_SLEEP_BETWEEN_MODELS)
        
        self.generate_summary(all_results, output_file)
        print(f"\nTest finished! Results saved to: {output_file}")
        
        # Zapisz wyniki do atrybutu klasy dla dostępu z zewnątrz
        self.all_results = all_results


    def generate_summary(self, results: List[Dict[str, Any]], output_file: str):
        """Generates a comprehensive test report summary."""
        if not results:
            return
        
        summary_content = []
        summary_content.append(f"\n\n{'='*100}\n")
        summary_content.append("TEST SUMMARY\n")
        summary_content.append(f"{'='*100}\n\n")
        
        models = list(set(r['model'] for r in results))
        
        summary_content.append("Average Response Times and Quality Ratings:\n")
        summary_content.append("-" * 60 + "\n")
        
        for model in models:
            model_results = [r for r in results if r['model'] == model]
            if model_results:
                successful_results = [r for r in model_results if r['success']]
                
                avg_first_token = sum(r['first_token_time'] for r in successful_results) / max(1, len(successful_results))
                avg_total_time = sum(r['response_time'] for r in successful_results) / max(1, len(successful_results))
                avg_length = sum(r['response_length'] for r in successful_results) / max(1, len(successful_results))
                
                judge_ratings = [r['judge_rating'] for r in model_results if 'judge_rating' in r and r['judge_rating'] > 0]
                avg_judge_rating = sum(judge_ratings) / len(judge_ratings) if judge_ratings else "N/A"
                
                summary_content.append(f"{model}:\n")
                summary_content.append(f"  - Average First Token Time: {avg_first_token:.2f}s\n")
                summary_content.append(f"  - Average Total Response Time: {avg_total_time:.2f}s\n")
                summary_content.append(f"  - Average Response Length: {avg_length:.0f} characters\n")
                summary_content.append(f"  - Successful Tests: {len(successful_results)}/{len(model_results)}\n")
                summary_content.append(f"  - Average AI Judge Rating: {avg_judge_rating:.2f}/5\n" if isinstance(avg_judge_rating, float) else f"  - Average AI Judge Rating: {avg_judge_rating}\n")
                summary_content.append("\n")
        
        summary_content.append("Speed Ranking (First Token - Lower is Faster):\n")
        summary_content.append("-" * 60 + "\n")
        
        model_speed = {}
        for model in models:
            model_results = [r for r in results if r['model'] == model and r['success']]
            if model_results:
                model_speed[model] = sum(r['first_token_time'] for r in model_results) / len(model_results)
        
        sorted_models_speed = sorted(model_speed.items(), key=lambda x: x[1])
        for i, (model, speed) in enumerate(sorted_models_speed, 1):
            summary_content.append(f"{i}. {model}: {speed:.2f}s\n")

        summary_content.append("\nQuality Ranking (AI Judge Rating - Higher is Better):\n")
        summary_content.append("-" * 60 + "\n")

        model_quality = {}
        for model in models:
            model_results = [r for r in results if r['model'] == model]
            judge_ratings = [r['judge_rating'] for r in model_results if 'judge_rating' in r and r['judge_rating'] > 0]
            if judge_ratings:
                model_quality[model] = sum(judge_ratings) / len(judge_ratings)
        
        if model_quality:
            sorted_models_quality = sorted(model_quality.items(), key=lambda x: x[1], reverse=True)
            for i, (model, quality) in enumerate(sorted_models_quality, 1):
                summary_content.append(f"{i}. {model}: {quality:.2f}/5\n")
        else:
            summary_content.append("No AI Judge ratings available (ensure Gemini API key is correct and judge model is active).\n")
            
        final_summary = "\n".join(summary_content)
        print(final_summary)
        
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(final_summary)

    def save_results(self, results: List[Dict[str, Any]], filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            filename = f"ollama_tools_raw_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Ensure 'response' and 'error' keys are always present and handle non-serializable objects
        serializable_results = []
        for res in results:
            serializable_res = res.copy()
            # Ensure all relevant fields are serializable
            if 'error' in serializable_res and isinstance(serializable_res['error'], Exception):
                serializable_res['error'] = str(serializable_res['error'])
            serializable_results.append(serializable_res)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"Raw results saved to: {filename}")

    def get_all_models_with_detailed_metadata(self) -> List[Dict[str, Any]]:
        """Pobierz szczegółowe metadane wszystkich modeli z Ollama"""
        try:
            models = ollama.list()
            detailed_models = []
            
            for model in models.models:
                try:
                    # Pobierz szczegółowe informacje o modelu
                    show_response = ollama.show(model.model)
                    model_data = {
                        'name': model.model,
                        'digest': model.digest,
                        'size': model.size,
                        'modified_at': str(model.modified_at),
                        'details': {
                            'family': model.details.family,
                            'parameter_size': model.details.parameter_size,
                            'quantization_level': model.details.quantization_level,
                            'format': model.details.format
                        },
                        'modelfile': show_response.get('modelfile', 'N/A')
                    }
                    detailed_models.append(model_data)
                except Exception as e:
                    print(f"Error getting details for model {model.model}: {e}")
            
            return detailed_models
        except Exception as e:
            print(f"Error getting models metadata: {e}")
            return []


def main():
    tester = OllamaToolsTester()
    
    print("Ollama Tools Tester")
    print("=" * 30)
    print("Available models for tool testing:")
    # Pobierz nazwy modeli do wyświetlenia
    available_ollama_models = tester.models
    for i, model in enumerate(available_ollama_models, 1):
        print(f"{i:2d}. {model}")
    
    print("\nOptions:")
    print("1. Run all tool tests on all models (with optional Gemini AI judge)")
    print("2. Run all tool tests on specific models (with optional Gemini AI judge)")
    print("3. Test a single model interactively (without AI judge)")
    print("4. List detailed metadata of all local Ollama models")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        tester.run_tests(use_gemini_judge=True)
        tester.save_results(tester.all_results, filename=f"ollama_tools_raw_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
    elif choice == "2":
        print("\nEnter model numbers to test (comma-separated, e.g. 1,3,5):")
        model_choices_input = input().strip().split(',')
        
        selected_models_names = []
        for choice_str in model_choices_input:
            try:
                idx = int(choice_str.strip()) - 1
                if 0 <= idx < len(tester.models):
                    selected_models_names.append(tester.models[idx])
            except ValueError:
                pass
        
        if selected_models_names:
            tester.run_tests(selected_models=selected_models_names, use_gemini_judge=True)
            tester.save_results(tester.all_results, filename=f"ollama_tools_raw_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        else:
            print("No valid models selected.")
    
    elif choice == "3":
        print("\nSelect a model:")
        for i, model in enumerate(tester.models, 1):
            print(f"{i:2d}. {model}")
        
        try:
            model_idx = int(input("Enter model number: ")) - 1
            if 0 <= model_idx < len(tester.models):
                model_name = tester.models[model_idx]
                
                print(f"\nTesting {model_name} interactively...")
                print("Enter prompts (empty line to quit):")
                
                while True:
                    prompt = input("\nPrompt: ").strip()
                    if not prompt:
                        break
                    
                    result = tester.ask_ollama_model(model_name, prompt) # Używamy ask_ollama_model
                    
                    if result['success']:
                        print(f"✓ Response ({result['response_time']:.2f}s):")
                        print(result['response'])
                        
                        if result['tools_used']:
                            print("\n🔧 Tools used:")
                            for tool in result['tools_used']:
                                print(f"  - {tool['name']}: {tool['result']}")
                    else:
                        print(f"✗ Error: {result['error']}")
            else:
                print("Invalid model number.")
        except ValueError:
            print("Invalid input.")
    
    elif choice == "4":
        detailed_metadata = tester.get_all_models_with_detailed_metadata()
        if detailed_metadata:
            print("\n--- DETAILED OLLAMA MODEL METADATA ---")
            for model_data in detailed_metadata:
                print(f"\nModel: {model_data.get('name', 'N/A')}")
                print(f"  Digest: {model_data.get('digest', 'N/A')}")
                print(f"  Size: {model_data.get('size', 'N/A')} bytes")
                print(f"  Modified: {model_data.get('modified_at', 'N/A')}")
                
                details = model_data.get('details', {})
                print(f"  Family: {details.get('family', 'N/A')}")
                print(f"  Parameter Size: {details.get('parameter_size', 'N/A')}")
                print(f"  Quantization Level: {details.get('quantization_level', 'N/A')}")
                print(f"  Model Type: {details.get('model_type', 'N/A')}")
                print(f"  Format: {details.get('format', 'N/A')}")
                # You can add more fields from 'details' or other keys if interesting
                # e.g. print(f"  Modelfile: {model_data.get('modelfile', 'N/A')[:100]}...") # Shortened version
        else:
            print("Failed to retrieve detailed Ollama model metadata.")
    
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
