from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_filter import FilterDepends

from logic import ForkliftLogic
from db.dependencies import get_db
from sqlalchemy.orm import Session
from api.dependencies import is_super_user_or_is_admin, get_active_current_user
from utils.logs import get_logger
import schemas
from utils.config import get_settings
from schemas.paginated import Paginated
from api.routes.users import create_user, update_user, delete_user


settings = get_settings()
logger = get_logger(__name__)


router = APIRouter(
    prefix='/forklifts',
    tags=['crud_forklift', 'platform']
)

# ------------------------
# CRUD endpoints
# ------------------------


@router.get("", response_model=Paginated[list[schemas.forklift.PublicForklift]],
            dependencies=[Depends(get_active_current_user)], tags=['mobile'])
async def read_forklifts(
        forklift_filter: schemas.forklift.ForkliftFilter = FilterDepends(schemas.forklift.ForkliftFilter),
        page: int = 1, skip: int = 0, size: int = 100, db: Session = Depends(get_db)):
    total = await ForkliftLogic.get_rows_count(db)
    size = min(size, settings.app.maximum_page_size)
    absolute_skip = (max(page, 1) - 1) * size + skip
    return Paginated[list[schemas.forklift.Forklift]](
        data=await ForkliftLogic.filter_by_query_partial(db, query=forklift_filter, skip=absolute_skip, limit=size),
        total=total,
        page=page,
        size=size
    )


@router.get("/{target_forklift_id}", response_model=schemas.forklift.PublicForklift,
            dependencies=[Depends(get_active_current_user)], tags=['mobile'])
async def read_forklift(target_forklift_id: int, db: Session = Depends(get_db)):
    db_forklift = await ForkliftLogic.get_by_id(db, row_id=target_forklift_id)
    if not db_forklift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forklift does not exist")
    return db_forklift


@router.post("", response_model=schemas.forklift.PublicForklift, dependencies=[Depends(is_super_user_or_is_admin)])
async def create_forklift(data_in: schemas.forklift.ForkliftCreate, db: Session = Depends(get_db)):
    user = await create_user(data_in, db)
    target_forklift_id = user.id
    forklift = await ForkliftLogic.create(db, {**data_in.model_dump(), "user_id": target_forklift_id})
    return forklift


@router.patch("/{target_user_id}", response_model=schemas.forklift.PublicForklift,
              dependencies=[Depends(is_super_user_or_is_admin)])
async def update_forklift(target_user_id: int, data_in: schemas.forklift.ForkliftPartialIn, db: Session = Depends(get_db)):
    forklift = await ForkliftLogic.get_by_user_id(db, target_user_id)
    if not forklift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forklift not found")
    await ForkliftLogic.update(db, forklift.id, data_in.model_dump(exclude_none=True))
    await update_user(target_user_id, schemas.user.ModifyUserByAdmin(**data_in.model_dump(exclude_none=True)), db)
    return forklift


@router.delete("/{target_user_id}", dependencies=[Depends(is_super_user_or_is_admin)])
async def remove_forklift(target_user_id: int, db: Session = Depends(get_db)):
    forklift = await ForkliftLogic.get_by_user_id(db, target_user_id)
    if not forklift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forklift not found")
    await delete_user(target_user_id, db)
