"""Unit tests for password hashing and JWT helpers (no DB required)."""

import jwt
import pytest

from app.core.security import (
    Role,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("s3cret-pass")
    assert hashed != "s3cret-pass"
    assert verify_password("s3cret-pass", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_carries_claims_and_type() -> None:
    token = create_access_token("user-1", {"role": Role.OWNER.value})
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == "user-1"
    assert payload["role"] == "owner"
    assert payload["type"] == "access"


def test_refresh_token_type_mismatch_rejected() -> None:
    token = create_refresh_token("user-1")
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(token, expected_type="access")
