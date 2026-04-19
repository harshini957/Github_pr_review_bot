# test_webhook.py
import hmac
import hashlib
import json
import urllib.request
import os
from dotenv import load_dotenv

load_dotenv()

secret = os.getenv("GITHUB_WEBHOOK_SECRET")

# Payload - must be the EXACT bytes sent
payload_dict = {
    "action": "opened",
    "pull_request": {"number": 1},
    "repository": {"full_name": "testuser/testrepo"}
}

# Use separators to control exact formatting - no spaces
payload_bytes = json.dumps(payload_dict, separators=(',', ':')).encode('utf-8')

# Generate signature from those exact bytes
signature = "sha256=" + hmac.new(
    secret.encode('utf-8'),
    payload_bytes,
    hashlib.sha256
).hexdigest()

print(f"Secret used    : '{secret}'")
print(f"Payload bytes  : {payload_bytes}")
print(f"Signature      : {signature}")
print(f"Sending request...")

# Send request with those exact bytes
req = urllib.request.Request(
    "http://localhost:8000/webhook",
    data=payload_bytes,
    headers={
        "Content-Type": "application/json",
        "x-hub-signature-256": signature
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"Response: {resp.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()}")