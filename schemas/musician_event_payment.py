"""
Pydantic schemas for MusicianEventPayment API operations.

Provides request/response validation for musician event payment endpoints.
"""
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from decimal import Decimal
from schemas.event_payment import PaymentType


class MusicianEventPaymentBase(BaseModel):
    """Base schema for MusicianEventPayment with common fields"""
    event_id: int
    musician_id: int
    amount: Decimal
    payment_type: PaymentType
    payment_date: datetime
    notes: str | None = None


class MusicianEventPaymentCreate(MusicianEventPaymentBase):
    """Schema for creating a new musician payment"""

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= Decimal("0.00"):
            raise ValueError('Amount must be positive')
        return v


class MusicianEventPaymentResponse(MusicianEventPaymentBase):
    """Schema for musician payment response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MusicianPaymentSummaryResponse(BaseModel):
    """Schema for musician payment summary response"""
    musician_id: int
    total_paid: Decimal
    payment_count: int

    model_config = ConfigDict(from_attributes=True)