import logging

from schemas.user import FirstSuperUserCreate
from logic import UserLogic, RoleLogic, AdminLogic
from utils.config import get_settings
from sqlalchemy.orm import Session
from utils.enums import UserRoles

logger = logging.getLogger(__name__)

settings = get_settings()


async def create_first_super_user(db: Session) -> bool:
    data = {
        'username': settings.app.super_user_username,
        'password': settings.app.super_user_password
    }

    try:
        super_user = FirstSuperUserCreate(**data)
        user = await UserLogic.get_super_user(db)
        if not user:
            user = await UserLogic.create(db, data_in=super_user)
        admin = await AdminLogic.get_by_user_id(db, user.id)
        if not admin:
            await AdminLogic.create(db, data_in={"user_id": user.id, "firstName": "Super", "lastName": "Admin"})
    except Exception as e:
        logger.error(f"Something wrong creating first super user {e}")
        return False
    return True


async def create_base_roles(db: Session) -> bool:
    try:
        for role in UserRoles:
            row = await RoleLogic.get_by_id(db, role)
            if not row:
                await RoleLogic.create(db, {"id": role})
    except Exception as e:
        logger.error(f"Something wrong creating first super user {e}")
        return False
    return True


async def init_db() -> bool:
    try:
        from db.dependencies import get_db
        db = next(get_db())
    except Exception as e:
        logger.error(f"Could not connect DB {e}")
        return False

    return await create_base_roles(db) and await create_first_super_user(db)
