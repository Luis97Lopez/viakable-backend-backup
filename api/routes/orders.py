from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from fastapi_filter import FilterDepends

from logic.order import OrderLogic

from db.dependencies import get_db
from sqlalchemy.orm import Session
from utils.logs import get_logger
from utils.config import get_settings
from utils import enums

from api.dependencies import is_super_user_or_is_admin, get_active_current_user, is_operator_user

import schemas
from schemas.paginated import Paginated
from schemas.user import User

logger = get_logger(__name__)
settings = get_settings()


router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


async def validate_order(db: Session, id_forklift: int, materials_order: list):
    return True


async def validate_can_cancel_order(db: Session):
    return True


@router.get("", response_model=Paginated[list[schemas.order.PublicOrder]])
async def read_my_orders(order_filter: schemas.order.OrderFilter = FilterDepends(schemas.order.OrderFilter),
                         page: int = 1, skip: int = 0, size: int = 100,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_active_current_user)):
    total = await OrderLogic.get_rows_count(db)
    size = min(size, settings.app.maximum_page_size)
    absolute_skip = (max(page, 1) - 1) * size + skip
    return Paginated[list[schemas.order.Order]](
        data=await OrderLogic.filter_by_query_partial(db, query=order_filter,
                                                      skip=absolute_skip, limit=size),
        total=total,
        page=page,
        size=size
    )


@router.get("/{target_order_id}", response_model=schemas.order.PublicOrder)
async def read_my_individual_order(target_order_id: int,
                                   db: Session = Depends(get_db),
                                   current_user: User = Depends(get_active_current_user)):
    db_order = await OrderLogic.get_by_id(db, row_id=target_order_id)
    if not db_order or db_order.id_operator is not current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist")
    return db_order


@router.post("", response_model=schemas.order.PublicOrder,
             dependencies=[Depends(is_operator_user)])
async def create_order(order_data: schemas.order.OrderCreate,
                       db: Session = Depends(get_db),
                       current_user: schemas.user.User = Depends(get_active_current_user)):
    await validate_order(db, order_data.id_forklift, order_data.materials_order)
    order_data.id_operator = current_user.id
    try:
        return await OrderLogic.create(db, data_in=order_data.model_dump())
    except IntegrityError:
        logger.debug("Order already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong foreign keys")


@router.delete("/{target_order_id}", response_model=schemas.order.PublicOrder,
               dependencies=[Depends(is_operator_user)])
async def cancel_order(target_order_id: int,
                       db: Session = Depends(get_db),
                       current_user: schemas.user.User = Depends(get_active_current_user)):
    order_obj: schemas.order.Order = \
        await OrderLogic.get_by_id(db, target_order_id)

    if order_obj.id_operator is not current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if not order_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order_obj.canceled:
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Order already canceled")

    await validate_can_cancel_order(db)

    try:
        return await OrderLogic.update(db=db, row_id=target_order_id,
                                       data_changes={"canceled": True})
    except IntegrityError:
        logger.debug("Order already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already exist")
