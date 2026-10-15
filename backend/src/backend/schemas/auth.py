from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class UserAuth(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str


class User(BaseModel):
    id: UUID
    username: str
    elo_rating: int
    created_at: datetime


class RefreshRequest(BaseModel):
    refresh_token: str

