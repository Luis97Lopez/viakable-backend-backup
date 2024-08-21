from enum import Enum


class UserRoles(str, Enum):
    FORKLIFT = "montacarga"
    OPERATOR = "operador"
    ADMIN = "admin"


class OrderStates(str, Enum):
    PENDING = "pendiente"
    DELIVERED = "entregado"
    CANCELED_BY_OPERATOR = "cancelado_por_operador"
    NO_MATERIAL = "no_hay_material"
