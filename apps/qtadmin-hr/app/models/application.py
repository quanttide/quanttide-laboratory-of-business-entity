import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ApplicationStage(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    EXAM_SENT = "exam_sent"
    EXAM_RECEIVED = "exam_received"
    EVALUATING = "evaluating"
    INTERVIEW = "interview"
    OFFER = "offer"
    CLOSED = "closed"


STAGE_ORDER = {
    ApplicationStage.NEW: 0,
    ApplicationStage.CONTACTED: 1,
    ApplicationStage.EXAM_SENT: 2,
    ApplicationStage.EXAM_RECEIVED: 3,
    ApplicationStage.EVALUATING: 4,
    ApplicationStage.INTERVIEW: 5,
    ApplicationStage.OFFER: 6,
    ApplicationStage.CLOSED: 7,
}

STAGE_TRANSITIONS = {
    ApplicationStage.NEW: [ApplicationStage.CONTACTED, ApplicationStage.CLOSED],
    ApplicationStage.CONTACTED: [ApplicationStage.EXAM_SENT, ApplicationStage.CLOSED],
    ApplicationStage.EXAM_SENT: [ApplicationStage.EXAM_RECEIVED, ApplicationStage.CLOSED],
    ApplicationStage.EXAM_RECEIVED: [ApplicationStage.EVALUATING, ApplicationStage.CLOSED],
    ApplicationStage.EVALUATING: [ApplicationStage.INTERVIEW, ApplicationStage.EXAM_SENT, ApplicationStage.CLOSED],
    ApplicationStage.INTERVIEW: [ApplicationStage.OFFER, ApplicationStage.CLOSED],
    ApplicationStage.OFFER: [ApplicationStage.CLOSED],
    ApplicationStage.CLOSED: [],
}


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"), index=True)
    stage: Mapped[ApplicationStage] = mapped_column(Enum(ApplicationStage), default=ApplicationStage.NEW, index=True)
    stage_history: Mapped[str | None] = mapped_column(Text)
    assigned_to: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    candidate: Mapped["Candidate"] = relationship(back_populates="applications")
    position: Mapped["Position"] = relationship(back_populates="applications")
