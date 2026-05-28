from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Recruitment(Base):
    __tablename__ = "recruitments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), comment="招聘活动名称，如「5月技术实习生招聘」")
    recruiter: Mapped[str | None] = mapped_column(String(100), comment="负责招聘职能官")
    target_date: Mapped[str | None] = mapped_column(String(50), comment="目标到岗时间")
    status: Mapped[str] = mapped_column(String(50), default="open", index=True, comment="open / closed / cancelled")
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    plan: Mapped["Plan"] = relationship(back_populates="recruitments")
    talents: Mapped[list["Talent"]] = relationship(back_populates="recruitment", cascade="all, delete-orphan")
