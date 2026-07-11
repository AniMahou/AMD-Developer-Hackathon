import re

def classify_task(prompt: str):
    """
    Returns (difficulty, schema)
    difficulty: 'easy', 'medium', 'hard'
    schema: 'number', 'json', 'choice', 'text'
    """
    prompt_lower = prompt.lower()
    
    # --- Schema Detection ---
    if "json" in prompt_lower or "provide json" in prompt_lower:
        schema = "json"
    elif re.search(r'[A-Da-d]\)', prompt) or "multiple choice" in prompt_lower:
        schema = "choice"
    elif re.search(r'what is \d+', prompt_lower) or "calculate" in prompt_lower or "sum" in prompt_lower:
        schema = "number"
    else:
        schema = "text"
    
    # --- Difficulty Detection ---
    # Hard: long prompts, complex reasoning, coding
    if len(prompt) > 500 or "reason" in prompt_lower or "explain" in prompt_lower or "code" in prompt_lower:
        difficulty = "hard"
    # Medium: math, specific facts
    elif "calculate" in prompt_lower or "solve" in prompt_lower or len(prompt) > 200:
        difficulty = "medium"
    else:
        difficulty = "easy"
    
    return difficulty, schema
