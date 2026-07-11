from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from config import LOCAL_MODEL_NAME, LOCAL_SYSTEM_PROMPT

_model = None
_tokenizer = None

def load_model():
    global _model, _tokenizer
    if _model is None:
        print(f"[Local] Loading {LOCAL_MODEL_NAME}... This may take 5 minutes.")
        _tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_NAME, trust_remote_code=True)
        _model = AutoModelForCausalLM.from_pretrained(
            LOCAL_MODEL_NAME,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto"  # Uses AMD GPU if available
        )
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token
        print("[Local] Model loaded successfully.")
    return _model, _tokenizer

def generate(prompt: str, max_new_tokens=256, temperature=0.2):
    """Generate an answer using the local model."""
    model, tokenizer = load_model()
    messages = [
        {"role": "system", "content": LOCAL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    inputs = tokenizer.apply_chat_template(messages, return_tensors="pt").to(model.device)
    outputs = model.generate(
        inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
    return response.strip()
