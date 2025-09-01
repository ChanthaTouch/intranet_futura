
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Integer, ForeignKey, DateTime
from datetime import datetime, date
from ..db import Base

class ProjectFolder(Base):
    __tablename__ = "project_folders"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("project_folders.id", ondelete="CASCADE"), nullable=True)
    # e.g. 'Design', 'IFC', 'Renders'
    name: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(1000), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ProjectScheduleItem(Base):
    __tablename__ = "project_schedule_items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("project_schedule_items.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    planned_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    sort_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
