from pydantic import BaseModel, ConfigDict


class UserRoleBase(BaseModel):
    name: str
    description: str | None = None


class UserRoleCreate(UserRoleBase):
    pass


class UserRole(UserRoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Allows conversion from SQLAlchemy models