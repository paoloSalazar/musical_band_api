from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum


class EventStatusEnum(str, Enum):
    """Enum for event status values"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class EventBase(BaseModel):
    """Base schema for Event with common fields"""
    name: str
    place: str
    description: str | None = None
    start_datetime: datetime
    end_datetime: datetime
    is_all_day: bool = False
    user_id: int


class EventCreate(EventBase):
    """Schema for creating an event"""
    user_id: int | None = None  # Optional - will be set from current_user in the endpoint


class EventResponse(EventBase):
    """Schema for event responses (includes id, status, timestamps)"""
    id: int
    status: EventStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventUpdate(BaseModel):
    """Schema for updating an event (all fields optional for PATCH)"""
    name: str | None = None
    place: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    is_all_day: bool | None = None
