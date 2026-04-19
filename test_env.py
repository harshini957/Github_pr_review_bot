# test_env.py
from dotenv import load_dotenv
import os
load_dotenv()

print("GITHUB_TOKEN:", os.getenv("GITHUB_TOKEN", "NOT FOUND")[:10] + "...")
print("GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY", "NOT FOUND")[:10] + "...")
print("GITHUB_WEBHOOK_SECRET:", os.getenv("GITHUB_WEBHOOK_SECRET", "NOT FOUND"))
print("REDIS_URL:", os.getenv("REDIS_URL", "NOT FOUND"))