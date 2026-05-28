from datetime import datetime

from pydantic import BaseModel


class RequisitionCreate(BaseModel):
    org_position_id: int
    headcount: int = 1
    reason: str | None = None
    recruiter: str | None = None
    target_start_date: str | None = None


class RequisitionUpdate(BaseModel):
    org_position_id: int | None = None
    headcount: int | None = None
    reason: str | None = None
    recruiter: str | None = None
    target_start_date: str | None = None
    status: str | None = None


class RequisitionRead(BaseModel):
    id: int
    org_position_id: int
    org_position_name: str | None
    headcount: int
    reason: str | None
    recruiter: str | None
    target_start_date: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
