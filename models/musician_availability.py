"""
MusicianAvailability model - tracks unavailable dates for musicians
"""
from sqlalchemy import Column, Integer, Date, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
from datetime import date

class MusicianAvailability(Base):
    __tablename__ = "musician_availability"

    id = Column(Integer, primary_key=True, index=True)
    musician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    unavailable_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    musician = relationship("User", back_populates="musician_availability")

    __table_args__ = (
        UniqueConstraint('musician_id', 'unavailable_date', name='uq_musician_availability'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.unavailable_date < date.today():
            raise ValueError("Unavailable date cannot be in the past")

    def __repr__(self):
        return f"<MusicianAvailability(musician_id={self.musician_id}, date={self.unavailable_date})>"