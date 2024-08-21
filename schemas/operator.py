from pydantic import ConfigDict, model_validator
from fastapi_filter.contrib.sqlalchemy import Filter
from db import models as db_models
from . import user


class OperatorBase(user.UserBase):
    machine: str
    area: str


class OperatorCreate(user.UserCreate, OperatorBase):
    pass


class OperatorPartialIn(user.ModifyUserByAdmin):
    machine: str | None = None
    area: str | None = None


class PublicOperator(user.PublicUser, OperatorBase):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def unpack_user(self):
        for field in user.PublicUser.model_fields:
            self[field] = getattr(self.get('role_user').user, field)
        return self


class Operator(user.User, PublicOperator):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def unpack_user(self):
        for field in user.User.model_fields:
            self[field] = getattr(self.get('role_user').user, field)
        return self


# -----------------
# FILTER
# -----------------
class OperatorFilter(user.UserFilter):
    # machine
    machine: str | None = None
    machine__like: str | None = None

    # area
    area: str | None = None
    area__like: str | None = None

    order_by: list[str] = ['machine', 'area']
    search: str | None = None

    class Constants(Filter.Constants):
        model = db_models.Operator
        search_model_fields = ['machine', 'area']
