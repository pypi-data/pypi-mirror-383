import os
import shutil
import math
from src.utils.helpers import clear, truncate_words


# --------- Menu display (4 cols x 25 rows = 100 items per page) ----------
NUM_COLS = 4
PER_COL = 25
PAGE_SIZE = NUM_COLS * PER_COL  # 100

def show_menu(commands, page_idx=0):
    clear()
    total_items = len(commands)
    total_pages = max(1, math.ceil(total_items / PAGE_SIZE))
    page_idx = max(0, min(page_idx, total_pages - 1))
    start = page_idx * PAGE_SIZE
    end = min(start + PAGE_SIZE, total_items)
    page_items = commands[start:end]

    # pad to PAGE_SIZE for column slicing
    padded = page_items + [("", "")] * (PAGE_SIZE - len(page_items))

    # split to columns: each column has PER_COL rows
    cols = []
    for c in range(NUM_COLS):
        col_slice = padded[c*PER_COL:(c+1)*PER_COL]
        cols.append(col_slice)

    term_width = shutil.get_terminal_size((140, 40)).columns
    col_width = max(20, term_width // NUM_COLS - 2)

    header = f"=== Linux Command Tutor By \033[1;38;2;57;255;20mgithub.com/jo4dan\033[0m — page {page_idx+1}/{total_pages} (showing items {start+1}-{end} of {total_items}) ==="
    print(header + "\n")
    # print rows
    for row in range(PER_COL):
        line = ""
        for col_idx in range(NUM_COLS):
            cmd, desc = cols[col_idx][row]
            if cmd:
                num = start + (col_idx * PER_COL) + row + 1
                brief = truncate_words(desc, col_width - 20)
                entry = f"{num:3}. {cmd:<15} - {brief}"
            else:
                entry = ""
            line += entry.ljust(col_width)
        print(line)
    print("\nCommands: enter number to open lesson | n: next page | p: prev page | q: quit")
