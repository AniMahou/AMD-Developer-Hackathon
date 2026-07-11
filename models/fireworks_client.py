import requests
from config import (
    FIREWORKS_API_KEY, FIREWORKS_BASE_URL,
    RUNG_MODELS, RUNG_PROMPTS, RUNG_MAX_TOKENS
)

def call_fireworks(prompt: str, rung: str) -> str:
    """
    rung: '8b', '70b', or '405b'
    Uses different system prompts and max_tokens per rung.
    """
    model = RUNG_MODELS.get(rung)
    if not model:
        raise ValueError(f"Unknown rung: {rung}")
    
    system_prompt = RUNG_PROMPTS[rung]
    max_tokens = RUNG_MAX_TOKENS[rung]
    
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(
            f"{FIREWORKS_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[Fireworks Error] Rung {rung}: {e}")
        return ""  # Empty answer triggers fallback
