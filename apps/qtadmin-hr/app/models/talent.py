import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TalentStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    EXAM_SENT = "exam_sent"
    EXAM_RECEIVED = "exam_received"
    EVALUATING = "evaluating"
    INTERVIEW = "interview"
    OFFER = "offer"
    CLOSED = "closed"


STATUS_TRANSITIONS = {
    TalentStatus.NEW: [TalentStatus.CONTACTED, TalentStatus.CLOSED],
    TalentStatus.CONTACTED: [TalentStatus.EXAM_SENT, TalentStatus.CLOSED],
    TalentStatus.EXAM_SENT: [TalentStatus.EXAM_RECEIVED, TalentStatus.CLOSED],
    TalentStatus.EXAM_RECEIVED: [TalentStatus.EVALUATING, TalentStatus.CLOSED],
    TalentStatus.EVALUATING: [TalentStatus.INTERVIEW, TalentStatus.EXAM_SENT, TalentStatus.CLOSED],
    TalentStatus.INTERVIEW: [TalentStatus.OFFER, TalentStatus.CLOSED],
    TalentStatus.OFFER: [TalentStatus.CLOSED],
    TalentStatus.CLOSED: [],
}


class Talent(Base):
    __tablename__ = "talents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recruitment_id: Mapped[int] = mapped_column(ForeignKey("recruitments.id"), index=True)
    user_profile_id: Mapped[int] = mapped_column(Integer, index=True, comment="引用 Auth 系统 UserProfile.id")

    status: Mapped[TalentStatus] = mapped_column(Enum(TalentStatus), default=TalentStatus.NEW, index=True)
    status_history: Mapped[str | None] = mapped_column(Text)
    assigned_to: Mapped[str | None] = mapped_column(String(200))
    source: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[str | None] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    recruitment: Mapped["Recruitment"] = relationship(back_populates="talents")
