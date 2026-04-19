from app.github.client import get_pr_files
from dotenv import load_dotenv
load_dotenv()

files = get_pr_files("harshini957/pr_bot_test", 1)

if not files:
    print("No files found — check your repo name and PR number")

for f in files:
    print(f"File    : {f['filename']}")
    print(f"Status  : {f['status']}")
    print(f"Changes : {f['changes']} lines")
    print(f"Patch preview:")
    print(f['patch'][:400] if f['patch'] else "  (no patch — binary or empty file)")
    print("---")