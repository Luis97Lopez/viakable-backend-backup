from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_filter import FilterDepends


from logic.user import UserLogic
from api.dependencies import get_active_current_user, is_super_user, is_super_user_or_is_admin
from utils.hash_helper import verify_password
from utils.logs import get_logger
import schemas
from utils.config import get_settings
from schemas.paginated import Paginated

from db.dependencies import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DBAPIError
from uuid import UUID


settings = get_settings()
logger = get_logger(__name__)


router = APIRouter(
    prefix='/users',
    tags=['users'],
)

# ------------------------
# ME endpoints
# ------------------------


@router.get("/me", response_model=schemas.user.PublicUser)
async def read_user_me(current_user: schemas.user.User = Depends(get_active_current_user)):
    return current_user


@router.patch("/me", response_model=schemas.user.PublicUser)
async def update_user_me(partial_user: schemas.user.UserPartialIn,
                         current_user: schemas.user.User = Depends(get_active_current_user),
                         db: Session = Depends(get_db)):
    return await UserLogic.update(db, current_user.id, partial_user)


@router.patch("/me/change-password", response_model=schemas.user.PublicUser)
async def update_password_me(passwords: schemas.user.ChangePasswordUser,
                             current_user: schemas.user.User = Depends(get_active_current_user),
                             db: Session = Depends(get_db)):
    user = await UserLogic.get_by_id(db, current_user.id)
    user_password = await UserLogic.get_user_password(db, current_user.id)
    if not verify_password(passwords.oldPassword, user_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    return await UserLogic.change_password(db, user.id, passwords.password)


# ------------------------
# CRUD endpoints
# ------------------------


@router.get("/{target_user_id}", response_model=schemas.user.PublicUser,
            dependencies=[Depends(is_super_user_or_is_admin)], include_in_schema=False)
async def read_user(target_user_id: int, db: Session = Depends(get_db)):
    db_user = await UserLogic.get_by_id(db, row_id=target_user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    return db_user


@router.post("", response_model=schemas.user.PublicUser,
             dependencies=[Depends(is_super_user_or_is_admin)], include_in_schema=False)
async def create_user(user_data: schemas.user.UserCreate,
                      db: Session = Depends(get_db)):
    logger.debug(f"Creating a user {user_data.username}")
    try:
        base_data = user_data.model_dump(exclude_none=True)
        user_final_data = schemas.user.CreateUserByAdmin(**base_data)
        return await UserLogic.create(db, data_in=user_final_data)
    except IntegrityError:
        logger.debug("User already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User already exist")


@router.patch("/{target_user_id}", response_model=schemas.user.PublicUser,
              dependencies=[Depends(is_super_user_or_is_admin)], include_in_schema=False)
async def update_user(target_user_id: int, partial_user: schemas.user.ModifyUserByAdmin,
                      db: Session = Depends(get_db)):
    user = await UserLogic.get_by_id(db, target_user_id)
    if user.isSuperUser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't edit this user")

    try:
        user = await UserLogic.update(db=db, row_id=target_user_id, data_changes=partial_user)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except DBAPIError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error: Username already registered.")


@router.patch("/{target_user_id}/change-password", response_model=schemas.user.PublicUser,
              dependencies=[Depends(is_super_user_or_is_admin)], include_in_schema=False)
async def update_user_password_by_admin(target_user_id: UUID,
                                        passwords: schemas.user.ChangePasswordUser,
                                        db: Session = Depends(get_db)):
    user = await UserLogic.get_by_id(db, target_user_id)
    if user.isSuperUser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't edit this user")
    return await UserLogic.change_password(db, user.id, passwords.password)


@router.delete("/{target_user_id}", dependencies=[Depends(is_super_user)], include_in_schema=False)
async def delete_user(target_user_id: UUID, db: Session = Depends(get_db)):
    user: schemas.user.User = await UserLogic.get_by_id(db, target_user_id)
    if user.isSuperUser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't remove this user")

    try:
        if not await UserLogic.delete(db=db, row_id=target_user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except DBAPIError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't delete User, related to other data")
