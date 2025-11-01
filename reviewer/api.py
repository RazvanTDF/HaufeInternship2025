# reviewer/api.py
# FastAPI endpoint for the web MVP. No diacritics in comments.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from novareview.prompts import build_prompt
from novareview.llm import ask_ollama
from novareview.heuristics import analyze_py

app = FastAPI(title="NovaReview API", version="0.1.0")

# Relaxed CORS for local demo and file:// browser usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
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
    # load config if present
    try:
        cfg = json.load(open(".aicodereviewrc.json", "r"))
    except Exception:
        cfg = {"model": "llama3.2:1b", "max_context_chars": 4000, "guidelines": []}

    # deterministic layer (python only for now)
    fixes, sugs = [], []
    if inp.lang in ("py", "python"):
        fixes, sugs = analyze_py(inp.code)

    # optional LLM layer (local via Ollama)
    code = inp.code[: int(cfg.get("max_context_chars", 4000))]
    prompt = build_prompt(cfg.get("guidelines", []), inp.path, inp.lang, code)
    out = ask_ollama(cfg.get("model", "llama3.2:1b"), prompt)

    # try to extract JSON object from model response
    s, e = out.find("{"), out.rfind("}")
    data = {"summary": "(unstructured)", "comments": []}
    if s != -1 and e != -1:
        try:
            data = json.loads(out[s : e + 1])
        except Exception:
            pass

    # merge deterministic findings first (more reliable), then LLM comments
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

    return {"summary": data.get("summary", ""), "comments": comments}
