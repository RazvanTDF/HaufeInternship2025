# Minimal Ollama client using local REST API
import requests

def ask_ollama(model: str, prompt: str) -> str:
    url = "http://127.0.0.1:11434/api/generate"
    res = requests.post(url, json={"model": model, "prompt": prompt, "stream": False}, timeout=300)
    res.raise_for_status()
    return res.json().get("response", "")
