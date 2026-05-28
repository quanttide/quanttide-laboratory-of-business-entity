from datetime import datetime

from pydantic import BaseModel, EmailStr


class CandidateCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    school: str | None = None
    major: str | None = None
    degree: str | None = None
    resume_url: str | None = None
    source: str | None = None
    tags: str | None = None
    notes: str | None = None


class CandidateUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    school: str | None = None
    major: str | None = None
    degree: str | None = None
    resume_url: str | None = None
    source: str | None = None
    tags: str | None = None
    notes: str | None = None


class CandidateRead(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    school: str | None
    major: str | None
    degree: str | None
    resume_url: str | None
    source: str | None
    tags: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
