import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_redis():
    return redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def get_cache(key: str):
    try:
        r = get_redis()
        value = r.get(key)
        if value:
            print(f"[CACHE] Hit: {key[:50]}")
            return json.loads(value)
        return None
    except Exception as e:
        print(f"[CACHE] Redis error: {e}")
        return None

def set_cache(key: str, value, ttl: int = 86400):
    try:
        r = get_redis()
        r.setex(key, ttl, json.dumps(value))
        print(f"[CACHE] Stored: {key[:50]}")
    except Exception as e:
        print(f"[CACHE] Redis error: {e}")

def is_duplicate(key: str) -> bool:
    try:
        r = get_redis()
        return r.exists(key) == 1
    except Exception as e:
        print(f"[CACHE] Redis error: {e}")
        return False

def mark_reviewed(key: str, ttl: int = 86400):
    try:
        r = get_redis()
        r.setex(key, ttl, "1")
    except Exception as e:
        print(f"[CACHE] Redis error: {e}")