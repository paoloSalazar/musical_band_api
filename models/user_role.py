from sqlalchemy import Column, Integer, String, Text
from config.database import Base

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<UserRole(name={self.name}, description={self.description})>"