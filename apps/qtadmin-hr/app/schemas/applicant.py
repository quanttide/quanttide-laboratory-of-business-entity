from datetime import datetime

from pydantic import BaseModel

from app.models.applicant import ApplicantStage


class ApplicantCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    school: str | None = None
    major: str | None = None
    resume_url: str | None = None
    stage: ApplicantStage = ApplicantStage.NEW
    assigned_to: str | None = None
    source: str | None = None
    tags: str | None = None


class ApplicantUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    school: str | None = None
    major: str | None = None
    resume_url: str | None = None
    assigned_to: str | None = None
    source: str | None = None
    tags: str | None = None


class ApplicantTransition(BaseModel):
    stage: ApplicantStage


class ApplicantRead(BaseModel):
    id: int
    recruitment_id: int
    name: str
    email: str
    phone: str | None
    school: str | None
    major: str | None
    resume_url: str | None
    stage: ApplicantStage
    stage_history: str | None
    assigned_to: str | None
    source: str | None
    tags: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
