from pydantic import BaseModel, ConfigDict, Field, AwareDatetime
from datetime import datetime, timezone
from fastapi_filter.contrib.sqlalchemy import Filter
from db import models as db_models
from utils.enums import OrderStates

# TODO:
from .forklift import PublicForklift
from .operator import PublicOperator
from .user import PublicUser
from .material import PublicMaterial


class OrderBase(BaseModel):
    id_forklift: int
    estimate_datetime: AwareDatetime
    id_operator: int | None = None
    creation_datetime: AwareDatetime = Field(default=datetime.now(tz=timezone.utc))
    order_datetime: datetime | None = None
    state: OrderStates = OrderStates.PENDING


class OrderByMaterial(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_material: int
    quantity: int
    material: PublicMaterial | None = None


class OrderCreate(OrderBase):
    materials_order: list[OrderByMaterial]


class PublicOrder(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    canceled: bool = False
    operator: PublicUser | None = None
    forklift: PublicUser | None = None
    materials_order: list[OrderByMaterial] | None = None


class Order(PublicOrder):
    pass


# -----------------
# FILTER
# -----------------
class OrderFilter(Filter):
    # canceled
    canceled: bool | None = None

    # creation_datetime
    creation_datetime: datetime | None = None
    creation_datetime__gt: datetime | None = None
    creation_datetime__gte: datetime | None = None
    creation_datetime__lte: datetime | None = None
    creation_datetime__lt: datetime | None = None

    # user: UserFilter | None = FilterDepends(with_prefix("user", UserFilter))

    order_by: list[str] = ['-creation_datetime']

    class Constants(Filter.Constants):
        model = db_models.Order
