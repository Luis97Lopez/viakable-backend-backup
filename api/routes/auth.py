from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import get_active_current_user
import schemas
from schemas.user import User
from schemas.token import TokenWithUser, RefreshTokenData

from logic.user import UserLogic

from db.dependencies import get_db
from sqlalchemy.orm import Session
from utils.config import get_settings
from utils.hash_helper import verify_password
from utils.jwt_helper import encode_access_token, encode_refresh_token, decode_refresh_token
from utils.logs import get_logger


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

logger = get_logger(__name__)
settings = get_settings()


def get_token_payload(user):
    user_id = str(user.id)
    access_token, access_expires_at = encode_access_token(user_id)
    refresh_token, refresh_expires_at = encode_refresh_token(user_id)

    response = {
        "user": user,
        "accessToken": access_token,
        "accessExpiresAt": access_expires_at,
        "refreshToken": refresh_token,
        "refreshExpiresAt": refresh_expires_at,
        "tokenType": "Bearer"
    }
    return response


@router.post(
    "/login",
    response_model=TokenWithUser,
)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    logger.debug(f"Trying to logging in by {form_data.username}")
    user: User = await UserLogic.get_by_username(db, form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    user_password = await UserLogic.get_user_password(db, user.id)
    if not verify_password(form_data.password, user_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    if not user.isActive:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")
    logger.debug(f"User {user.username} logged in")
    return get_token_payload(user)


@router.post(
    "/refresh",
    response_model=TokenWithUser
)
async def refresh(
        refresh_token_data: RefreshTokenData,
        db: Session = Depends(get_db)
):
    refresh_token = refresh_token_data.refresh_token
    payload: dict = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The provided refresh token is not valid or has expired.")

    user_id = payload.get('sub', None)
    user = await UserLogic.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The provided refresh token is not valid or has expired.")
    return get_token_payload(user)


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
