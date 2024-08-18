from sqlalchemy.orm import Session

import schemas.user
from db import models
from .base import CRUD
from schemas.user import UserPartialIn, UpdatePassword, User, FirstSuperUserCreate, CreateUserByAdmin
from utils.hash_helper import get_hash_password


class UserCRUD(CRUD):
    async def activate_user(self, db: Session, row_id: int):
        return await super().update(db, row_id, {"isActive": True})

    async def create(self, db: Session, data_in: CreateUserByAdmin | FirstSuperUserCreate):
        user_data = data_in.model_dump()
        hashed_password = get_hash_password(user_data.pop('password'))
        user_data['password'] = hashed_password
        is_super_user = user_data.get('isSuperUser', False)
        user_data['isSuperUser'] = is_super_user
        return await super().create(db, user_data)

    async def update(self, db: Session, row_id: int, data_changes: UserPartialIn | dict):
        if not isinstance(data_changes, dict):
            data_changes = data_changes.model_dump(exclude_none=True)
        return await super().update(db=db, row_id=row_id, data_changes=data_changes)

    async def change_password(self, db: Session, row_id: int, password: str):
        hashed_password = get_hash_password(password)
        data_changes = UpdatePassword(password=hashed_password).model_dump()
        return await super().update(db=db, row_id=row_id, data_changes=data_changes)

    async def get_by_username(self, db: Session, username: str):
        return await self.parse(db.query(self.db_model).filter(models.User.username == username).first())

    async def get_user_password(self, db: Session, row_id: int):
        data = await self.get_by_id(db, row_id)
        return data.password

    async def get_super_user(self, db: Session):
        return await self.parse(db.query(self.db_model).filter(models.User.isSuperUser == True).first())


UserLogic = UserCRUD(db_model=models.User, model=User, filter_model=schemas.user.UserFilter)
