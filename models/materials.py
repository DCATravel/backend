from core.database import Base
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String


class Materials(Base):
    __tablename__ = "materials"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)
    destination_name = Column(String, nullable=True)
    file_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    dimensions = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)