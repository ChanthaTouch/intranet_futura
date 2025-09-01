from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base
from datetime import datetime

class Recruitment(Base):
    __tablename__ = "recruitments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    project = Column(String, nullable=False)
    hiring_manager = Column(String, nullable=False)
    request_date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, nullable=False)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
