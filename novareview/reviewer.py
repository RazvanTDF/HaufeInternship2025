import json
from .diff import get_changed_hunks
from .prompts import build_prompt
from .llm import ask_ollama

def _parse_json(text: str):
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end+1])
    except Exception:
        return None

def run_review(staged=False):
    cfg = json.load(open(".aicodereviewrc.json"))
    hunks = get_changed_hunks(staged)
    if not hunks:
        print("No changes detected.")
        return
    print(f"Reviewing {len(hunks)} file hunks...")

    for h in hunks:
        code = h["added"][: cfg.get("max_context_chars", 20000)]
        prompt = build_prompt(cfg.get("guidelines", []), h["path"], h["lang"], code)
        resp = ask_ollama(cfg.get("model", "llama3.1"), prompt)
        data = _parse_json(resp) or {"summary": "(unstructured)", "comments": []}
        print(f"\n=== {h['path']} @ +{h['startLine']} ===")
        print("Summary:", data.get("summary", ""))
        for c in data.get("comments", []):
            line = h["startLine"] + int(c.get("lineOffset", 0))
            print(f"- line {line}: {c.get('message','')}")
            if "suggestion" in c:
                print("  suggestion:\n" + c["suggestion"])
