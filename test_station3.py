# test_station3.py
from app.review.file_filter import should_review
from app.github.diff_parser import parse_diff

print("=" * 50)
print("TESTING FILE FILTER")
print("=" * 50)

# Should be reviewed
should_review("calculator.py", 12)
should_review("app/main.py", 45)
should_review("utils/helpers.ts", 20)

# Should be skipped
should_review("logo.png", 1)
should_review("package-lock.json", 200)
should_review("requirements.txt", 5)   # .txt not in reviewable list
should_review("huge_file.py", 600)     # too many lines

print()
print("=" * 50)
print("TESTING DIFF PARSER")
print("=" * 50)

# This is the exact patch from your calculator.py PR
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

line_map = parse_diff(patch, "calculator.py")

print(f"\nLine map for calculator.py:")
for abs_line, diff_pos in line_map.items():
    print(f"  file line {abs_line}  →  diff position {diff_pos}")

print(f"\nTotal reviewable lines: {len(line_map)}")
print("\nVerification:")
print(f"  Line 7 (subtract def) in diff? : {7 in line_map}")
print(f"  Line 8 (return a-b) in diff?   : {8 in line_map}")
print(f"  Line 4 (divide def) in diff?   : {4 in line_map}  ← should be False, unchanged line")