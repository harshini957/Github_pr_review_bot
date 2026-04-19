from github import Github
import os
from dotenv import load_dotenv
import requests

load_dotenv()

def get_github_client():
    return Github(os.getenv("GITHUB_TOKEN"))

def get_pr_files(repo_name: str, pr_number: int):
    g = get_github_client()
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    files = []
    for f in pr.get_files():
        files.append({
            "filename": f.filename,
            "patch":    f.patch or "",
            "changes":  f.changes,
            "status":   f.status
        })
    return files

def get_pr_head_sha(repo_name: str, pr_number: int) -> str:
    g = get_github_client()
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    return pr.head.sha

def get_pr_diff_positions(repo_name: str, pr_number: int) -> dict:
    """
    Fetches the raw unified diff from GitHub and builds
    a position map per file: {filename: {absolute_line: position}}
    Position here is counted across the ENTIRE diff, not per file.
    This is what GitHub's review API actually expects.
    """
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }

    response = requests.get(url, headers=headers)
    raw_diff = response.text

    return parse_full_diff(raw_diff)


def parse_full_diff(raw_diff: str) -> dict:
    import re
    line_map = {}
    current_file = None
    diff_position = 0
    current_line = 0

    for line in raw_diff.split("\n"):

        if line.startswith("diff --git"):
            current_file = None
            current_line = 0

        elif line.startswith("+++ b/"):
            current_file = line[6:].strip()
            line_map[current_file] = {}
            diff_position = 0
            current_line = 0

        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            if match:
                current_line = int(match.group(1)) - 1
            diff_position += 1

        elif current_file is not None:

            # Skip the "no newline at end of file" marker
            if line.startswith("\\ No newline"):
                continue

            diff_position += 1

            if line.startswith("+"):
                current_line += 1
                line_map[current_file][current_line] = diff_position

            elif line.startswith("-"):
                pass

            else:
                current_line += 1

    return line_map