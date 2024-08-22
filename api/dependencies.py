from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from logic.user import UserLogic
from schemas.user import User
from utils.enums import UserRoles
from utils.jwt_helper import decode_access_token
from db.dependencies import get_db
from sqlalchemy.orm import Session
from utils.logs import get_logger
from utils.roles_helper import has_role


# tokenUrl refers to a relative URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

logger = get_logger(__name__)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await UserLogic.get_by_id(db, row_id=user_id)
    if user is None:
        raise credentials_exception
    logger.debug(f'Sign in user successful: {user.id}')
    return user


async def get_active_current_user(current_user: User = Depends(get_current_user)):
    if not current_user.isActive:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    return current_user


async def is_super_user(current_active_user: User = Depends(get_active_current_user)):
    if not current_active_user.isSuperUser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    return True


async def is_teacher_user(current_active_user: User = Depends(get_active_current_user)):
    # TODO: roles
    if not (True or current_active_user.role == UserRoles.TEACHER):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    return True


async def is_operator_user(current_active_user: User = Depends(get_active_current_user)):
    if not has_role(UserRoles.OPERATOR, current_active_user.roles):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    return True


async def is_super_user_or_is_admin(current_active_user: User = Depends(get_active_current_user)):
    if not (current_active_user.isSuperUser or has_role(UserRoles.ADMIN, current_active_user.roles)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    return True
