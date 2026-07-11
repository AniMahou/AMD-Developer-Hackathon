from core.heuristics import exact_match_lookup, structural_verifier
from core.task_classifier import classify_task
from core.cache import semantic_lookup
from models.local_inference import generate as local_generate
from models.fireworks_client import call_fireworks
from core.evaluator import score_confidence, self_consistency_vote
from config import CONFIDENCE_THRESHOLD, RUNG_MODELS

def process_task(prompt: str):
    """
    The full cascade:
    1. Exact-match cache (golden)
    2. Task classification (skip rung prep)
    3. Semantic cache (fallback)
    4. Adaptive local (1 sample → structural → confidence → optional 2 more)
    5. Fireworks escalation (skip rungs based on difficulty)
    """
    prompt_stripped = prompt.strip()
    
    # ---- PHASE 1: EXACT MATCH (0 tokens, 100% accurate) ----
    golden = exact_match_lookup(prompt_stripped)
    if golden:
        print("[Cache] Exact hit (0 tokens)")
        return golden
    
    # ---- PHASE 2: CLASSIFY (free) ----
    difficulty, schema = classify_task(prompt_stripped)
    print(f"[Classify] {difficulty} | schema: {schema}")
    
    # ---- PHASE 3: SEMANTIC CACHE (fallback, 0 tokens) ----
    semantic = semantic_lookup(prompt_stripped)
    if semantic:
        # Structural verifier on semantic answer just to be safe
        if structural_verifier(semantic, schema):
            print("[Cache] Semantic hit (0 tokens)")
            return semantic
    
    # ---- PHASE 4: LOCAL MODEL (0 tokens) ----
    print("[Local] Generating 1st sample...")
    answer1 = local_generate(prompt_stripped, max_new_tokens=200, temperature=0.2)
    
    # Structural check first (free gate)
    if structural_verifier(answer1, schema):
        conf1 = score_confidence(prompt_stripped, answer1)
        print(f"[Local] Confidence: {conf1}")
        
        if conf1 >= CONFIDENCE_THRESHOLD:
            print("[Local] PASSED (0 tokens)")
            return answer1
        
        # BORDERLINE: Generate 2 more for self-consistency
        if conf1 >= 60:  # Only if it's borderline, not total garbage
            print("[Local] Borderline, generating 2 more samples...")
            answer2 = local_generate(prompt_stripped, max_new_tokens=200, temperature=0.5)
            answer3 = local_generate(prompt_stripped, max_new_tokens=200, temperature=0.8)
            best, avg_conf = self_consistency_vote(prompt_stripped, [answer1, answer2, answer3])
            if avg_conf >= CONFIDENCE_THRESHOLD:
                print(f"[Local] Self-consistency PASSED (avg {avg_conf}, 0 tokens)")
                return best
    else:
        print("[Local] Failed structural verifier.")
    
    # ---- PHASE 5: FIREWORKS ESCALATION (Skip rungs) ----
    # Map difficulty to starting rung
    start_rung = {"easy": "8b", "medium": "70b", "hard": "405b"}.get(difficulty, "8b")
    rung_order = ["8b", "70b", "405b"]
    start_idx = rung_order.index(start_rung)
    
    print(f"[Fireworks] Starting at {start_rung} (skipping previous rungs)")
    
    for rung in rung_order[start_idx:]:
        print(f"[Fireworks] Trying {rung}...")
        fw_answer = call_fireworks(prompt_stripped, rung)
        
        if not fw_answer:
            continue  # Empty answer, skip to next rung
        
        # Structural verify
        if not structural_verifier(fw_answer, schema):
            print(f"[Fireworks] {rung} failed structural check.")
            continue
        
        # Confidence check
        conf = score_confidence(prompt_stripped, fw_answer)
        print(f"[Fireworks] {rung} confidence: {conf}")
        
        if conf >= CONFIDENCE_THRESHOLD:
            print(f"[Fireworks] {rung} PASSED")
            return fw_answer
    
    # ---- PHASE 6: ABSOLUTE LAST RESORT ----
    # If even 405B fails, force a direct raw prompt with self-correction
    print("[Fallback] Last resort: raw 405B with self-correction")
    fallback_prompt = f"Question: {prompt_stripped}\nProvide the correct answer concisely:"
    fallback_answer = call_fireworks(fallback_prompt, "405b")
    return fallback_answer if fallback_answer else "ERROR: Unable to generate answer."
