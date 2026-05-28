from datetime import datetime

from pydantic import BaseModel

from app.models.application import ApplicationStage


class ApplicationCreate(BaseModel):
    candidate_id: int
    requisition_id: int
    assigned_to: str | None = None


class ApplicationQuickCreate(BaseModel):
    candidate_name: str
    candidate_email: str
    candidate_school: str | None = None
    candidate_major: str | None = None
    org_position_name: str
    assigned_to: str | None = None


class ApplicationUpdate(BaseModel):
    assigned_to: str | None = None


class StageTransition(BaseModel):
    stage: ApplicationStage


class ApplicationRead(BaseModel):
    id: int
    candidate_id: int
    requisition_id: int
    stage: ApplicationStage
    stage_history: str | None
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
