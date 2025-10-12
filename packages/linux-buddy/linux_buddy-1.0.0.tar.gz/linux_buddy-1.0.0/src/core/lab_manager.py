import os
import shutil

def setup_lab_environment(lab_dir, setup_items):
    # create a lab dir and dummy files/dirs from setup list
    if os.path.exists(lab_dir):
        try:
            shutil.rmtree(lab_dir)
        except Exception:
            pass
    os.makedirs(lab_dir, exist_ok=True)
    for item in (setup_items or []):
        path = os.path.join(lab_dir, item)
        if item.endswith("/"):
            os.makedirs(path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
            with open(path, "w") as f:
                f.write(f"Dummy content for {item}\n")