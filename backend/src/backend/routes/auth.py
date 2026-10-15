from fastapi import APIRouter, Depends

from ..db.pool import get_db_conn
from ..schemas.auth import RefreshRequest, Token, User, UserAuth
from ..services import auth
from ..api.middlewares import get_curr_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(user: UserAuth, conn=Depends(get_db_conn)):
    return await auth.register(user, conn)


@router.post("/login", response_model=Token)
async def login(user: UserAuth, conn=Depends(get_db_conn)):
    return await auth.login(user, conn)


@router.post("/refresh", response_model=Token)
async def refresh(body: RefreshRequest, conn=Depends(get_db_conn)):
    return await auth.refresh(body.refresh_token, conn)


@router.post("/logout", status_code=204)
async def logout(body: RefreshRequest, conn=Depends(get_db_conn)):
    await auth.logout(body.refresh_token, conn)


@router.get("/me", response_model=User)
async def me(current_user: User = Depends(get_curr_user)):
    return current_user
