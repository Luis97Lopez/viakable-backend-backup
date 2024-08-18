from pydantic import BaseModel, ConfigDict
from .user import UserCreate


class FirstUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activationToken: int
    userData: UserCreate
