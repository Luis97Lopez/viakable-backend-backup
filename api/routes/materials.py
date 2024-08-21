from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_filter import FilterDepends

from logic.material import MaterialLogic
from api.dependencies import is_super_user_or_is_admin, get_active_current_user
from utils.logs import get_logger
import schemas
from utils.config import get_settings
from schemas.paginated import Paginated

from sqlalchemy.orm import Session
from db.dependencies import get_db
from sqlalchemy.exc import IntegrityError


logger = get_logger(__name__)
settings = get_settings()


router = APIRouter(
    prefix='/materials',
    tags=['crud materials', 'platform']
)

server_error_exception = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                       detail="Server Error, please try again later.")


@router.get("", response_model=Paginated[list[schemas.material.PublicMaterial]],
            dependencies=[Depends(get_active_current_user)], tags=['mobile'])
async def read_materials(material_filter: schemas.material.MaterialFilter =
                         FilterDepends(schemas.material.MaterialFilter),
                         page: int = 1, skip: int = 0, size: int = 100, db: Session = Depends(get_db)):
    total = await MaterialLogic.get_rows_count(db)
    size = min(size, settings.app.maximum_page_size)
    absolute_skip = (max(page, 1) - 1) * size + skip
    return Paginated[list[schemas.material.Material]](
        data=await MaterialLogic.filter_by_query_partial(db, query=material_filter, skip=absolute_skip, limit=size),
        total=total,
        page=page,
        size=size
    )


@router.get("/{target_material_id}", response_model=schemas.material.PublicMaterial,
            dependencies=[Depends(get_active_current_user)], tags=['mobile'])
async def read_material(target_material_id: int, db: Session = Depends(get_db)):
    db_material = await MaterialLogic.get_by_id(db, row_id=target_material_id)
    if not db_material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material does not exist")
    return db_material


@router.post("", response_model=schemas.material.PublicMaterial, dependencies=[Depends(is_super_user_or_is_admin)])
async def create_material(material: schemas.material.MaterialCreate, db: Session = Depends(get_db)):
    logger.debug(f"Creating a material {material}")
    try:
        return await MaterialLogic.create(db, data_in=material.model_dump())
    except IntegrityError:
        logger.debug("Material already exists")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Material already exists")


@router.patch("/{target_material_id}", response_model=schemas.material.PublicMaterial,
              dependencies=[Depends(is_super_user_or_is_admin)])
async def update_material(target_material_id: int,
                          partial_material: schemas.material.MaterialPartialIn,
                          db: Session = Depends(get_db)):
    try:
        material = await MaterialLogic.update(db=db, row_id=target_material_id,
                                              data_changes=partial_material.model_dump(exclude_none=True))
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
        return material
    except IntegrityError:
        logger.debug("Material already exists")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Material already exists")


@router.delete("/{target_material_id}", dependencies=[Depends(is_super_user_or_is_admin)])
async def delete_material(target_material_id: int, db: Session = Depends(get_db)):
    if not await MaterialLogic.delete(db=db, row_id=target_material_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
