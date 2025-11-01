def build_prompt(guidelines, file_path, lang, code):
    guide = "\n".join(f"- {g}" for g in guidelines)
    return (
        "You are a senior code reviewer. Review ONLY the provided diff chunk.\n"
        "Goals:\n"
        "- Find bugs, security issues, undefined behavior, race conditions.\n"
        "- Flag style only if it reduces readability or maintainability.\n"
        "- Suggest minimal, concrete improvements with inline examples.\n"
        "- If change alters behavior, propose tests.\n"
        "- If docs/comments need updates, point them out.\n\n"
        "Output JSON with fields:\n"
        "{severity:'info'|'warn'|'error', summary:str, "
        "comments:[{lineOffset:int, message:str, suggestion?:str}]}\n\n"
        f"Project guidelines:\n{guide}\n"
        f"File: {file_path} ({lang})\n"
        f"Changed code:\n```{lang}\n{code}\n```"
    )
