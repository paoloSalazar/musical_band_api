from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from config.database import Base


class UserDetail(Base):
    __tablename__ = "user_details"
    __table_args__ = (
        UniqueConstraint('user_id', 'detail_type', name='uq_user_detail_type'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    detail_type = Column(String(50), nullable=False)
    detail_value = Column(String(255), nullable=False)

    # Relationship to User
    user = relationship("User", back_populates="details")

    def __repr__(self):
        return f"<UserDetail(user_id={self.user_id}, type={self.detail_type})>"
