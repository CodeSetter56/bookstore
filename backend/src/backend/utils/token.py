from datetime import datetime, timedelta, timezone
import hashlib
import jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = {**data, "exp": datetime.now(timezone.utc) + expires_delta}
    return jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.hash_algo,
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    return _create_token(
        data,
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    return _create_token(
        data,
        expires_delta or timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.hash_algo],
    )


def hash_token(token: str) -> str:
    """SHA-256 hash a raw token for safe DB storage."""
    return hashlib.sha256(token.encode()).hexdigest()

