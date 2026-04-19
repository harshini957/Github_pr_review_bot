import asyncio
from app.github.client import get_pr_files, get_pr_head_sha, get_pr_diff_positions
from app.review.file_filter import should_review
from app.langchain_engine.chains import run_review_chain
from app.github.comment_poster import post_review
from dotenv import load_dotenv
load_dotenv()

REPO = "harshini957/pr_bot_test"
PR_NUMBER = 4

async def main():
    print(f"Fetching files for PR #{PR_NUMBER}...")
    files = get_pr_files(REPO, PR_NUMBER)
    head_sha = get_pr_head_sha(REPO, PR_NUMBER)
    full_line_map = get_pr_diff_positions(REPO, PR_NUMBER)

    print(f"Head SHA: {head_sha[:10]}...")
    print(f"Files in diff: {[f['filename'] for f in files]}")

    all_comments = []

    for f in files:
        filename = f["filename"]
        print(f"\nProcessing: {filename}")

        if not should_review(filename, f["changes"]):
            continue

        line_map = full_line_map.get(filename, {})
        valid_lines = list(line_map.keys())
        print(f"  Valid lines: {valid_lines}")

        if not valid_lines:
            print(f"  No reviewable lines — skipping")
            continue

        result = await run_review_chain(
            filename,
            f["patch"],
            valid_lines=valid_lines
        )

        print(f"  Summary: {result.summary}")
        print(f"  Comments: {len(result.comments)}")

        for comment in result.comments:
            diff_position = line_map.get(comment.line)
            if diff_position is None:
                print(f"  ❌ Line {comment.line} — discarded")
                continue
            print(f"  ✅ Line {comment.line} → position {diff_position}")
            all_comments.append({
                "path": filename,
                "position": diff_position,
                "body": f"**{comment.severity.capitalize()}**: {comment.comment}"
            })

    print(f"\nTotal valid comments: {len(all_comments)}")
    if all_comments:
        post_review(REPO, PR_NUMBER, head_sha, all_comments)
        print("Check PR #4 on GitHub — comments should appear!")
    else:
        print("No valid comments — push a commit with obvious issues")

asyncio.run(main())