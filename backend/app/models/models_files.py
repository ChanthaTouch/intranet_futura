
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, DateTime, BigInteger
from datetime import datetime
from ..db import Base

class ProjectFileVersion(Base):
    __tablename__ = "project_file_versions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("project_files.id", ondelete="CASCADE"), index=True)
    revision_no: Mapped[int] = mapped_column(Integer, default=1)
    stored_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str | None] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProjectFolderPermission(Base):
    __tablename__ = "project_folder_permissions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(Integer, index=True)
    folder_id: Mapped[int | None] = mapped_column(ForeignKey("project_folders.id", ondelete="CASCADE"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    can_read: Mapped[int] = mapped_column(Integer, default=1)   # 0/1
    can_write: Mapped[int] = mapped_column(Integer, default=0)  # 0/1
