from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Requisition(Base):
    __tablename__ = "requisitions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    org_position_id: Mapped[int] = mapped_column(Integer, index=True)
    org_position_name: Mapped[str | None] = mapped_column(String(200))
    headcount: Mapped[int] = mapped_column(Integer, default=1)
    reason: Mapped[str | None] = mapped_column(Text)
    recruiter: Mapped[str | None] = mapped_column(String(200))
    target_start_date: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    applications: Mapped[list["Application"]] = relationship(back_populates="requisition", cascade="all, delete-orphan")
