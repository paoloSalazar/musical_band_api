"""
EventMusician model - tracks musicians assigned to events with roles, salaries, and payment status
"""
import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
from decimal import Decimal


class PaymentStatus(str, enum.Enum):
    """Enum for payment status values"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"


class EventMusician(Base):
    __tablename__ = "event_musicians"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    musician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(100), nullable=True)
    salary = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String(20), nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="musicians")
    musician = relationship("User", back_populates="event_musicians")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.payment_status is None:
            self.payment_status = "PENDING"
        if self.salary <= Decimal("0.00"):
            raise ValueError("Salary must be positive")
        if self.payment_status and isinstance(self.payment_status, PaymentStatus):
            self.payment_status = self.payment_status.value
        if self.payment_status not in [status.value for status in PaymentStatus]:
            raise ValueError(f"Invalid payment status: {self.payment_status}")

    def __repr__(self):
        return f"<EventMusician(event_id={self.event_id}, musician_id={self.musician_id}, role={self.role}, salary={self.salary})>"