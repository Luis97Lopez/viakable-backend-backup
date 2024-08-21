from db import models
from .base import CRUD
from schemas.material import Material, MaterialFilter


class MaterialCRUD(CRUD):
    pass


MaterialLogic = MaterialCRUD(db_model=models.Material, model=Material, filter_model=MaterialFilter)
