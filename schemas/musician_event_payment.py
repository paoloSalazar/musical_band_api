"""
Pydantic schemas for MusicianEventPayment API operations.

Provides request/response validation for musician event payment endpoints.
"""
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from schemas.event_payment import PaymentType


class MusicianEventPaymentBase(BaseModel):
    """Base schema for MusicianEventPayment with common fields"""
    event_id: int
    musician_id: int
    amount: Decimal
    payment_type: PaymentType
    payment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None

    @field_validator('payment_date', mode='before')
    @classmethod
    def normalize_to_utc(cls, v: datetime | str) -> datetime:
        """Ensure payment_date is always timezone-aware in UTC."""
        if isinstance(v, str):
            # Handle ISO strings with or without timezone (e.g. '2026-05-23T02:37:00' or with Z/+00:00)
            v = datetime.fromisoformat(v.replace('Z', '+00:00'))
        if isinstance(v, datetime):
            if v.tzinfo is None:
                # Naive datetime: assume it was intended as UTC (common for APIs)
                v = v.replace(tzinfo=timezone.utc)
            else:
                # Convert any timezone to UTC
                v = v.astimezone(timezone.utc)
        return v


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


class MusicianEventSummaryResponse(BaseModel):
    """Schema for musician event payment summary response"""
    musician_name: str
    salary: Decimal
    payment_done: Decimal
    remaining_payment: Decimal

    model_config = ConfigDict(from_attributes=True)


class EventBillingSummaryResponse(BaseModel):
    """Schema for event billing summary response"""
    event_name: str
    payment_done: Decimal
    remaining_payment: Decimal
    payment_done_to_musicians: Decimal

    model_config = ConfigDict(from_attributes=True)