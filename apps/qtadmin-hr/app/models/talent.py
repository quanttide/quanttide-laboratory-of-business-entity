import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TalentStage(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    EXAM_SENT = "exam_sent"
    EXAM_RECEIVED = "exam_received"
    EVALUATING = "evaluating"
    INTERVIEW = "interview"
    OFFER = "offer"
    CLOSED = "closed"


STAGE_TRANSITIONS = {
    TalentStage.NEW: [TalentStage.CONTACTED, TalentStage.CLOSED],
    TalentStage.CONTACTED: [TalentStage.EXAM_SENT, TalentStage.CLOSED],
    TalentStage.EXAM_SENT: [TalentStage.EXAM_RECEIVED, TalentStage.CLOSED],
    TalentStage.EXAM_RECEIVED: [TalentStage.EVALUATING, TalentStage.CLOSED],
    TalentStage.EVALUATING: [TalentStage.INTERVIEW, TalentStage.EXAM_SENT, TalentStage.CLOSED],
    TalentStage.INTERVIEW: [TalentStage.OFFER, TalentStage.CLOSED],
    TalentStage.OFFER: [TalentStage.CLOSED],
    TalentStage.CLOSED: [],
}


class Talent(Base):
    __tablename__ = "talents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recruitment_id: Mapped[int] = mapped_column(ForeignKey("recruitments.id"), index=True)

    real_name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str] = mapped_column(String(200), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    school: Mapped[str | None] = mapped_column(String(200))
    major: Mapped[str | None] = mapped_column(String(200))
    resume_url: Mapped[str | None] = mapped_column(Text)

    stage: Mapped[TalentStage] = mapped_column(Enum(TalentStage), default=TalentStage.NEW, index=True)
    stage_history: Mapped[str | None] = mapped_column(Text)
    assigned_to: Mapped[str | None] = mapped_column(String(200))
    source: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[str | None] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    recruitment: Mapped["Recruitment"] = relationship(back_populates="talents")

