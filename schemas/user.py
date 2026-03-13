from pydantic import BaseModel, ConfigDict
from typing import List


class UserBase(BaseModel):
    name: str
    lastname: str
    second_lastname: str | None = None
    email: str
    phone_number: str | None = None
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


class UserUpdate(BaseModel):
    """Schema for updating a user (all fields optional for PATCH)"""
    name: str | None = None
    lastname: str | None = None
    second_lastname: str | None = None
    email: str | None = None
    phone_number: str | None = None
    role_id: int | None = None


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password (requires current password)"""
    current_password: str
    new_password: str


class UserResponseWithRole(BaseModel):
    """Schema for user response including role name."""
    id: int
    name: str
    lastname: str
    second_lastname: str | None = None
    email: str
    phone_number: str | None = None
    role_id: int
    role: str  # Role name

    model_config = ConfigDict(from_attributes=True)


class UserPaginationResponse(BaseModel):
    """Schema for paginated user response."""
    data: List[UserResponseWithRole]
    total: int
    skip: int
    limit: int
