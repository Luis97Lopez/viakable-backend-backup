from pydantic import BaseModel, ConfigDict
from .user import User


class Role(BaseModel):
    id: str
