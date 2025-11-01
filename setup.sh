#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama not found. Install it from https://ollama.com first."
else
  ollama pull llama3.1 || true
fi
echo "Done. Run: source .venv/bin/activate && novareview --staged"
