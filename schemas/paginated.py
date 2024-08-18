from pydantic.generics import GenericModel
from typing import TypeVar
from typing import Generic

T = TypeVar("T")


class GenericField(GenericModel, Generic[T]):
    data: T


class Paginated(GenericField[T], Generic[T]):
    page: int
    size: int
    total: int
