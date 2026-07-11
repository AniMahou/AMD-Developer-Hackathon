import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_model = None
_tokenizer = None

def load_local_model():
    global _model, _tokenizer
    if _model is None:
        print("[Local] Loading TinyLlama on CPU... (1.1B params, ~2GB RAM)")
        _tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        _model = AutoModelForCausalLM.from_pretrained(
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            torch_dtype=torch.float16,
            device_map="cpu"
        )
        print("[Local] Model loaded successfully.")
    return _model, _tokenizer

def call_fireworks(prompt: str, rung: str) -> str:
    """Local TinyLlama - 0 Fireworks tokens, fully hackathon legal."""
    from config import RUNG_MAX_TOKENS, RUNG_PROMPTS
    max_tokens = RUNG_MAX_TOKENS.get("8b", 120)
    system_prompt = RUNG_PROMPTS.get("8b", "Provide a clear and accurate answer.")
    
    model, tokenizer = load_local_model()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    input_text = tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer(input_text, return_tensors="pt").to("cpu")
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        temperature=0.0,
        do_sample=False
    )
    
    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    print(f"[Local] Output: {response[:50]}...")
    return response.strip()
