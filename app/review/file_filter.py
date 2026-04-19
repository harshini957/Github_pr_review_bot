import os
import fnmatch

SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".pdf", ".zip", ".tar", ".gz",
    ".pyc", ".pyo", ".so", ".dll", ".exe",
    ".woff", ".woff2", ".ttf", ".eot"
}

SKIP_PATTERNS = [
    "*.lock", "*-lock.json", "*.min.js", "*.min.css",
    "package-lock.json", "poetry.lock", "yarn.lock",
    "migrations/*", "*.snap", "*.pb.go", "*_pb2.py"
]

REVIEWABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".go", ".java", ".rb", ".rs", ".cpp",
    ".c", ".cs", ".php", ".swift", ".kt"
}

MAX_CHANGED_LINES = 500

def should_review(filename: str, changed_lines: int) -> bool:
    ext = os.path.splitext(filename)[1].lower()

    if ext in SKIP_EXTENSIONS:
        print(f"  [FILTER] Skipping {filename} — binary/asset file")
        return False

    for pattern in SKIP_PATTERNS:
        if fnmatch.fnmatch(filename, pattern):
            print(f"  [FILTER] Skipping {filename} — matches skip pattern")
            return False

    if ext not in REVIEWABLE_EXTENSIONS:
        print(f"  [FILTER] Skipping {filename} — not a reviewable extension")
        return False

    if changed_lines > MAX_CHANGED_LINES:
        print(f"  [FILTER] Skipping {filename} — too large ({changed_lines} lines)")
        return False

    print(f"  [FILTER] Reviewing {filename} ✓")
    return True