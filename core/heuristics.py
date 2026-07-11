import json
import re
from pathlib import Path

# Load the golden cache (built offline with 405B)
GOLDEN_CACHE_PATH = Path(__file__).parent.parent / "golden_cache.json"
_golden_cache = {}

def load_golden_cache():
    global _golden_cache
    if GOLDEN_CACHE_PATH.exists():
        with open(GOLDEN_CACHE_PATH, 'r') as f:
            _golden_cache = json.load(f)
    else:
        _golden_cache = {}

def exact_match_lookup(prompt: str):
    """Phase 2: Exact match against offline 405B answers."""
    load_golden_cache()
    return _golden_cache.get(prompt.strip(), None)

def structural_verifier(answer: str, schema: str) -> bool:
    """
    Phase 5: Free deterministic check before confidence scoring.
    schema: 'number', 'json', 'choice', 'text'
    """
    if schema == 'number':
        # Check if answer is a number (with or without decimal)
        return bool(re.match(r'^-?\d+(\.\d+)?$', answer.strip()))
    elif schema == 'json':
        try:
            json.loads(answer.strip())
            return True
        except:
            return False
    elif schema == 'choice':
        # Single letter A, B, C, D etc.
        return bool(re.match(r'^[A-Da-d]$', answer.strip()))
    else:  # 'text' - always valid if non-empty
        return len(answer.strip()) > 0

def entity_aware_match(prompt: str, cached_prompt: str) -> bool:
    """
    Claude's fix: Before accepting a semantic cache hit, check if numbers/entities changed.
    e.g., '2+2' vs '2+3' should NOT match.
    """
    # Extract all numbers
    numbers1 = set(re.findall(r'\d+', prompt))
    numbers2 = set(re.findall(r'\d+', cached_prompt))
    if numbers1 != numbers2:
        return False  # Numbers differ, can't trust cache
    
    # Extract all proper nouns (capitalized words)
    nouns1 = set(re.findall(r'\b[A-Z][a-z]+\b', prompt))
    nouns2 = set(re.findall(r'\b[A-Z][a-z]+\b', cached_prompt))
    if nouns1 != nouns2:
        return False
    
    return True  # Safe to use cache
