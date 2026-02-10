from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PermissionCreate(BaseModel):
    """Schema for creating a permission."""
    name: str
    description: Optional[str] = None


class PermissionUpdate(BaseModel):
    """Schema for updating a permission."""
    name: Optional[str] = None
    description: Optional[str] = None


class PermissionResponse(BaseModel):
    """Schema for permission response."""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionWithRoles(BaseModel):
    """Schema for permission with roles."""
    id: int
    name: str
    description: Optional[str]
    roles: List[int]  # Role IDs

    class Config:
        from_attributes = True
