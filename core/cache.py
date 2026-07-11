from sentence_transformers import SentenceTransformer, util
import json
from pathlib import Path
from core.heuristics import entity_aware_match
from config import SEMANTIC_SIMILARITY_THRESHOLD

# Load the tiny 80MB model ONCE (runs on CPU)
_embedder = None
_semantic_cache_data = []  # list of {"prompt": "...", "answer": "..."}
_semantic_cache_embeddings = None

def load_semantic_cache():
    global _embedder, _semantic_cache_data, _semantic_cache_embeddings
    if _embedder is None:
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load your pre-built semantic knowledge base (optional)
    cache_path = Path(__file__).parent.parent / "semantic_cache.json"
    if cache_path.exists() and not _semantic_cache_data:
        with open(cache_path, 'r') as f:
            _semantic_cache_data = json.load(f)
        prompts = [item["prompt"] for item in _semantic_cache_data]
        _semantic_cache_embeddings = _embedder.encode(prompts, convert_to_tensor=True)

def semantic_lookup(prompt: str):
    """Fallback fuzzy cache with entity diff check."""
    load_semantic_cache()
    if not _semantic_cache_data:
        return None
    
    prompt_emb = _embedder.encode(prompt, convert_to_tensor=True)
    similarities = util.cos_sim(prompt_emb, _semantic_cache_embeddings)[0]
    best_score = similarities.max().item()
    best_idx = similarities.argmax().item()
    
    if best_score >= SEMANTIC_SIMILARITY_THRESHOLD:
        cached_entry = _semantic_cache_data[best_idx]
        # Claude's fix: verify numbers/entities match before returning
        if entity_aware_match(prompt, cached_entry["prompt"]):
            return cached_entry["answer"]
    return None
