from pydantic import BaseModel, ConfigDict
from .user import PublicUser
from datetime import datetime


class Token(BaseModel):
    refreshToken: str
    accessToken: str
    accessExpiresAt: datetime
    refreshExpiresAt: datetime
    tokenType: str


class TokenWithUser(Token):
    model_config = ConfigDict(from_attributes=True)

    user: PublicUser


class RefreshTokenData(BaseModel):
    refresh_token: str
