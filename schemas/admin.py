from pydantic import BaseModel, ConfigDict, model_validator
from fastapi_filter.contrib.sqlalchemy import Filter
from db import models as db_models
from . import user


class AdminBase(user.UserBase):
    firstName: str
    lastName: str


class AdminCreate(user.UserCreate, AdminBase):
    pass


class AdminPartialIn(user.UserPartialIn):
    firstName: str | None = None
    lastName: str | None = None


class PublicAdmin(user.PublicUser, AdminBase):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def unpack_user(self):
        for field in user.PublicUser.model_fields:
            self[field] = getattr(self.get('role_user').user, field)
        return self


class Admin(user.User, PublicAdmin):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def unpack_user(self):
        for field in user.User.model_fields:
            self[field] = getattr(self.get('role_user').user, field)
        return self


# -----------------
# FILTER
# -----------------
class AdminFilter(user.UserFilter):
    # firstName
    firstName: str | None = None
    firstName__like: str | None = None

    # lastName
    lastName: str | None = None
    lastName__like: str | None = None

    order_by: list[str] = ['firstName', 'lastName']
    search: str | None = None

    class Constants(Filter.Constants):
        model = db_models.Admin
        search_model_fields = ['firstName', 'lastName']
