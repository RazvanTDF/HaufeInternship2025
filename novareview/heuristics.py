# Deterministic checks and autofix for Python. No diacritics in comments.
import re

def analyze_py(code: str):
    fixes = []
    suggestions = []
    lines = code.splitlines()

    # 0) helpers
    def add_s(line, msg): suggestions.append({"lineOffset": line, "message": msg})

    # 1) bare except -> except Exception:
    for i, l in enumerate(lines):
        if re.match(r'^\s*except\s*:\s*$', l):
            fixes.append({
                "lineOffset": i,
                "message": "Replace bare `except:` with `except Exception:`",
                "suggestion": l.replace("except:", "except Exception:")
            })

    # 2) open(...) without context manager
    if "open(" in code and not re.search(r'with\s+open\(.+\)\s+as\s+\w+\s*:', code):
        add_s(0, "Use context manager: `with open(...) as f:` to avoid leaks.")

    # 3) requests.* without timeout=
    if re.search(r'\brequests\.(get|post|put|delete|patch)\(', code) and "timeout=" not in code:
        add_s(0, "Provide a `timeout=` in requests calls.")

    # 4) range(len(...)) -> enumerate
    if re.search(r'\bfor\s+\w+\s+in\s+range\(\s*len\(.+\)\s*\)\s*:', code):
        add_s(0, "Prefer `for i, item in enumerate(seq):` over `range(len(seq))`.")

    # 5) string concat -> f-strings
    if re.search(r'print\(\s*".*"\s*\+\s*', code):
        add_s(0, "Prefer f-strings over string concatenation.")

    # 6) URL building via '+' instead of f-strings
    m = re.search(r'url\s*=\s*["\']https?://[^"\']+["\']\s*\+\s*\w+', code)
    if m:
        add_s(0, "Build URLs with f-strings or urllib.parse; avoid string concatenation.")

    # 7) unsafe json parsing: json.loads(r.text) instead of r.json()
    if re.search(r'json\.loads\(\s*\w+\.text\s*\)', code):
        add_s(0, "Use `response.json()` instead of `json.loads(response.text)`.")

    # 8) missing error handling on non-200
    if re.search(r'if\s+\w+\.status_code\s*==\s*200:', code) and "else" in code and "raise" not in code:
        add_s(0, "Consider raising for non-200 responses or returning a structured error.")

    # 9) logic bug pattern: discount computed as price * percent / 100
    if re.search(r'\breturn\s+\w+\s*\*\s*\w+\s*/\s*100\b', code):
        add_s(0, "Discount logic: final price should likely be `price * (1 - percent/100)`.")

    return fixes, suggestions

def apply_py_fixes(content: str) -> str:
    # Apply only safe replacements here.
    content = re.sub(r'^\s*except\s*:\s*$', 'except Exception:', content, flags=re.M)
    return content
