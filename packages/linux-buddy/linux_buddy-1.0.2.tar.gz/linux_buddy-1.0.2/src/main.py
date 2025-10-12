import sys
import os
import math
from src.data.lessons import LESSONS, LINUX_COMMANDS
from src.ui.menu import show_menu, PAGE_SIZE
from src.core.terminal import open_lesson_in_new_terminal


def main_menu():
    # use LINUX_COMMANDS list as table source (command, description)
    commands = LINUX_COMMANDS.copy()
    page = 0
    keys_flat = [c for c, _ in commands]

    while True:
        show_menu(commands, page)
        choice = input("\nSelect: ").strip().lower()
        if choice == "q":
            print("bye.")
            break
        if choice == "n":
            page += 1
            max_pages = math.ceil(len(commands) / PAGE_SIZE)
            if page >= max_pages:
                page = max_pages - 1
            continue
        if choice == "p":
            page = max(0, page - 1)
            continue
        if not choice:
            continue
        if not choice.isdigit():
            input("invalid input. press Enter to continue...")
            continue
        idx = int(choice) - 1
        if idx < 0 or idx >= len(commands):
            input("selection out of range. press Enter...")
            continue

        cmd, desc = commands[idx]
        # try find a detailed LESSON by command name (exact match). fallback to minimal lesson.
        lesson = None
        # some keys in LESSONS might be "ls" or "ncat/nc" etc. try exact match first, then try without slash
        if cmd in LESSONS:
            lesson = LESSONS[cmd]
        else:
            alt = cmd.split("/")[0]
            if alt in LESSONS:
                lesson = LESSONS[alt]

        if not lesson:
            lesson = {
                "brief": desc,
                "usage": cmd,
                "options": {},
                "ethical": "No special notes.",
                "practice": "Try running the command in the lab directory above.",
                "setup": [],
                "lab_dir": os.path.abspath(f"./labs/{cmd.replace('/', '_')}")
            }

        print(f"\nLaunching lesson for: {cmd}\n")
        open_lesson_in_new_terminal(cmd, lesson)
        input(f"\nReturned from lesson '{cmd}'. Press Enter to continue...")


def main():
    """Entry point for the linux-buddy command."""
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nexiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
