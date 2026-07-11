import os
import requests
from dotenv import load_dotenv

# Load .env FIRST so the API key is available
load_dotenv()

# Read Fireworks API key from environment
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY or FIREWORKS_API_KEY == "YOUR_API_KEY_HERE":
    print("⚠️  WARNING: FIREWORKS_API_KEY not found or is placeholder. Set it in .env")
    FIREWORKS_API_KEY = "MISSING_KEY"

FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"

def call_fireworks(prompt: str, rung: str) -> str:
    """
    Calls Fireworks AI serverless API.
    Uses config.py for model names, token caps, and system prompts.
    """
    from config import RUNG_MODELS, RUNG_MAX_TOKENS, RUNG_PROMPTS
    
    model = RUNG_MODELS.get(rung)
    if not model:
        return ""
    
    max_tokens = RUNG_MAX_TOKENS.get(rung, 120)
    system_prompt = RUNG_PROMPTS.get(rung, "Provide a clear answer.")
    
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
        "temperature": 0.0
    }
    
    try:
        response = requests.post(
            f"{FIREWORKS_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        print(f"[Fireworks] HTTP {response.status_code} on {rung}")
        
        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"].strip()
            print(f"[Fireworks] Output: {result[:50]}...")
            return result
        else:
            print(f"[Fireworks] Error: {response.text[:200]}")
            return ""
    except Exception as e:
        print(f"[Fireworks] Exception: {e}")
        return ""
