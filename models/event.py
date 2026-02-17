import enum
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Enum
from sqlalchemy.sql import func
from config.database import Base


class EventStatus(str, enum.Enum):
    """Enum for event status values"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    place = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    created_by = Column(String(100), nullable=False)
    reference_phone = Column(String(20), nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.PENDING, server_default=EventStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.status is None:
            self.status = EventStatus.PENDING

    def __repr__(self):
        return f"<Event(name={self.name}, place={self.place})>"
