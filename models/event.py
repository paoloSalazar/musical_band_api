import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
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
    start_datetime = Column(DateTime(timezone=False), nullable=False)
    end_datetime = Column(DateTime(timezone=False), nullable=False)
    is_all_day = Column(Boolean, default=False, server_default='false', nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.PENDING, server_default=EventStatus.PENDING, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=True, default=Numeric("0.00"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to User
    user = relationship("User", back_populates="events")
    
    # Relationship to Payments
    payments = relationship("EventPayment", back_populates="event")

    # Relationship to Musicians
    musicians = relationship("EventMusician", back_populates="event")

    # Relationship to Musician Payments
    musician_payments = relationship("MusicianEventPayment", back_populates="event")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.status is None:
            self.status = EventStatus.PENDING
        if self.is_all_day is None:
            self.is_all_day = False

    def __repr__(self):
        return f"<Event(name={self.name}, place={self.place})>"
