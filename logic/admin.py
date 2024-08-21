from db import models
from .base import CRUD
from schemas.admin import Admin, AdminFilter, AdminCreate
from sqlalchemy.orm import Session
from sqlalchemy import and_
from utils.enums import UserRoles


class AdminCRUD(CRUD):
    async def create(self, db: Session, data_in: dict):
        extra_data = {"id_role": UserRoles.ADMIN, "id_user": data_in["user_id"]}
        row = models.RoleByUser(**extra_data)
        db.add(row)
        db.commit()

        fields = ["firstName", "lastName"]
        admin_data = {}
        for field in fields:
            admin_data[field] = data_in[field]

        return await super().create(db, {"id": row.id, **admin_data})

    async def update_by_user_id(self, db: Session, user_id: int, data_changes: dict):
        admin = await self.get_by_user_id(db, user_id)
        return await super().update(db, admin.id, data_changes)

    async def get_by_user_id(self, db: Session, user_id: int):
        user_by_role = db.query(models.RoleByUser).filter(and_(models.RoleByUser.id_user == user_id,
                                                               models.RoleByUser.id_role == UserRoles.ADMIN)).first()
        if not user_by_role:
            return None
        return self.parse(db.query(self.db_model).filter(self.db_model.id == user_by_role.id).first())


AdminLogic = AdminCRUD(db_model=models.Admin, model=Admin, filter_model=AdminFilter)
