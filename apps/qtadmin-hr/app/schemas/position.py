from datetime import datetime

from pydantic import BaseModel


class PositionCreate(BaseModel):
    name: str
    type: str
    description: str | None = None
    requirements: str | None = None
    headcount: int = 1


class PositionUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    description: str | None = None
    requirements: str | None = None
    headcount: int | None = None
    active: bool | None = None


class PositionRead(BaseModel):
    id: int
    name: str
    type: str
    description: str | None
    requirements: str | None
    headcount: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
