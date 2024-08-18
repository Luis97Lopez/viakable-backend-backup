from pydantic import BaseModel, ConfigDict
from fastapi_filter.contrib.sqlalchemy import Filter
from db import models as db_models


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserPartialIn(BaseModel):
    username: str | None = None


class ModifyUserByAdmin(BaseModel):
    username: str | None = None


class CreateUserByAdmin(UserCreate):
    isActive: bool = True


class FirstSuperUserCreate(UserCreate):
    isSuperUser: bool = True
    isActive: bool = True


class PublicUser(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    isSuperUser: bool
    isActive: bool


class User(PublicUser):
    password: str


# -----------------
# FILTER
# -----------------
class UserFilter(Filter):
    # username
    username: str | None = None
    username__like: str | None = None

    order_by: list[str] = ['username']
    search: str | None = None

    class Constants(Filter.Constants):
        model = db_models.User
        search_model_fields = ['username']

# -----------------
# CHANGE PASSWORDS
# -----------------


class ChangePasswordUser(BaseModel):
    oldPassword: str
    password: str


class UpdatePassword(BaseModel):
    password: str
