"""Authentication helpers: password hashing and JWT tokens."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time

import jwt


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256 (stdlib, no external deps)."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"pbkdf2_sha256$200000${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    """Return True if ``password`` matches the encoded hash."""
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_token(secret: str, username: str, role: str, expires_minutes: int) -> str:
    """Create a signed JWT for the given user."""
    now = int(time.time())
    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + expires_minutes * 60,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(secret: str, token: str) -> dict | None:
    """Decode and validate a JWT, returning its payload or None."""
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
