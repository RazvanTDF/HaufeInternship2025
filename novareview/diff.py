# Reads git diff and extracts added hunks with file path and starting line
# Robust parser for staged/unstaged diffs, multiple hunks per file
from git import Repo
import re
from pathlib import Path

HUNK_RE = re.compile(r"@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,(\d+))?\s+@@")

def get_changed_hunks(staged: bool = False):
    repo = Repo(Path(".").resolve())

    args = ["--unified=0"]
    if staged:
        args.insert(0, "--staged")

    diff_text = repo.git.diff(*args)
    if not diff_text.strip():
        return []

    hunks = []
    current_file = None
    current_hunk_index = -1

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            m = re.search(r"a/(.+?) b/(.+)$", line)
            current_file = m.group(2) if m else None
            current_hunk_index = -1
            continue

        if not current_file:
            continue

        if line.startswith("@@"):
            m = HUNK_RE.search(line)
            if not m:
                continue
            start_new = int(m.group(1))
            lang = Path(current_file).suffix.lstrip(".") or "text"
            hunks.append({"path": current_file, "added": "", "startLine": start_new, "lang": lang})
            current_hunk_index += 1
            continue

        if current_hunk_index >= 0 and line.startswith("+") and not line.startswith("+++"):
            hunks[current_hunk_index]["added"] += line[1:] + "\n"

    return [h for h in hunks if h["added"].strip()]
