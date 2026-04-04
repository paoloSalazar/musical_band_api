"""
MusicianEventPayment model - tracks payments for musician salaries in events
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class MusicianEventPayment(Base):
    __tablename__ = "musician_event_payments"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_type = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="musician_payments")
    user = relationship("User", back_populates="musician_payments")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Can add validation if needed

    def __repr__(self):
        return f"<MusicianEventPayment(event_id={self.event_id}, user_id={self.user_id}, amount={self.amount})>"