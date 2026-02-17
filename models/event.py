from sqlalchemy import Column, Integer, String, Date, Time, DateTime
from sqlalchemy.sql import func
from config.database import Base


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
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Event(name={self.name}, place={self.place})>"
