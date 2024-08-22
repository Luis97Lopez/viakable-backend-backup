from typing import Any
from enum import Enum


class UserRoles(str, Enum):
    FORKLIFT = "montacarga"
    OPERATOR = "operador"
    ADMIN = "admin"


class OrderStates(str, Enum):
    PENDING = "pendiente"
    DELIVERED = "entregado"
    CONFIRMED = "confirmado"
    CANCELED_BY_OPERATOR = "cancelado_por_operador"
    CANCELED_NO_MATERIAL = "no_hay_material"


def has_role(role: str, roles: list[Any]):
    for r in roles:
        if role == getattr(r, "id", "unknown"):
            return True
    return False
