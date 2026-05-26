from core.database import Base
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String


class Itineraries(Base):
    __tablename__ = "itineraries"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    destination_id = Column(Integer, nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    duration_days = Column(Integer, nullable=False)
    duration_nights = Column(Integer, nullable=True)
    cities_count = Column(Integer, nullable=True)
    season = Column(String, nullable=True)
    price_per_person = Column(Float, nullable=True)
    flight_departure_city = Column(String, nullable=True)
    flight_departure_date = Column(String, nullable=True)
    flight_arrival_city = Column(String, nullable=True)
    flight_arrival_date = Column(String, nullable=True)
    flight_return_date = Column(String, nullable=True)
    flight_stopovers = Column(String, nullable=True)
    activities = Column(String, nullable=True)
    included = Column(String, nullable=True)
    not_included = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True, server_default='true')
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)