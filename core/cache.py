import re
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from config import SEMANTIC_SIMILARITY_THRESHOLD

# Load the 80MB embedding model ONCE on CPU (uses ~500MB RAM, fits in 4GB)
_embedder = None
_semantic_data = []
_semantic_embeddings = None

def load_semantic_cache():
    global _embedder, _semantic_data, _semantic_embeddings
    if _embedder is None:
        print("[Cache] Loading 80MB embedding model on CPU...")
        _embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    
    cache_path = Path(__file__).parent.parent / "semantic_cache.json"
    if cache_path.exists() and not _semantic_data:
        with open(cache_path, 'r') as f:
            _semantic_data = json.load(f)  # List of {"prompt": "text", "answer": "text"}
        prompts = [item["prompt"] for item in _semantic_data]
        _semantic_embeddings = _embedder.encode(prompts, convert_to_tensor=True)
        print(f"[Cache] Loaded {len(_semantic_data)} semantic entries.")

def semantic_lookup(prompt: str):
    load_semantic_cache()
    if not _semantic_data or _semantic_embeddings is None:
        return None
    
    prompt_emb = _embedder.encode(prompt, convert_to_tensor=True)
    similarities = util.cos_sim(prompt_emb, _semantic_embeddings)[0]
    best_score = similarities.max().item()
    best_idx = similarities.argmax().item()
    
    if best_score >= SEMANTIC_SIMILARITY_THRESHOLD:
        cached_prompt = _semantic_data[best_idx]["prompt"]
        # Entity diff check (prevents matching "2+2" with "2+3")
        nums1 = set(re.findall(r'\d+', prompt))
        nums2 = set(re.findall(r'\d+', cached_prompt))
        if nums1 == nums2:
            print(f"[Cache] Semantic hit! Score: {best_score:.2f} (0 tokens)")
            return _semantic_data[best_idx]["answer"]
    return None
