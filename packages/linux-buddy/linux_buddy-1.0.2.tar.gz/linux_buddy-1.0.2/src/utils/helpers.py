import os
import shutil

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def truncate_words(text, limit):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "…"

