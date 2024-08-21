from sqlalchemy.orm import Session

from db import models
from .base import CRUD
from schemas.order import Order, OrderFilter


class OrderCRUD(CRUD):
    async def create(self, db: Session, data_in: dict):
        id_materials = data_in.pop("id_materials")
        order = await super().create(db, data_in)

        for id_material in id_materials:
            row = models.MaterialByOrder(id_order=order.id, id_material=id_material)
            db.add(row)
            db.commit()

        return await self.get_by_id(db, order.id)


OrderLogic = OrderCRUD(db_model=models.Order, model=Order, filter_model=OrderFilter)
