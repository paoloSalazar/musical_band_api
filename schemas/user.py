from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: str
    lastname: str
    second_lastname: str | None = None
    email: str
    role_id: int


class UserCreate(UserBase):
    """Schema for creating a user (includes password)"""
    password: str


class UserResponse(UserBase):
    """Schema for user responses (excludes password, created_at, updated_at)"""
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: str
    password: str
