from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_filter import FilterDepends

from logic import OperatorLogic
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
    prefix='/operators',
    tags=['crud_operator', 'platform']
)

# ------------------------
# CRUD endpoints
# ------------------------


@router.get("", response_model=Paginated[list[schemas.operator.PublicOperator]],
            dependencies=[Depends(get_active_current_user)], tags=['mobile'])
async def read_operators(
        operator_filter: schemas.operator.OperatorFilter = FilterDepends(schemas.operator.OperatorFilter),
        page: int = 1, skip: int = 0, size: int = 100, db: Session = Depends(get_db)):
    total = await OperatorLogic.get_rows_count(db)
    size = min(size, settings.app.maximum_page_size)
    absolute_skip = (max(page, 1) - 1) * size + skip
    return Paginated[list[schemas.operator.Operator]](
        data=await OperatorLogic.filter_by_query_partial(db, query=operator_filter, skip=absolute_skip, limit=size),
        total=total,
        page=page,
        size=size
    )


@router.get("/{target_operator_id}", response_model=schemas.operator.PublicOperator,
            dependencies=[Depends(get_active_current_user)], tags=['mobile'])
async def read_operator(target_operator_id: int, db: Session = Depends(get_db)):
    db_operator = await OperatorLogic.get_by_id(db, row_id=target_operator_id)
    if not db_operator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator does not exist")
    return db_operator


@router.post("", response_model=schemas.operator.PublicOperator, dependencies=[Depends(is_super_user_or_is_admin)])
async def create_operator(data_in: schemas.operator.OperatorCreate, db: Session = Depends(get_db)):
    user = await create_user(data_in, db)
    target_operator_id = user.id
    operator = await OperatorLogic.create(db, {**data_in.model_dump(), "user_id": target_operator_id})
    return operator


@router.patch("/{target_user_id}", response_model=schemas.operator.PublicOperator,
              dependencies=[Depends(is_super_user_or_is_admin)])
async def update_operator(target_user_id: int, data_in: schemas.operator.OperatorPartialIn, db: Session = Depends(get_db)):
    operator = await OperatorLogic.get_by_user_id(db, target_user_id)
    if not operator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator not found")
    await OperatorLogic.update(db, operator.id, data_in.model_dump(exclude_none=True))
    await update_user(target_user_id, schemas.user.ModifyUserByAdmin(**data_in.model_dump(exclude_none=True)), db)
    return operator


@router.delete("/{target_user_id}", dependencies=[Depends(is_super_user_or_is_admin)])
async def remove_operator(target_user_id: int, db: Session = Depends(get_db)):
    operator = await OperatorLogic.get_by_user_id(db, target_user_id)
    if not operator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator not found")
    await delete_user(target_user_id, db)
