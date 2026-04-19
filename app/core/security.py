import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)