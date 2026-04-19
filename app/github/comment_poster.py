# from github import Github
# from dotenv import load_dotenv
# import os

# load_dotenv()

# def post_review(
#     repo_name: str,
#     pr_number: int,
#     head_sha: str,
#     comments: list
# ):
#     g = Github(os.getenv("GITHUB_TOKEN"))
#     repo = g.get_repo(repo_name)
#     pr = repo.get_pull(pr_number)
#     commit = repo.get_commit(head_sha)

#     if not comments:
#         print("[POSTER] No valid comments to post")
#         return

#     print(f"[POSTER] PR head SHA : {pr.head.sha[:10]}")
#     print(f"[POSTER] Commit SHA  : {head_sha[:10]}")
#     print(f"[POSTER] Comments to post:")
#     for c in comments:
#         print(f"  path={c['path']} position={c['position']} body={c['body'][:40]}")

#     pr.create_review(
#         commit=commit,
#         body="Automated review by PR Bot",
#         event="COMMENT",
#         comments=comments
#     )

#     print(f"[POSTER] Done ✅")

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def post_review(
    repo_name: str,
    pr_number: int,
    head_sha: str,
    comments: list
):
    if not comments:
        print("[POSTER] No valid comments to post")
        return

    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/reviews"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }

    # Try posting all comments together first
    payload = {
        "commit_id": head_sha,
        "body": "Automated review by PR Bot",
        "event": "COMMENT",
        "comments": comments
    }

    print(f"[POSTER] Posting to: {url}")
    print(f"[POSTER] commit_id : {head_sha[:10]}")
    print(f"[POSTER] Comments  : {len(comments)}")

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"[POSTER] ✅ All {len(comments)} comments posted successfully")
        return

    print(f"[POSTER] Batch failed {response.status_code}: {response.text[:200]}")
    print(f"[POSTER] Trying one comment at a time...")

    posted = 0
    for c in comments:
        single_payload = {
            "commit_id": head_sha,
            "body": "Automated review by PR Bot",
            "event": "COMMENT",
            "comments": [c]
        }

        print(f"  Trying: path={c['path']} position={c['position']}")
        r = requests.post(url, headers=headers, json=single_payload)

        if r.status_code == 200:
            print(f"  ✅ Posted position {c['position']}")
            posted += 1
        else:
            print(f"  ❌ Failed position {c['position']}: {r.status_code} {r.text[:150]}")

    print(f"[POSTER] Posted {posted}/{len(comments)} comments")