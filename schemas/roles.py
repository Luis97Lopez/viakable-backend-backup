from pydantic import BaseModel, UUID4 as UUID


class ActivateOrDeactivateRole(BaseModel):
    userId: UUID
