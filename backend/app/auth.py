"""Lightweight JWT auth layer."""
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Callable

import jwt
from flask import request, abort
from loguru import logger

JWT_SECRET = os.getenv("JWT_SECRET", "change‑me‑in‑prod")
JWT_ALGORITHM = "HS256"
JWT_TTL_MIN = int(os.getenv("JWT_TTL_MIN", "60"))

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")


def _generate_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=JWT_TTL_MIN),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def login_handler() -> dict:
    data = request.get_json(silent=True) or {}
    if data.get("username") == ADMIN_USER and data.get("password") == ADMIN_PASSWORD:
        token = _generate_token(ADMIN_USER)
        logger.success("Admin logged in, token issued")
        return {"access_token": token}
    logger.error("Invalid credentials")
    abort(401, description="Invalid credentials")


def require_auth(fn: Callable):
    @wraps(fn)
    def _wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, description="Missing Bearer token")
        token = auth_header.removeprefix("Bearer ")
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.PyJWTError as exc:
            abort(401, description=f"Token error: {exc}")
        return fn(*args, **kwargs)

    return _wrapper