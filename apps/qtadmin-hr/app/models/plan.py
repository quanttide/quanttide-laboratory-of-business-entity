from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    org_position_id: Mapped[int] = mapped_column(Integer, index=True, comment="引用 Org 系统的 Position.id")
    org_position_name: Mapped[str | None] = mapped_column(String(200))
    headcount: Mapped[int] = mapped_column(Integer, default=1, comment="计划招聘人数")
    reason: Mapped[str | None] = mapped_column(Text, comment="招聘原因")
    period: Mapped[str | None] = mapped_column(String(100), comment="计划周期，如 2026 Q2")
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True, comment="draft / approved / executing / closed")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    recruitments: Mapped[list["Recruitment"]] = relationship(back_populates="plan", cascade="all, delete-orphan")
