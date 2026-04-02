"""
Pydantic schemas for EventPayment API operations.

Provides request/response validation for event payment endpoints.
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentType(str, Enum):
    """Enum for payment type values"""
    ADVANCE = "ADVANCE"
    REMAINING = "REMAINING"
    TOTAL = "TOTAL"


class EventPaymentBase(BaseModel):
    """Base schema for EventPayment with common fields"""
    event_id: int
    user_id: int
    amount: Decimal
    payment_type: PaymentType
    notes: str | None = None


class EventPaymentCreate(BaseModel):
    """Schema for creating a new payment"""
    event_id: int
    user_id: int
    amount: Decimal
    payment_type: PaymentType
    notes: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class EventPaymentResponse(BaseModel):
    """Schema for payment response"""
    id: int
    event_id: int
    user_id: int
    amount: Decimal
    payment_type: PaymentType
    payment_date: datetime
    notes: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EventPaymentSummary(BaseModel):
    """Schema for payment summary response"""
    event_id: int
    total_paid: Decimal
    pending_balance: Decimal
    final_price: Decimal
    is_fully_paid: bool
    
    model_config = ConfigDict(from_attributes=True)