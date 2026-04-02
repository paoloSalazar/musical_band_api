from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    second_lastname = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    phone_number = Column(String(50), nullable=True)
    role_id = Column(Integer, ForeignKey('user_roles.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    role = relationship("UserRole", back_populates="users")
    events = relationship("Event", back_populates="user")
    details = relationship("UserDetail", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("EventPayment", back_populates="user")

    def __repr__(self):
        return f"<User(name={self.name}, email={self.email})>"