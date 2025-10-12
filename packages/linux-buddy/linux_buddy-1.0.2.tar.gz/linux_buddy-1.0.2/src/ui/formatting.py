import textwrap

def format_options(opts):
    if not opts:
        return "  (no options provided)"
    lines = []
    for k, v in opts.items():
        lines.append(f"  {k : <8} : {v}")
    return "\n".join(lines)

def format_lesson(name, lesson):
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    text = []
    text.append(f"{YELLOW}{name}{RESET}")
    brief = lesson.get("brief", "")
    text.append(f"{YELLOW}{brief}{RESET}\n")

    usage = lesson.get("usage", name)
    text.append(f"Usage: {usage}\n")
    text.append("Options:\n" + format_options(lesson.get("options", {})) + "\n")

    text.append(f"{YELLOW}ETHICAL HACKER SIGNIFICANCE:{RESET}")
    wrapped_ethical = textwrap.fill(lesson.get("ethical", "No ethical notes."), width=70, initial_indent='  ', subsequent_indent='  ')
    text.append(wrapped_ethical + "\n")

    if "practice" in lesson and lesson["practice"]:
        practice_wrapped = textwrap.fill(lesson["practice"], width=70, initial_indent='  ', subsequent_indent='  ')
        text.append(f"{YELLOW}What you should do:{RESET}")
        text.append(practice_wrapped + "\n")

    text.append("Type 'exit' to close this tab and return to the menu.")
    return "\n".join(text)