import os
import hashlib
import secrets
from typing import Tuple

# PBKDF2-HMAC-SHA256 parameters
ITERATIONS = 200_000
SALT_BYTES = 16
KEY_LEN = 32


def hash_password(password: str) -> Tuple[bytes, bytes]:
    """Return (hash, salt) for storage."""
    salt = secrets.token_bytes(SALT_BYTES)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, ITERATIONS, dklen=KEY_LEN
    )
    return pwd_hash, salt


def verify_password(password: str, stored_hash: bytes, salt: bytes) -> bool:
    calc = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, ITERATIONS, dklen=KEY_LEN
    )
    return secrets.compare_digest(calc, stored_hash)