import os
from dotenv import load_dotenv

load_dotenv()

FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "YOUR_API_KEY_HERE")
FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"

# CORRECT SERVERLESS MODEL NAMES (DO NOT CHANGE)
RUNG_MODELS = {
    "8b": "accounts/fireworks/models/llama-v3p1-8b-instruct",
    "70b": "accounts/fireworks/models/llama-v3p1-70b-instruct"
}

# RUTHLESS TOKEN CAPS: Force 1-word or 1-sentence answers
RUNG_MAX_TOKENS = {
    "8b": 15,   # Max 3-5 tokens (e.g., "Paris", "42")
    "70b": 40   # Max 1 short sentence (e.g., "The capital is Paris.")
}

# BRUTAL SYSTEM PROMPTS: No fluff, no explanations.
RUNG_PROMPTS = {
    "8b": "Reply with ONLY the direct answer. 1-3 words maximum. No explanations. Never say 'I think' or 'As an AI'.",
    "70b": "Reply with ONE short sentence (max 10 words). No explanations. No bullet points. Just the direct answer."
}

# Keyword router: if prompt contains these, use 70b (hard tasks)
KEYWORD_70B = ["code", "algorithm", "explain", "reason", "solve", "calculate complex"]

# Semantic cache threshold
SEMANTIC_SIMILARITY_THRESHOLD = 0.92
