from pydantic import BaseModel, ConfigDict


class Role(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
