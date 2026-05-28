from datetime import datetime

from pydantic import BaseModel


class RecruitmentCreate(BaseModel):
    org_position_id: int
    name: str
    recruiter: str | None = None
    target_date: str | None = None
    description: str | None = None


class RecruitmentUpdate(BaseModel):
    name: str | None = None
    recruiter: str | None = None
    target_date: str | None = None
    status: str | None = None
    description: str | None = None


class RecruitmentRead(BaseModel):
    id: int
    org_position_id: int
    org_position_name: str | None
    name: str
    recruiter: str | None
    target_date: str | None
    status: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
