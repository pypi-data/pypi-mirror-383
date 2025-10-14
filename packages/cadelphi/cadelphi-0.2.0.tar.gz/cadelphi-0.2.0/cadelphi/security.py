from __future__ import annotations

import secrets
from typing import MutableMapping

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(password, hashed)
    except ValueError:
        return False


def ensure_csrf_token(session: MutableMapping[str, object]) -> str:
    token = session.get("csrf_token")
    if not token or not isinstance(token, str):
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validate_csrf_token(session: MutableMapping[str, object], provided: str | None) -> bool:
    stored = session.get("csrf_token")
    if not stored or not isinstance(stored, str) or not provided:
        return False
    return secrets.compare_digest(stored, provided)
