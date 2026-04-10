"""
Pydantic schemas for EventMusician API operations.

Provides request/response validation for event musician assignment endpoints.
"""
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class PaymentStatus(str, Enum):
    """Enum for payment status values"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"


class EventMusicianBase(BaseModel):
    """Base schema for EventMusician with common fields"""
    event_id: int
    musician_id: int
    role: Optional[str] = None
    salary: Decimal
    payment_status: PaymentStatus = PaymentStatus.PENDING


class EventMusicianCreate(EventMusicianBase):
    """Schema for creating a new event musician assignment"""

    @field_validator('salary')
    @classmethod
    def validate_salary(cls, v):
        if v <= Decimal("0.00"):
            raise ValueError('Salary must be positive')
        return v


class EventMusicianUpdate(BaseModel):
    """Schema for updating event musician (all fields optional for PATCH)"""
    role: Optional[str] = None
    salary: Optional[Decimal] = None
    payment_status: Optional[PaymentStatus] = None

    @field_validator('salary')
    @classmethod
    def validate_salary(cls, v):
        if v is not None and v <= Decimal("0.00"):
            raise ValueError('Salary must be positive')
        return v


class EventMusicianResponse(EventMusicianBase):
    """Schema for event musician response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MusicianSummaryResponse(BaseModel):
    """Schema for musician summary per event"""
    id: int
    musician_id: int
    musician_name: str
    role: Optional[str] = None
    salary: Decimal
    payment_status: PaymentStatus

    model_config = ConfigDict(from_attributes=True)