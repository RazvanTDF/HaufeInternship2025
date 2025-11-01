def build_prompt(guidelines, file_path, lang, code):
    guide = "\n".join(f"- {g}" for g in guidelines)
    return (
        "You are a senior code reviewer. Review ONLY the provided diff chunk.\n"
        "Focus order: (1) correctness/bugs (2) security (3) reliability (4) maintainability.\n"
        "Avoid vague style nits. Prefer precise, minimal, actionable comments.\n"
        "If you are not certain, say so.\n\n"
        "Output STRICT JSON with fields:\n"
        "{summary:str, comments:[{lineOffset:int, message:str, suggestion?:str}]}\n"
        f"Project guidelines:\n{guide}\n"
        f"File: {file_path} ({lang})\n"
        f"Changed code:\n```{lang}\n{code}\n```"
    )
