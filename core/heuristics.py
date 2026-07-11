import json
import re
from pathlib import Path
from config import KEYWORD_70B

GOLDEN_PATH = Path(__file__).parent.parent / "golden_cache.json"
_golden_cache = {}

def load_cache():
    global _golden_cache
    if GOLDEN_PATH.exists():
        with open(GOLDEN_PATH, 'r') as f:
            _golden_cache = json.load(f)
    else:
        _golden_cache = {}

def exact_match(prompt: str):
    load_cache()
    return _golden_cache.get(prompt.strip(), None)

def keyword_router(prompt: str) -> str:
    prompt_lower = prompt.lower()
    for keyword in KEYWORD_70B:
        if keyword in prompt_lower:
            return "70b"
    return "8b"

def structural_verifier(answer: str) -> bool:
    """Loosened: Only reject if empty or clearly a refusal."""
    if not answer or len(answer.strip()) < 2:
        return False
    # Only reject obvious refusals, not actual content.
    refuse = ["i cannot", "i'm sorry", "as an ai", "i don't have", "unable to"]
    if any(k in answer.lower() for k in refuse):
        return False
    return True
