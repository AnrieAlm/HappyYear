"""Two-person auth.

There is no public signup. The allowlist is a JSON object in the USERS env var,
so adding a third player is a config change, not a code change. Tokens are
signed JWTs sent as `Authorization: Bearer <token>` and kept in localStorage by
the frontend -- simplest thing that works cross-origin from GitHub Pages to
Render (cookies would need SameSite=None + Secure and get blocked by some
browsers as third-party). This is a private two-person app with no third-party
scripts; if you ever add one, move the token to an HttpOnly cookie.
"""
from __future__ import annotations

import hmac
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

ALGORITHM = "HS256"
_bearer = HTTPBearer(auto_error=False)


def verify_passcode(name: str, passcode: str) -> bool:
    expected = settings().users_map.get(name)
    if expected is None:
        # Still burn a comparison so a missing user isn't faster than a wrong one.
        hmac.compare_digest("x" * 16, "y" * 16)
        return False
    return hmac.compare_digest(expected, passcode)


def issue_token(name: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": name,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings().jwt_ttl_days)).timestamp()),
    }
    return jwt.encode(payload, settings().jwt_secret, algorithm=ALGORITHM)


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    if creds is None or not creds.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    try:
        payload = jwt.decode(creds.credentials, settings().jwt_secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid session") from None

    name = payload.get("sub")
    if name not in settings().users_map:
        # A user removed from the allowlist loses access immediately.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not on the allowlist")
    return name
