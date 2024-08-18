from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_filter import FilterDepends

from logic.user import UserLogic
from db.dependencies import get_db
from sqlalchemy.orm import Session
from uuid import UUID
from api.dependencies import is_super_user
from utils.logs import get_logger
import schemas
from utils.config import get_settings
from schemas.paginated import Paginated
from utils.enums import UserRoles


settings = get_settings()
logger = get_logger(__name__)


router = APIRouter(
    prefix='/admins',
    tags=['admins']
)

server_error_exception = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                       detail="Server Error, please try again later.")


@router.get("", response_model=Paginated[list[schemas.user.PublicUser]],
            dependencies=[Depends(is_super_user)])
async def read_admins(admin_filter: schemas.user.UserFilter = FilterDepends(schemas.user.UserFilter),
                      page: int = 1, skip: int = 0, size: int = 100, db: Session = Depends(get_db)):
    admin_filter.role = UserRoles.ADMIN
    total = await UserLogic.get_number_users_by_role(db, UserRoles.ADMIN)
    size = min(size, settings.app.maximum_page_size)
    absolute_skip = (max(page, 1) - 1) * size + skip
    return Paginated[list[schemas.user.User]](
        data=await UserLogic.filter_by_query_partial(db, query=admin_filter, skip=absolute_skip, limit=size),
        total=total,
        page=page,
        size=size
    )


@router.get("/{target_user_id}", response_model=schemas.user.PublicUser, dependencies=[Depends(is_super_user)])
async def read_admin(target_user_id: UUID, db: Session = Depends(get_db)):
    db_user = await UserLogic.get_by_id(db, row_id=target_user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    return db_user


@router.post("", response_model=schemas.user.PublicUser, dependencies=[Depends(is_super_user)])
async def activate_admin(data_in: schemas.roles.ActivateOrDeactivateRole,
                         db: Session = Depends(get_db)):
    target_user_id = data_in.userId
    try:
        partial_user = {
            "role": UserRoles.ADMIN
        }
        user = await UserLogic.update(db=db, row_id=target_user_id, data_changes=partial_user)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except Exception as e:
        logger.error(f"Server error {e}")
        raise server_error_exception


@router.delete("/{target_user_id}", response_model=schemas.user.PublicUser,
               dependencies=[Depends(is_super_user)])
async def deactivate_admin(target_user_id: UUID, db: Session = Depends(get_db)):
    partial_user = {
        "role": UserRoles.DEFAULT
    }
    user: schemas.user.User = await UserLogic.get_by_id(db, target_user_id)
    if user.isSuperUser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't deactivate this admin")

    try:
        user = await UserLogic.update(db=db, row_id=target_user_id, data_changes=partial_user)
    except Exception as e:
        logger.error(f"Server error {e}")
        raise server_error_exception
    else:
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
