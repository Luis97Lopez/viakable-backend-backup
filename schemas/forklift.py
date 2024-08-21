from pydantic import ConfigDict, model_validator
from fastapi_filter.contrib.sqlalchemy import Filter
from db import models as db_models
from . import user


class ForkliftBase(user.UserBase):
    name: str


class ForkliftCreate(user.UserCreate, ForkliftBase):
    pass


class ForkliftPartialIn(user.ModifyUserByAdmin):
    name: str | None = None


class PublicForklift(user.PublicUser, ForkliftBase):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def unpack_user(self):
        for field in user.PublicUser.model_fields:
            self[field] = getattr(self.get('role_user').user, field)
        return self


class Forklift(user.User, PublicForklift):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def unpack_user(self):
        for field in user.User.model_fields:
            self[field] = getattr(self.get('role_user').user, field)
        return self


# -----------------
# FILTER
# -----------------
class ForkliftFilter(user.UserFilter):
    # name
    name: str | None = None
    name__like: str | None = None

    order_by: list[str] = ['name']
    search: str | None = None

    class Constants(Filter.Constants):
        model = db_models.Forklift
        search_model_fields = ['name']
