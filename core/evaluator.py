import re
from models.local_inference import generate

def score_confidence(prompt: str, answer: str) -> int:
    """
    Ask the local model to rate the answer from 1-100.
    Runs on local GPU (0 tokens).
    """
    eval_prompt = f"""
    Question: {prompt}
    Proposed Answer: {answer}
    On a scale of 1 to 100, how accurate and relevant is this answer?
    Reply with ONLY the integer number.
    """
    result = generate(eval_prompt, max_new_tokens=20, temperature=0.1)
    # Extract number
    numbers = re.findall(r'\d+', result)
    if numbers:
        score = int(numbers[0])
        return min(100, max(0, score))  # Clamp 0-100
    return 50  # Default if parsing fails

def self_consistency_vote(prompt: str, answers: list) -> (str, int):
    """
    Takes 3 answers. If ≥2 agree (via embedding similarity), return best.
    Returns (best_answer, average_confidence)
    """
    from sentence_transformers import SentenceTransformer, util
    if len(answers) < 2:
        return answers[0], score_confidence(prompt, answers[0])
    
    # Use embedding similarity for free-form agreement
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = embedder.encode(answers, convert_to_tensor=True)
    sim_matrix = util.cos_sim(embeddings, embeddings)
    
    # Count agreements: if similarity > 0.85 between two answers, they agree
    best_idx = 0
    max_agreements = 0
    for i in range(len(answers)):
        agreements = sum(1 for j in range(len(answers)) if i != j and sim_matrix[i][j] > 0.85)
        if agreements > max_agreements:
            max_agreements = agreements
            best_idx = i
    
    # If at least 2 agree, return that with confidence
    if max_agreements >= 1:  # At least one other agrees
        avg_conf = (score_confidence(prompt, answers[best_idx]) + 
                   score_confidence(prompt, answers[(best_idx+1)%3])) // 2
        return answers[best_idx], avg_conf
    
    # No agreement: return the one with highest individual confidence
    confs = [score_confidence(prompt, ans) for ans in answers]
    best_idx = confs.index(max(confs))
    return answers[best_idx], max(confs)
