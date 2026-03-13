from pydantic import BaseModel, ConfigDict
from datetime import date as date_type
from datetime import time as time_type


class EventBase(BaseModel):
    """Base schema for Event with common fields"""
    name: str
    place: str
    description: str | None = None
    date: date_type
    time: time_type
    created_by: str
    reference_phone: str


class EventCreate(EventBase):
    """Schema for creating an event"""
    pass


class EventResponse(EventBase):
    """Schema for event responses (includes id)"""
    id: int

    model_config = ConfigDict(from_attributes=True)


class EventUpdate(BaseModel):
    """Schema for updating an event (all fields optional for PATCH)"""
    name: str | None = None
    place: str | None = None
    description: str | None = None
    date: date_type | None = None
    time: time_type | None = None
    reference_phone: str | None = None
