# NovaReview – AI Code Reviewer (Python)

Minimal, local-first AI code reviewer powered by Ollama. Reviews only changed hunks from your git diff.

## Quick start

1) (Optional but recommended) Create a virtualenv
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install package (editable) and deps
```bash
pip install -e .
```

3) Install Ollama and pull a model (local)
```bash
ollama pull llama3.1
```

4) Run the reviewer
```bash
novareview            # on current diff
novareview --staged   # only staged files (pre-commit style)
```

## Config

Edit `.aicodereviewrc.json` to change the model, context limits, and guidelines.

## Notes

- Locally, results are printed to console.
- You can wire PR comments later via GitHub API if needed.
