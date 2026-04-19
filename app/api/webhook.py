from fastapi import APIRouter, Request, Header, HTTPException
from app.core.security import verify_signature
from app.github.client import get_pr_files, get_pr_head_sha, get_pr_diff_positions
from app.review.file_filter import should_review
from app.langchain_engine.chains import run_review_chain
from app.github.comment_poster import post_review
from app.core.cache import get_cache, set_cache, is_duplicate, mark_reviewed
from dotenv import load_dotenv
import os
import asyncio
import hashlib

load_dotenv()
router = APIRouter()

@router.post("/webhook")
async def handle_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None)
):
    payload = await request.body()

    if not verify_signature(
        payload,
        x_hub_signature_256,
        os.getenv("GITHUB_WEBHOOK_SECRET")
    ):
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()
    action = data.get("action")

    if action not in ("opened", "synchronize"):
        return {"status": "ignored"}

    pr_number = data["pull_request"]["number"]
    repo_name = data["repository"]["full_name"]
    head_sha  = data["pull_request"]["head"]["sha"]

    print(f"[WEBHOOK] PR #{pr_number} {action} — queuing review")
    asyncio.create_task(process_pr(repo_name, pr_number, head_sha))
    return {"status": "queued"}


async def process_pr(repo_name: str, pr_number: int, head_sha: str):
    try:
        files = get_pr_files(repo_name, pr_number)
        full_line_map = get_pr_diff_positions(repo_name, pr_number)
        all_comments = []

        for f in files:
            filename = f["filename"]

            if not should_review(filename, f["changes"]):
                continue

            line_map = full_line_map.get(filename, {})
            valid_lines = list(line_map.keys())

            if not valid_lines:
                continue

            # Cache check — skip LLM if this exact file content was reviewed before
            content_hash = hashlib.sha256(
                f["patch"].encode()
            ).hexdigest()
            cache_key = f"review:{content_hash}"

            cached = get_cache(cache_key)
            if cached is not None:
                print(f"[CACHE] Using cached review for {filename}")
                file_comments = cached
            else:
                result = await run_review_chain(
                    filename,
                    f["patch"],
                    valid_lines=valid_lines
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

                # Store result in cache for 24 hours
                set_cache(cache_key, file_comments, ttl=86400)

            # Deduplication — skip comments already posted on this PR
            for comment in file_comments:
                dedup_key = (
                    f"posted:{repo_name}:{pr_number}"
                    f":{comment['path']}:{comment['position']}"
                    f":{comment['body'][:40]}"
                )

                if is_duplicate(dedup_key):
                    print(f"[DEDUP] Skipping duplicate: position {comment['position']}")
                    continue

                mark_reviewed(dedup_key, ttl=86400)
                all_comments.append(comment)

        if all_comments:
            post_review(repo_name, pr_number, head_sha, all_comments)
            print(f"[WEBHOOK] ✅ Posted {len(all_comments)} comment(s) on PR #{pr_number}")
        else:
            print(f"[WEBHOOK] No new comments for PR #{pr_number}")

    except Exception as e:
        import traceback
        print(f"[WEBHOOK] Error on PR #{pr_number}: {e}")
        traceback.print_exc()