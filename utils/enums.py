from enum import IntEnum


class UserRoles(IntEnum):
    SUSPENDED = -1
    DEFAULT = 0
    TEACHER = 1
    ADMIN = 2
