from pydantic import BaseModel, ConfigDict


class UserDetailBase(BaseModel):
    user_id: int
    detail_type: str
    detail_value: str


class UserDetailCreate(UserDetailBase):
    """Schema for creating a user detail"""
    pass


class UserDetailUpdate(BaseModel):
    """Schema for updating a user detail (all fields optional for PATCH)"""
    detail_type: str | None = None
    detail_value: str | None = None


class UserDetailResponse(UserDetailBase):
    """Schema for user detail responses"""
    id: int

    model_config = ConfigDict(from_attributes=True)
