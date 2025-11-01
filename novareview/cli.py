# CLI entrypoint. No diacritics in comments.
import sys
from .reviewer import run_review

def main():
    staged = "--staged" in sys.argv
    apply = "--apply" in sys.argv  # optional autofix
    run_review(staged=staged, apply=apply)

if __name__ == "__main__":
    main()
