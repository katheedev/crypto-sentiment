from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config.settings import EnvSettings


settings = EnvSettings()


def create_access_token(username: str) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=120)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> str | None:
    try:
        data = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return data.get("sub")
    except JWTError:
        return None
