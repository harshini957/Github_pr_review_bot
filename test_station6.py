# test_station6.py
import asyncio
import time
from app.github.client import get_pr_files, get_pr_head_sha, get_pr_diff_positions
from app.review.file_filter import should_review
from app.langchain_engine.chains import run_review_chain
from app.github.comment_poster import post_review
from app.core.cache import get_cache, set_cache, is_duplicate, mark_reviewed
import hashlib
from dotenv import load_dotenv
load_dotenv()

REPO = "harshini957/pr_bot_test"
PR_NUMBER = 4

async def review_with_cache(files, full_line_map, repo_name, pr_number):
    all_comments = []

    for f in files:
        filename = f["filename"]
        if not should_review(filename, f["changes"]):
            continue

        line_map = full_line_map.get(filename, {})
        valid_lines = list(line_map.keys())
        if not valid_lines:
            continue

        content_hash = hashlib.sha256(f["patch"].encode()).hexdigest()
        cache_key = f"review:{content_hash}"

        cached = get_cache(cache_key)
        if cached is not None:
            print(f"  [CACHE] HIT for {filename} — no LLM call made ✅")
            file_comments = cached
        else:
            print(f"  [CACHE] MISS for {filename} — calling LLM...")
            result = await run_review_chain(
                filename, f["patch"], valid_lines=valid_lines
            )
            file_comments = []
            for comment in result.comments:
                diff_position = line_map.get(comment.line)
                if diff_position is None:
                    continue
                file_comments.append({
                    "path": filename,
                    "position": diff_position,
                    "body": f"**{comment.severity.capitalize()}**: {comment.comment}"
                })
            set_cache(cache_key, file_comments, ttl=86400)

        for comment in file_comments:
            dedup_key = (
                f"posted:{repo_name}:{pr_number}"
                f":{comment['path']}:{comment['position']}"
                f":{comment['body'][:40]}"
            )
            if is_duplicate(dedup_key):
                print(f"  [DEDUP] Skipping duplicate: position {comment['position']}")
                continue
            mark_reviewed(dedup_key)
            all_comments.append(comment)

    return all_comments

async def main():
    files = get_pr_files(REPO, PR_NUMBER)
    full_line_map = get_pr_diff_positions(REPO, PR_NUMBER)

    print("=" * 50)
    print("RUN 1 — First time, cache is empty")
    print("=" * 50)
    start = time.time()
    comments = await review_with_cache(files, full_line_map, REPO, PR_NUMBER)
    print(f"Time: {time.time() - start:.1f}s | Comments: {len(comments)}")

    print()
    print("=" * 50)
    print("RUN 2 — Same files, cache should hit")
    print("=" * 50)
    start = time.time()
    comments2 = await review_with_cache(files, full_line_map, REPO, PR_NUMBER)
    print(f"Time: {time.time() - start:.1f}s | Comments: {len(comments2)}")
    print("(Should be near 0s and 0 new comments — all deduplicated)")

asyncio.run(main())