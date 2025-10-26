from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings

settings = get_settings()


def create_access_token(data: Dict[str, Any], expires_minutes: int | None = None) -> tuple[str, datetime]:
    expire_delta = timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    expire = datetime.now(tz=timezone.utc) + expire_delta
    payload = {"exp": expire, **data}
    encoded_jwt = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return encoded_jwt, expire


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        decoded = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:  # pragma: no cover - runtime guard
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:  # pragma: no cover - runtime guard
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return decoded
