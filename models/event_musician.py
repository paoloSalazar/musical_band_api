import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class PaymentStatus(str, enum.Enum):
    """Enum for musician payment status"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class EventMusician(Base):
    __tablename__ = "event_musicians"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    musician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Text, nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, server_default=PaymentStatus.PENDING, nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="musicians")
    musician = relationship("User", back_populates="event_musicians")

    __table_args__ = (
        UniqueConstraint('event_id', 'musician_id', name='uq_event_musician'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.payment_status is None:
            self.payment_status = PaymentStatus.PENDING

    def __repr__(self):
        return f"<EventMusician(event_id={self.event_id}, musician_id={self.musician_id}, salary={self.salary})>"