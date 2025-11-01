import json, sys, pathlib
from .diff import get_changed_hunks
from .prompts import build_prompt
from .llm import ask_ollama
from .heuristics import analyze_py, apply_py_fixes

def _parse_json(text: str):
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        return None
    try:
        return json.loads(text[s:e+1])
    except Exception:
        return None

def _is_safe_llm_comment(lang: str, message_lower: str) -> bool:
    # Allowlist of LLM hints we accept; drop noisy advice
    allowed_fragments = [
        "context manager", "timeout", "enumerate", "f-strings", "null", "none",
        "sanitize", "validate input", "exception", "try/catch", "error handling"
    ]
    banned_fragments = [
        "str.join", "validate import", "zip(items", "empty string import"
    ]
    if any(b in message_lower for b in banned_fragments):
        return False
    if lang in ("py", "python"):
        return any(a in message_lower for a in allowed_fragments)
    return True

def run_review(staged=False, apply=False):
    cfg = json.load(open(".aicodereviewrc.json"))
    max_chars = int(cfg.get("max_context_chars", 4000))
    model = cfg.get("model", "llama3.2:1b")

    hunks = get_changed_hunks(staged)
    if not hunks:
        print("No changes detected.")
        return

    print(f"Reviewing {len(hunks)} file hunks...")
    files_to_autofix = set()

    try:
        for i, h in enumerate(hunks, start=1):
            print(f"[{i}/{len(hunks)}] {h['path']} @ +{h['startLine']} ...", flush=True)
            code = (h["added"] or "")[:max_chars]

            # 1) deterministic layer
            det_fixes, det_sugs = ([], [])
            if h["lang"] in ("py", "python"):
                det_fixes, det_sugs = analyze_py(code)
                if apply and det_fixes:
                    files_to_autofix.add(h["path"])

            # 2) LLM layer
            prompt = build_prompt(cfg.get("guidelines", []), h["path"], h["lang"], code)
            out = ask_ollama(model, prompt)
            data = _parse_json(out) or {"summary": "(unstructured)", "comments": []}

            # 3) merge results: heuristics (reliable) + filtered LLM
            merged = []
            merged.extend(det_fixes)  # include suggestions as quick fixes
            merged.extend(det_sugs)
            for c in data.get("comments", []):
                msg = str(c.get("message", ""))
                if _is_safe_llm_comment(h["lang"], msg.lower()):
                    merged.append(c)

            print(f"\n=== {h['path']} @ +{h['startLine']} ===")
            print("Summary:", data.get("summary", ""))
            for c in merged:
                line = h["startLine"] + int(c.get("lineOffset", 0))
                print(f"- line {line}: {c.get('message','')}")
                if "suggestion" in c:
                    print("  suggestion:\n" + c["suggestion"])
            print("")

        # 4) optional autofix (safe replacements on full files)
        if apply and files_to_autofix:
            for rel in sorted(files_to_autofix):
                p = pathlib.Path(rel)
                try:
                    text = p.read_text(encoding="utf-8")
                    fixed = text
                    # apply safe Python fixes
                    fixed = apply_py_fixes(fixed)
                    if fixed != text:
                        p.write_text(fixed, encoding="utf-8")
                        print(f"[autofix] applied safe fixes to {rel}")
                except Exception as e:
                    print(f"[autofix] failed for {rel}: {e}", file=sys.stderr)

    except KeyboardInterrupt:
        print("\nInterrupted by user. Partial results printed.", file=sys.stderr)
