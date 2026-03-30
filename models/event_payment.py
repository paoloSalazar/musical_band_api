"""
EventPayment model - tracks payments for events
"""
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class PaymentType(str, enum.Enum):
    """Enum for payment type values"""
    ADVANCE = "ADVANCE"
    REMAINING = "REMAINING"
    TOTAL = "TOTAL"


class EventPayment(Base):
    __tablename__ = "event_payments"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_type = Column(String(20), nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="payments")
    user = relationship("User", back_populates="payments")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.payment_type and isinstance(self.payment_type, PaymentType):
            self.payment_type = self.payment_type.value

    def __repr__(self):
        return f"<EventPayment(event_id={self.event_id}, amount={self.amount}, type={self.payment_type})>"