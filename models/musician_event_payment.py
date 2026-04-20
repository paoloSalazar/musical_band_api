"""
MusicianEventPayment model - tracks payments for musicians assigned to events
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
from models.event_payment import PaymentType
from decimal import Decimal


class MusicianEventPayment(Base):
    __tablename__ = "musician_event_payments"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    musician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payment_type = Column(String(20), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="musician_payments")
    musician = relationship("User", back_populates="musician_event_payments")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.amount <= Decimal("0.00"):
            raise ValueError("Amount must be positive")
        if self.payment_type and isinstance(self.payment_type, PaymentType):
            self.payment_type = self.payment_type.value
        if self.payment_type not in [pt.value for pt in PaymentType]:
            raise ValueError(f"Invalid payment type: {self.payment_type}")

    def __repr__(self):
        return f"<MusicianEventPayment(event_id={self.event_id}, musician_id={self.musician_id}, amount={self.amount}, type={self.payment_type})>"