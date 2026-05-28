from datetime import datetime

from pydantic import BaseModel

from app.models.talent import TalentStage


class TalentCreate(BaseModel):
    user_profile_id: int
    stage: TalentStage = TalentStage.NEW
    assigned_to: str | None = None
    source: str | None = None
    tags: str | None = None


class TalentUpdate(BaseModel):
    stage: TalentStage | None = None
    assigned_to: str | None = None
    source: str | None = None
    tags: str | None = None


class TalentTransition(BaseModel):
    stage: TalentStage


class TalentRead(BaseModel):
    id: int
    recruitment_id: int
    user_profile_id: int
    stage: TalentStage
    stage_history: str | None
    assigned_to: str | None
    source: str | None
    tags: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
