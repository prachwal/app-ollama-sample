"""
Result analysis and summary generation utilities.
"""

from typing import List, Dict, Any


def generate_summary(results: List[Dict[str, Any]], output_file: str) -> str:
    """
    Generuje podsumowanie wyników testów.
    
    Args:
        results (List[Dict[str, Any]]): Lista wyników testów
        output_file (str): Nazwa pliku wyjściowego
        
    Returns:
        str: Sformatowane podsumowanie
    """
    if not results:
        return ""
    
    summary = f"\n{'='*100}\n"
    summary += "PODSUMOWANIE WYNIKÓW\n"
    summary += f"{'='*100}\n\n"
    
    models = list(set(r['model'] for r in results))
    
    summary += "Średnie czasy odpowiedzi i oceny jakości:\n"
    summary += "-" * 60 + "\n"
    
    for model in models:
        model_results = [r for r in results if r['model'] == model]
        if model_results:
            avg_first_token = sum(r['first_token_time'] for r in model_results) / len(model_results)
            avg_total_time = sum(r['total_time'] for r in model_results) / len(model_results)
            avg_length = sum(r['response_length'] for r in model_results) / len(model_results)
            
            # Oblicz średnią ocenę sędziego, jeśli dostępne
            judge_ratings = [r['judge_rating'] for r in model_results if 'judge_rating' in r and r['judge_rating'] > 0]
            avg_judge_rating = sum(judge_ratings) / len(judge_ratings) if judge_ratings else "N/A"
            
            summary += f"{model}:\n"
            summary += f"  - Średni czas pierwszego tokena: {avg_first_token:.2f}s\n"
            summary += f"  - Średni całkowity czas: {avg_total_time:.2f}s\n"
            summary += f"  - Średnia długość odpowiedzi: {avg_length:.0f} znaków\n"
            summary += f"  - Zakończonych testów: {len(model_results)}\n"
            summary += f"  - Średnia ocena sędziego AI: {avg_judge_rating:.2f}/5\n" if isinstance(avg_judge_rating, float) else f"  - Średnia ocena sędziego AI: {avg_judge_rating}\n"
            summary += "\n"
    
    summary += "🏆 RANKING SZYBKOŚCI (pierwszy token - niżej = lepiej):\n"
    summary += "-" * 60 + "\n"
    
    model_speed = {}
    for model in models:
        model_results = [r for r in results if r['model'] == model]
        if model_results:
            model_speed[model] = sum(r['first_token_time'] for r in model_results) / len(model_results)
    
    sorted_models_speed = sorted(model_speed.items(), key=lambda x: x[1])
    for i, (model, speed) in enumerate(sorted_models_speed, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        summary += f"{medal} {i}. {model}: {speed:.2f}s\n"

    summary += f"\n🎖️ RANKING JAKOŚCI (ocena sędziego AI - wyżej = lepiej):\n"
    summary += "-" * 60 + "\n"

    model_quality = {}
    for model in models:
        model_results = [r for r in results if r['model'] == model]
        if model_results:
            judge_ratings = [r['judge_rating'] for r in model_results if 'judge_rating' in r and r['judge_rating'] > 0]
            if judge_ratings:
                model_quality[model] = sum(judge_ratings) / len(judge_ratings)
    
    if model_quality:
        sorted_models_quality = sorted(model_quality.items(), key=lambda x: x[1], reverse=True)
        for i, (model, quality) in enumerate(sorted_models_quality, 1):
            summary += f"{i}. {model}: {quality:.2f}/5\n"
    else:
        summary += "Brak danych o ocenach sędziego AI (upewnij się, że klucz API Gemini jest poprawny).\n"
    
    # Zapisz podsumowanie do pliku
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(summary)
    
    return summary
