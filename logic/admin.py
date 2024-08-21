from db import models
from .base import CRUD
from schemas.admin import Admin, AdminFilter, AdminCreate
from sqlalchemy.orm import Session
from utils.enums import UserRoles


class AdminCRUD(CRUD):
    async def create(self, db: Session, data_in: dict):
        row = models.RoleByUser(**{"id_role": UserRoles.ADMIN, "id_user": data_in["user_id"]})
        db.add(row)
        db.commit()
        return await super().create(db, {"id": row.id, **data_in})


AdminLogic = AdminCRUD(db_model=models.Admin, model=Admin, filter_model=AdminFilter)
