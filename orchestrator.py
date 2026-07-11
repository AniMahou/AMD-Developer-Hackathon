from core.heuristics import exact_match, keyword_router, structural_verifier
from core.cache import semantic_lookup
from models.fireworks_client import call_fireworks

def process_task(prompt: str) -> str:
    prompt = prompt.strip()
    
    # 1. EXACT MATCH (0 tokens)
    cached = exact_match(prompt)
    if cached:
        print("[Cache] Exact hit! 0 tokens.")
        return cached
    
    # 2. SEMANTIC CACHE (0 tokens)
    semantic = semantic_lookup(prompt)
    if semantic:
        return semantic
    
    # 3. KEYWORD ROUTER
    chosen_rung = keyword_router(prompt)
    print(f"[Router] Routing to {chosen_rung}.")
    
    # 4. PRIMARY CALL
    answer = call_fireworks(prompt, chosen_rung)
    if structural_verifier(answer):
        print("[OK] Primary passed.")
        return answer
    
    # 5. FALLBACK (try the other rung)
    fallback_rung = "70b" if chosen_rung == "8b" else "8b"
    print(f"[Fallback] Trying {fallback_rung}.")
    fallback_answer = call_fireworks(prompt, fallback_rung)
    
    if structural_verifier(fallback_answer):
        print("[OK] Fallback passed.")
        return fallback_answer
    
    # 6. LAST RESORT: Return whatever we got (even if it failed structural)
    # Better to submit something than nothing.
    if answer:
        return answer
    if fallback_answer:
        return fallback_answer
    
    return "No answer generated."
