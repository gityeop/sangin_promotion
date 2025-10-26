from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class SessionTokenData(BaseModel):
    user_id: int
    role: str
    exp: Optional[int]
