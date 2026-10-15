import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..db.pool import get_db_conn
from ..schemas.auth import User
from ..utils.token import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login") 


async def get_curr_user(
    token: str = Depends(oauth2_scheme),
    conn=Depends(get_db_conn),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        username = decode_token(token).get("sub")
    except jwt.PyJWTError:
        raise credentials_exception
    if username is None:
        raise credentials_exception

    cur = await conn.execute(
        """
        SELECT id, username, elo_rating, created_at
        FROM users
        WHERE username = %s
        """,
        (username,),
    )

    db_user = await cur.fetchone()
    if db_user is None:
        raise credentials_exception

    return User(**db_user)