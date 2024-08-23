from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from fastapi_filter import FilterDepends

from logic.order import OrderLogic

from db.dependencies import get_db
from sqlalchemy.orm import Session
from utils.logs import get_logger
from utils.config import get_settings
from utils import enums

from api.dependencies import get_active_current_user, is_operator_user, is_forklift_user

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
async def read_orders(order_filter: schemas.order.OrderFilter = FilterDepends(schemas.order.OrderFilter),
                      page: int = 1, skip: int = 0, size: int = 100,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_active_current_user)):
    if enums.has_role(enums.UserRoles.OPERATOR, current_user.roles):
        order_filter.id_operator = current_user.id
    elif enums.has_role(enums.UserRoles.FORKLIFT, current_user.roles):
        order_filter.id_forklift = current_user.id

    total = await OrderLogic.count_rows_by_query_partial(db, query=order_filter)
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
async def read_individual_order(target_order_id: int,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_active_current_user)):
    db_order = await OrderLogic.get_by_id(db, row_id=target_order_id)

    order_not_exist_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist")

    if not db_order:
        raise order_not_exist_exception

    if enums.has_role(enums.UserRoles.OPERATOR, current_user.roles) and db_order.id_operator is not current_user.id:
        raise order_not_exist_exception

    if enums.has_role(enums.UserRoles.FORKLIFT, current_user.roles):
        raise order_not_exist_exception

    return db_order


# ------------------------
# Mobile process endpoints
# ------------------------


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


@router.post("/{target_order_id}/confirm", response_model=schemas.order.PublicOrder,
             dependencies=[Depends(is_operator_user)])
async def confirm_order(target_order_id: int, db: Session = Depends(get_db),
                        current_user: schemas.user.User = Depends(get_active_current_user)):
    order = await read_individual_order(target_order_id, db, current_user)

    if order.state in [enums.OrderStates.CONFIRMED]:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Already confirmed and delivered")

    if order.state in [enums.OrderStates.CANCELED_BY_OPERATOR, enums.OrderStates.CANCELED_NO_MATERIAL]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is canceled can't confirm")

    try:
        return await OrderLogic.update(db, target_order_id, {"state": enums.OrderStates.CONFIRMED})
    except IntegrityError:
        logger.debug("Order already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong foreign keys")


@router.post("/{target_order_id}/cancel-by-operator", response_model=schemas.order.PublicOrder,
             dependencies=[Depends(is_operator_user)])
async def cancel_order_by_operator(target_order_id: int, db: Session = Depends(get_db),
                                   current_user: schemas.user.User = Depends(get_active_current_user)):
    order = await read_individual_order(target_order_id, db, current_user)

    if order.state in [enums.OrderStates.CANCELED_BY_OPERATOR, enums.OrderStates.CANCELED_NO_MATERIAL]:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Already canceled")

    if order.state == enums.OrderStates.DELIVERED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is delivered can't cancel")

    try:
        return await OrderLogic.update(db, target_order_id, {"state": enums.OrderStates.CANCELED_BY_OPERATOR})
    except IntegrityError:
        logger.debug("Order already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong foreign keys")


@router.post("/{target_order_id}/cancel-by-forklift", response_model=schemas.order.PublicOrder,
             dependencies=[Depends(is_forklift_user)])
async def cancel_order_by_forklift(target_order_id: int, db: Session = Depends(get_db),
                                   current_user: schemas.user.User = Depends(get_active_current_user)):
    order = await read_individual_order(target_order_id, db, current_user)

    if order.state in [enums.OrderStates.CANCELED_BY_OPERATOR, enums.OrderStates.CANCELED_NO_MATERIAL]:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Already canceled")

    if order.state == enums.OrderStates.DELIVERED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is delivered can't cancel")

    try:
        return await OrderLogic.update(db, target_order_id, {"state": enums.OrderStates.CANCELED_NO_MATERIAL})
    except IntegrityError:
        logger.debug("Order already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong foreign keys")


@router.post("/{target_order_id}/deliver", response_model=schemas.order.PublicOrder,
             dependencies=[Depends(is_forklift_user)])
async def notify_order_delivered(target_order_id: int, db: Session = Depends(get_db),
                                 current_user: schemas.user.User = Depends(get_active_current_user)):
    order = await read_individual_order(target_order_id, db, current_user)

    if order.state in [enums.OrderStates.CONFIRMED, enums.OrderStates.DELIVERED]:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Already confirmed and delivered")

    if order.state in [enums.OrderStates.CANCELED_BY_OPERATOR, enums.OrderStates.CANCELED_NO_MATERIAL]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is canceled can't notify")

    try:
        return await OrderLogic.update(db, target_order_id, {"state": enums.OrderStates.CANCELED_NO_MATERIAL})
    except IntegrityError:
        logger.debug("Order already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong foreign keys")
