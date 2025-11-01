# Reads git diff and extracts added hunks with file path and starting line
# Note: comments have no diacritics
from git import Repo
import re
from pathlib import Path

def get_changed_hunks(staged: bool = False):
    repo = Repo(Path(".").resolve())
    diff_text = repo.git.diff("--staged", "--unified=0") if staged else repo.git.diff("--unified=0")
    files = []
    for block in diff_text.split("\ndiff --git ")[1:]:
        header = block.split("\n", 1)[0]
        m = re.search(r"a/(.+?) b/(.+)$", header)
        if not m:
            continue
        path = m.group(2)
        lang = Path(path).suffix.lstrip(".") or "text"
        hunks = list(re.finditer(r"^@@ .* \+(\d+)(?:,(\d+))? @@", block, re.M))
        parts = re.split(r"^@@ .* @@", block, flags=re.M)[1:]
        for i, h in enumerate(hunks):
            start = int(h.group(1))
            after = parts[i] if i < len(parts) else ""
            lines = [l[1:] for l in after.splitlines() if l.startswith("+") and not l.startswith("+++")]
            if lines:
                files.append({"path": path, "added": "\n".join(lines), "startLine": start, "lang": lang})
    return files
