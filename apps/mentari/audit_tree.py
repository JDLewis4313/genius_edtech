# audit_tree.py
import os

EXCLUDE = {"__pycache__", "migrations", "static", "media", ".git", ".venv", "genius_env", "node_modules"}
MAX_DEPTH = 4

def print_tree(base_path, prefix="", depth=0):
    if depth > MAX_DEPTH:
        return
    try:
        entries = sorted([e for e in os.listdir(base_path) if e not in EXCLUDE])
    except PermissionError:
        return
    for i, entry in enumerate(entries):
        path = os.path.join(base_path, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(prefix + connector + entry)
        if os.path.isdir(path):
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(path, prefix + extension, depth + 1)

if __name__ == "__main__":
    print("📁 Project Structure (Level 4):\n")
    print_tree(".", depth=0)
