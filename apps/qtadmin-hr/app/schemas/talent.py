from datetime import datetime

from pydantic import BaseModel

from app.models.talent import TalentStatus


class TalentCreate(BaseModel):
    user_profile_id: int
    status: TalentStatus = TalentStatus.NEW


class TalentUpdate(BaseModel):
    status: TalentStatus | None = None


class TalentTransition(BaseModel):
    status: TalentStatus


class TalentRead(BaseModel):
    id: int
    recruitment_id: int
    user_profile_id: int
    status: TalentStatus
    status_history: str | None
    assigned_to: str | None
    source: str | None
    tags: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
