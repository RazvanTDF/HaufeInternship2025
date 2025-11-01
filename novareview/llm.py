# Minimal Ollama client using local REST API (fast mode)
import requests

def ask_ollama(model: str, prompt: str) -> str:
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": 2048,
            "num_predict": 256,
            "temperature": 0.2,
        },
    }
    try:
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()
        return res.json().get("response", "")
    except requests.exceptions.Timeout:
        return '{"summary":"timeout after 30s","comments":[]}'
    except Exception as e:
        return f'{{"summary":"ollama error: {str(e)}","comments":[]}}'
