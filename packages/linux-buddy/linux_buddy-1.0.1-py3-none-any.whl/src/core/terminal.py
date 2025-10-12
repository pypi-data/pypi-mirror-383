import os
import shutil
import subprocess
from src.core.lab_manager import setup_lab_environment
from src.ui.formatting import format_lesson



def open_lesson_in_new_terminal(name, lesson):
    lab_dir = lesson.get("lab_dir", os.path.abspath(f"./labs/{name}"))
    setup_lab_environment(lab_dir, lesson.get("setup", []))
    desc = format_lesson(name, lesson)
    title = f"{name} lesson"

    # prepare bash script to show the lesson and drop to an interactive shell in lab_dir
    safe_desc = desc.replace("'", "'\"'\"'")  # naive single-quote escape for bash printf
    bash_cmd = f"clear; printf '\\n\\033[1m{name} Command Lesson\\033[0m\\n\\n'; printf '{safe_desc}\\n\\n'; printf 'Lab Directory: {lab_dir}\\n\\n'; cd '{lab_dir}' || true; exec bash"

    # try to open a new tab with gnome-terminal, otherwise fallback to same terminal interactive bash
    if shutil.which("gnome-terminal"):
        try:
            subprocess.run([
                "gnome-terminal",
                "--tab",
                "--title", title,
                "--",
                "bash",
                "-c",
                bash_cmd
            ])
            return
        except Exception:
            pass

    # fallback: open interactive bash in same terminal (this will block until user types exit)
    try:
        subprocess.run(["bash", "-i", "-c", bash_cmd])
    except Exception:
        # last resort: just print the lesson and return
        print("\n" + desc + "\n")
        input("Press Enter to continue...")