from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from config.database import Base
from datetime import date

class MusicianAvailability(Base):
    __tablename__ = "musician_availability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    musician_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    unavailable_date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    musician = relationship("User", backref="availabilities")

    # Constraint to ensure unavailable_date is not in the past
    __table_args__ = (
        CheckConstraint('unavailable_date >= CURRENT_DATE', name='check_unavailable_date_future'),
    )

    @validates('unavailable_date')
    def validate_unavailable_date(self, key, value):
        if value < date.today():
            raise ValueError("Unavailable date cannot be in the past")
        return value

    def __repr__(self):
        return f"<MusicianAvailability(musician_id={self.musician_id}, date={self.unavailable_date})>"