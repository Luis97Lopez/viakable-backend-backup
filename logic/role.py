from db import models
from .base import CRUD
from schemas.role import Role


class RoleCRUD(CRUD):
    pass


RoleLogic = RoleCRUD(db_model=models.Role, model=Role, filter_model=None)
