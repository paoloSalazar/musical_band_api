from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional


class EventCreator(BaseModel):
    """Schema for event creator user info (embedded in event response)"""
    user_id: int
    name: str
    lastname: str
    email: str
    phone_number: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


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
    """Schema for event responses (includes id, status, created_by)"""
    id: int
    status: EventStatusEnum
    created_by: EventCreator | None = None
    # Note: created_at and updated_at are excluded as they are for database tracking only

    model_config = ConfigDict(from_attributes=True)


class EventUpdate(BaseModel):
    """Schema for updating an event (all fields optional for PATCH)"""
    name: str | None = None
    place: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    is_all_day: bool | None = None


class EventFilter(BaseModel):
    """Schema for filtering events in list/table view"""
    status: Optional[EventStatusEnum] = None
    search: Optional[str] = None
    user_id: Optional[int] = None
    start_after: Optional[datetime] = None
    end_before: Optional[datetime] = None
    sort_by: Optional[str] = "created_at"
    order: Optional[str] = "desc"


class PaginatedEventResponse(BaseModel):
    """Schema for paginated event response"""
    items: list[EventResponse]
    total: int
    page: int
    limit: int
    total_pages: int
