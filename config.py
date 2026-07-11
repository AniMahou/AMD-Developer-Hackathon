import os

# Fireworks AI
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "YOUR_API_KEY_HERE")
FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"

# The Escalation Ladder (Cheapest to Expensive)
RUNG_MODELS = {
    "8b": "accounts/fireworks/models/llama-v3p1-8b-instruct",
    "70b": "accounts/fireworks/models/llama-v3p1-70b-instruct",
    "405b": "accounts/fireworks/models/llama-v3p1-405b-instruct"
}

# Per-rung system prompts (Claude's advice: tune differently per rung)
# 8B needs more structure/examples; 405B can be terse.
RUNG_PROMPTS = {
    "8b": "You are a helpful assistant. Answer accurately. Keep it very short (1-2 sentences). If the answer requires a specific format (JSON, number, or letter), follow that format strictly.",
    "70b": "You are an expert. Provide a concise answer in 2-3 sentences. Do not ramble.",
    "405b": "You are a world-class expert. Solve this accurately. Keep the final answer extremely brief and to the point."
}

# Max output tokens per rung to cap Fireworks spending
RUNG_MAX_TOKENS = {
    "8b": 80,
    "70b": 120,
    "405b": 200
}

# Local Model (small enough for AMD GPU)
LOCAL_MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"

# Thresholds
CONFIDENCE_THRESHOLD = 85   # Out of 100. If local confidence >= this, submit.
SEMANTIC_SIMILARITY_THRESHOLD = 0.92  # For fuzzy cache fallback

# System prompt for local generation (costs 0 tokens, so length doesn't matter)
LOCAL_SYSTEM_PROMPT = "You are a precise assistant. Answer the user's question accurately and concisely."
