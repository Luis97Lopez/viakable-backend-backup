from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_filter import FilterDepends

from logic import AdminLogic
from db.dependencies import get_db
from sqlalchemy.orm import Session
from api.dependencies import is_super_user
from utils.logs import get_logger
import schemas
from utils.config import get_settings
from schemas.paginated import Paginated
from api.routes.users import create_user, update_user, delete_user


settings = get_settings()
logger = get_logger(__name__)


router = APIRouter(
    prefix='/admins',
    tags=['crud_admin', 'platform']
)

# ------------------------
# CRUD endpoints
# ------------------------


@router.get("", response_model=Paginated[list[schemas.admin.PublicAdmin]],
            dependencies=[Depends(is_super_user)])
async def read_admins(admin_filter: schemas.admin.AdminFilter = FilterDepends(schemas.admin.AdminFilter),
                      page: int = 1, skip: int = 0, size: int = 100, db: Session = Depends(get_db)):
    total = await AdminLogic.get_rows_count(db)
    size = min(size, settings.app.maximum_page_size)
    absolute_skip = (max(page, 1) - 1) * size + skip
    return Paginated[list[schemas.admin.Admin]](
        data=await AdminLogic.filter_by_query_partial(db, query=admin_filter, skip=absolute_skip, limit=size),
        total=total,
        page=page,
        size=size
    )


@router.get("/{target_admin_id}", response_model=schemas.admin.PublicAdmin, dependencies=[Depends(is_super_user)])
async def read_admin(target_admin_id: int, db: Session = Depends(get_db)):
    db_admin = await AdminLogic.get_by_id(db, row_id=target_admin_id)
    if not db_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin does not exist")
    return db_admin


@router.post("", response_model=schemas.admin.PublicAdmin, dependencies=[Depends(is_super_user)])
async def create_admin(data_in: schemas.admin.AdminCreate, db: Session = Depends(get_db)):
    user = await create_user(data_in, db)
    target_admin_id = user.id
    admin = await AdminLogic.create(db, {**data_in.model_dump(), "user_id": target_admin_id})
    return admin


@router.patch("/{target_user_id}", response_model=schemas.admin.PublicAdmin, dependencies=[Depends(is_super_user)])
async def update_admin(target_user_id: int, data_in: schemas.admin.AdminPartialIn, db: Session = Depends(get_db)):
    admin = await AdminLogic.get_by_user_id(db, target_user_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    await AdminLogic.update(db, admin.id, data_in.model_dump(exclude_none=True))
    await update_user(target_user_id, schemas.user.ModifyUserByAdmin(**data_in.model_dump(exclude_none=True)), db)
    return admin


@router.delete("/{target_user_id}", dependencies=[Depends(is_super_user)])
async def remove_admin(target_user_id: int, db: Session = Depends(get_db)):
    admin = await AdminLogic.get_by_user_id(db, target_user_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    await delete_user(target_user_id, db)
