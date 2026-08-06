from pydantic import BaseModel, ConfigDict


class UserRoleBase(BaseModel):
    name: str
    description: str | None = None


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    """Schema for updating a user role - id not required since it's in the URL"""
    name: str | None = None
    description: str | None = None


class UserRole(UserRoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Allows conversion from SQLAlchemy models
