from enum import Enum


class UserRoles(str, Enum):
    FORKLIFT = "montacarga"
    OPERATOR = "operador"
    ADMIN = "admin"
