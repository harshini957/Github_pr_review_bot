# test_station4.py
import asyncio
from app.langchain_engine.chains import run_review_chain
from dotenv import load_dotenv
load_dotenv()

# Exact patch from your calculator.py PR
patch = """@@ -4,6 +4,11 @@ def add(a, b):
 def divide(a, b):
     return a / b
 
+def subtract(a,b):
+    return a-b
+def multiply(a,b):
+    return a*b
+
 def get_user(user_id):
     data = fetch_from_db(user_id)
     return data['name']"""

async def main():
    print("Sending patch to LangChain...")
    print("=" * 50)

    result = await run_review_chain("calculator.py", patch)

    print(f"Summary: {result.summary}")
    print(f"Total comments: {len(result.comments)}")
    print()

    for i, comment in enumerate(result.comments, 1):
        print(f"Comment {i}:")
        print(f"  Line     : {comment.line}")
        print(f"  Severity : {comment.severity}")
        print(f"  Comment  : {comment.comment}")
        print()

    # Now verify each line exists in our line map
    print("=" * 50)
    print("LINE MAP VALIDATION")
    print("=" * 50)

    from app.github.diff_parser import parse_diff
    line_map = parse_diff(patch, "calculator.py")
    print(f"Valid diff lines: {list(line_map.keys())}")
    print()

    for comment in result.comments:
        diff_pos = line_map.get(comment.line)
        if diff_pos:
            print(f"  ✅ Line {comment.line} → diff position {diff_pos} — will post comment")
        else:
            print(f"  ❌ Line {comment.line} → NOT in diff — will discard")

asyncio.run(main())