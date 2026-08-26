"""Tests for password hashing and JWT helpers."""

from __future__ import annotations

from ragkb.auth import create_token, decode_token, hash_password, verify_password

SECRET = "test-secret-key-for-ragkb-0123456789"
WRONG_SECRET = "wrong-secret-key-for-ragkb-0123456789"


def test_password_hash_and_verify() -> None:
    encoded = hash_password("secret")
    assert encoded != "secret"
    assert verify_password("secret", encoded)
    assert not verify_password("wrong", encoded)


def test_token_roundtrip() -> None:
    token = create_token(SECRET, "alice", "admin", 60)
    payload = decode_token(SECRET, token)
    assert payload is not None
    assert payload["sub"] == "alice"
    assert payload["role"] == "admin"


def test_token_invalid() -> None:
    assert decode_token(SECRET, "not-a-token") is None


def test_token_wrong_secret() -> None:
    token = create_token(SECRET, "alice", "admin", 60)
    assert decode_token(WRONG_SECRET, token) is None
