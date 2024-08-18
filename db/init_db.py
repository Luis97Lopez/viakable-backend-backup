import logging

from db.base import SessionLocal
from schemas.user import FirstSuperUserCreate
from logic.user import UserLogic
from utils.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


async def create_first_super_user(db: SessionLocal) -> bool:
    data = {
        'username': settings.app.super_user_username,
        'password': settings.app.super_user_password
    }

    try:
        super_user = FirstSuperUserCreate(**data)
        user = await UserLogic.get_super_user(db)
        if not user:
            await UserLogic.create(db, data_in=super_user)
    except Exception as e:
        logger.error(f"Something wrong creating first super user {e}")
        return False
    return True


async def create_base_roles(db: SessionLocal) -> bool:
    # TODO
    return True


async def init_db() -> bool:
    try:
        from db.dependencies import get_db
        db = next(get_db())
    except Exception as e:
        logger.error(f"Could not connect DB {e}")
        return False

    return await create_first_super_user(db) and await create_base_roles(db)
