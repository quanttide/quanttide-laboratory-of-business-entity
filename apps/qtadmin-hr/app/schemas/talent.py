from datetime import datetime

from pydantic import BaseModel

from app.models.talent import TalentStage


class TalentCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    school: str | None = None
    major: str | None = None
    resume_url: str | None = None
    stage: TalentStage = TalentStage.NEW
    assigned_to: str | None = None
    source: str | None = None
    tags: str | None = None


class TalentUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    school: str | None = None
    major: str | None = None
    resume_url: str | None = None
    assigned_to: str | None = None
    source: str | None = None
    tags: str | None = None


class TalentTransition(BaseModel):
    stage: TalentStage


class TalentRead(BaseModel):
    id: int
    recruitment_id: int
    name: str
    email: str
    phone: str | None
    school: str | None
    major: str | None
    resume_url: str | None
    stage: TalentStage
    stage_history: str | None
    assigned_to: str | None
    source: str | None
    tags: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
