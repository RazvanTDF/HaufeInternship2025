# reviewer/api.py
# FastAPI endpoint for the web MVP. No diacritics in comments.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import time

from novareview.prompts import build_prompt
from novareview.llm import ask_ollama
from novareview.heuristics import analyze_py

app = FastAPI(title="NovaReview API", version="0.1.0")

# Relaxed CORS for local demo and file:// browser usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],  # includes OPTIONS so browsers can preflight
    allow_headers=["*"],
)

class ReviewIn(BaseModel):
    code: str
    lang: str = "text"
    path: str = "pasted"

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/review")
def review(inp: ReviewIn):
    # Load config if present
    try:
        cfg = json.load(open(".aicodereviewrc.json", "r"))
    except Exception:
        cfg = {
            "model": "llama3.1",
            "max_context_chars": 4000,
            "guidelines": [],
            # metrics defaults (safe if missing)
            "price_per_mtok_usd": 0.0,  # 0 => show cost as 0 (local model)
            "chars_per_token": 4
        }

    model_name = cfg.get("model", "llama3.1")
    max_ctx = int(cfg.get("max_context_chars", 4000))
    price_per_mtok = float(cfg.get("price_per_mtok_usd", 0.0))
    chars_per_token = int(cfg.get("chars_per_token", 4))

    # Deterministic layer (python only for now)
    fixes, sugs = [], []
    if inp.lang in ("py", "python"):
        try:
            fixes, sugs = analyze_py(inp.code)
        except Exception:
            fixes, sugs = [], []

    # LLM layer (local via Ollama) + metrics
    code = inp.code[:max_ctx]
    prompt = build_prompt(cfg.get("guidelines", []), inp.path, inp.lang, code)

    prompt_chars = len(prompt)
    t0 = time.time()
    out = ""
    try:
        out = ask_ollama(model_name, prompt)
    except Exception:
        # keep going even if LLM layer fails
        out = ""
    duration_ms = int((time.time() - t0) * 1000)
    response_chars = len(out)

    # Try to extract JSON object from model response
    s, e = out.find("{"), out.rfind("}")
    data = {"summary": "(unstructured)", "comments": []}
    if s != -1 and e != -1:
        try:
            data = json.loads(out[s : e + 1])
        except Exception:
            pass

    # Merge deterministic findings first (more reliable), then LLM comments
    comments = []
    for f in fixes:
        comments.append({
            "lineOffset": f.get("lineOffset", 0),
            "message": f.get("message", ""),
            "suggestion": f.get("suggestion")
        })
    for s_ in sugs:
        comments.append({
            "lineOffset": s_.get("lineOffset", 0),
            "message": s_.get("message", "")
        })
    for c in data.get("comments", []):
        comments.append(c)

    # Metrics: token estimates and cost
    prompt_tokens_est = max(1, prompt_chars // chars_per_token) if prompt_chars else 0
    response_tokens_est = max(1, response_chars // chars_per_token) if response_chars else 0
    total_tokens_est = prompt_tokens_est + response_tokens_est
    cost_usd_est = round((total_tokens_est / 1_000_000.0) * price_per_mtok, 6) if price_per_mtok else 0.0

    metrics = {
        "model": model_name,
        "prompt_chars": prompt_chars,
        "response_chars": response_chars,
        "prompt_tokens_est": prompt_tokens_est,
        "response_tokens_est": response_tokens_est,
        "chars_per_token": chars_per_token,
        "duration_ms": duration_ms,
        "price_per_mtok_usd": price_per_mtok,
        "cost_usd_est": cost_usd_est,
    }

    return {
        "summary": data.get("summary", ""),
        "comments": comments,
        "metrics": metrics,
    }
