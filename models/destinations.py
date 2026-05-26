from core.database import Base
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String


class Destinations(Base):
    __tablename__ = "destinations"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_popular = Column(Boolean, nullable=True, default=False, server_default='false')
    is_monthly = Column(Boolean, nullable=True, default=False, server_default='false')
    rating = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)