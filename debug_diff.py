# debug_diff.py
from app.github.client import get_pr_files, get_pr_diff_positions, get_pr_head_sha
from dotenv import load_dotenv
load_dotenv()

REPO = "harshini957/pr_bot_test"
PR_NUMBER = 4

files = get_pr_files(REPO, PR_NUMBER)
full_line_map = get_pr_diff_positions(REPO, PR_NUMBER)
head_sha = get_pr_head_sha(REPO, PR_NUMBER)

print(f"Head SHA: {head_sha[:10]}")
print()

for f in files:
    filename = f["filename"]
    print(f"FILE: {filename}")
    print(f"Raw patch:")
    print(f["patch"])
    print()
    print(f"Line map for this file:")
    line_map = full_line_map.get(filename, {})
    for line, pos in line_map.items():
        print(f"  file line {line} → diff position {pos}")
    print("---")