from sqlalchemy.orm import Session

from db import models
from .base import CRUD
from schemas.order import Order, OrderFilter


class OrderCRUD(CRUD):
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
