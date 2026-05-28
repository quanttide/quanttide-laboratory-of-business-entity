from datetime import datetime

from pydantic import BaseModel


class PlanCreate(BaseModel):
    org_position_id: int
    headcount: int = 1
    reason: str | None = None
    period: str | None = None


class PlanUpdate(BaseModel):
    org_position_id: int | None = None
    headcount: int | None = None
    reason: str | None = None
    period: str | None = None
    status: str | None = None


class PlanRead(BaseModel):
    id: int
    org_position_id: int
    org_position_name: str | None
    headcount: int
    reason: str | None
    period: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
