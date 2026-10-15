from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
import jwt

from ..schemas.auth import Token, UserAuth
from ..utils.config import settings
from ..utils.token import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)


async def _issue_tokens(username: str, conn) -> Token:
    """Create an access + refresh token pair, store the refresh token in the DB."""
    access_token = create_access_token({"sub": username})
    refresh_token = create_refresh_token({"sub": username})

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days,
    )
    await conn.execute(
        """
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
        SELECT id, %s, %s
        FROM users
        WHERE username = %s
        """,
        (hash_token(refresh_token), expires_at, username),
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


async def register(data: UserAuth, conn) -> Token:
    cur = await conn.execute(
        """
        SELECT 1
        FROM users
        WHERE username = %s
        """,
        (data.username,)
    )
    if await cur.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    cur = await conn.execute(
        """
        INSERT INTO users (username, password_hash)
        VALUES (%s, %s)
        RETURNING id, username, elo_rating, created_at
        """,
        (data.username, hash_password(data.password)),
    )
    new_user = await cur.fetchone()
    if new_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )

    token = await _issue_tokens(new_user["username"], conn)
    await conn.commit()
    return token


async def login(data: UserAuth, conn) -> Token:
    cur = await conn.execute(
        """
        SELECT username, password_hash
        FROM users
        WHERE username = %s
        """,
        (data.username,),
    )
    db_user = await cur.fetchone()

    if db_user is None or not verify_password(data.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = await _issue_tokens(db_user["username"], conn)
    await conn.commit()
    return token


async def refresh(refresh_token: str, conn) -> Token:
    """Validate a refresh token, rotate it, and return a new token pair."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Decode the JWT to check signature + expiry
    try:
        payload = decode_token(refresh_token)
        username = payload.get("sub")
    except jwt.PyJWTError:
        raise credentials_exception
    if username is None:
        raise credentials_exception

    # 2. Check the hashed token exists in the DB (not revoked)
    token_hash = hash_token(refresh_token)
    cur = await conn.execute(
        """
        DELETE FROM refresh_tokens
        WHERE token_hash = %s
        RETURNING user_id
        """,
        (token_hash,),
    )
    deleted = await cur.fetchone()
    if deleted is None:
        raise credentials_exception

    # 3. Issue a brand new pair (rotation)
    token = await _issue_tokens(username, conn)
    await conn.commit()
    return token


async def logout(refresh_token: str, conn) -> None:
    """Revoke a refresh token so it can't be used again."""
    token_hash = hash_token(refresh_token)
    await conn.execute(
        "DELETE FROM refresh_tokens WHERE token_hash = %s",
        (token_hash,),
    )
    await conn.commit()



