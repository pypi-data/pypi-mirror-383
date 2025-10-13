"""Authentication helpers for CRL API."""

import hashlib
import hmac
import base64
import time


def create_signature(method: str, path: str, timestamp: int, body: str, secret: str) -> str:
    """
    Create HMAC-SHA256 signature for request.
    
    Signature string format:
    METHOD\nPATH\nTIMESTAMP\nSHA256(BODY)
    """
    # Hash body
    body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
    
    # Create signature string
    sig_string = f"{method}\n{path}\n{timestamp}\n{body_hash}"
    
    # HMAC-SHA256
    signature = hmac.new(
        secret.encode('utf-8'),
        sig_string.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Base64 encode
    return base64.b64encode(signature).decode('utf-8')
