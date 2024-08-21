from pydantic import BaseModel, ConfigDict
from fastapi_filter.contrib.sqlalchemy import Filter
from db import models as db_models


class MaterialBase(BaseModel):
    name: str
    unit: str
    image: str | None = None
    color: str | None = None


class MaterialPartialIn(BaseModel):
    name: str | None = None
    unit: str | None = None
    image: str | None = None
    color: str | None = None


class MaterialCreate(MaterialBase):
    pass


class PublicMaterial(MaterialBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class Material(PublicMaterial):
    pass


# -----------------
# FILTER
# -----------------
class MaterialFilter(Filter):
    # name
    name: str | None = None
    name__like: str | None = None

    order_by: list[str] = ['name']

    class Constants(Filter.Constants):
        model = db_models.Material
