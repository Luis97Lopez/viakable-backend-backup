from typing import Any


def has_role(role: str, roles: list[Any]):
    for r in roles:
        if role == getattr(r, "id", "unknown"):
            return True
    return False
