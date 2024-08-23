from typing import Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from db import models
from .base import CRUD
from schemas.order import Order, OrderFilter


def to_utc(dt: datetime) -> datetime:
    if not dt.tzinfo:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class OrderCRUD(CRUD):
    async def parse(self, row: Any):
        row.estimate_datetime = to_utc(row.estimate_datetime)
        row.creation_datetime = to_utc(row.creation_datetime)
        return await super().parse(row)

    async def create(self, db: Session, data_in: dict):
        materials_order = data_in.pop("materials_order")
        order = await super().create(db, data_in)

        for material_order in materials_order:
            row = models.MaterialByOrder(id_order=order.id, id_material=material_order.get("id_material"),
                                         quantity=material_order.get("quantity"))
            db.add(row)
            db.commit()

        return await self.get_by_id(db, order.id)


OrderLogic = OrderCRUD(db_model=models.Order, model=Order, filter_model=OrderFilter)
