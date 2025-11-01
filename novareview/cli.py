# CLI entrypoint. No diacritics in comments.
import sys
from .reviewer import run_review

def main():
    staged = "--staged" in sys.argv
    run_review(staged=staged)
