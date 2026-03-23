from pydantic import BaseModel, ConfigDict, model_validator, model_serializer
from datetime import datetime, time, timedelta, timezone
from enum import Enum
from typing import Optional, Any
import os


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
    
    @model_validator(mode='before')
    @classmethod
    def handle_datetime_inputs(cls, data: Any) -> Any:
        """
        Handle datetime inputs - ensure naive datetimes are treated as local time and converted to UTC.
        
        - For timezone-aware inputs: convert to UTC and strip tzinfo
        - For naive datetime inputs: treat as local time and convert to UTC
        - For all-day events: normalize times to 00:00-23:59:59
        """
        if isinstance(data, dict):
            data = dict(data)
            
            is_all_day = data.get('is_all_day', False)
            start_datetime = data.get('start_datetime')
            end_datetime = data.get('end_datetime')
            
            # Helper function to convert datetime to UTC
            def to_utc(dt: Any) -> Any:
                if dt is None:
                    return None
                if not isinstance(dt, datetime):
                    return dt
                # If timezone-aware, convert to UTC
                if dt.tzinfo is not None:
                    # Use timedelta offset instead of ZoneInfo (no tzdata required)
                    utc_dt = dt.astimezone(datetime.now().astimezone().tzinfo)
                    offset = utc_dt.utcoffset()
                    return (utc_dt - offset).replace(tzinfo=None)
                # If naive, assume local time and convert to UTC using offset
                local_now = datetime.now()
                utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
                offset = local_now - utc_now
                return (dt.replace(tzinfo=local_now.tzinfo) - offset).replace(tzinfo=None)
            
            start_datetime = to_utc(start_datetime)
            end_datetime = to_utc(end_datetime)
            
            # For all-day events, normalize times to 08:00-23:00
            if is_all_day:
                if start_datetime and isinstance(start_datetime, datetime):
                    start_date = start_datetime.date()
                    start_datetime = datetime.combine(start_date, time(8, 0))
                if end_datetime and isinstance(end_datetime, datetime):
                    end_date = end_datetime.date()
                    end_datetime = datetime.combine(end_date, time(23, 0))
                
                # If no datetime provided, use current date with default times
                if data.get('start_datetime') is None or data.get('end_datetime') is None:
                    now = datetime.now()
                    today = now.date()
                    start_datetime = datetime.combine(today, time(8, 0))
                    end_datetime = datetime.combine(today, time(23, 0))
            
            data['start_datetime'] = start_datetime
            data['end_datetime'] = end_datetime
        
        return data


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
    
    @model_validator(mode='before')
    @classmethod
    def handle_datetime_inputs(cls, data: Any) -> Any:
        """
        Handle datetime inputs for updates - ensure naive datetimes are treated as local time and converted to UTC.
        
        - For timezone-aware inputs: convert to UTC and strip tzinfo
        - For naive datetime inputs: treat as local time and convert to UTC
        - For all-day events: normalize times to 00:00-23:59:59
        """
        if isinstance(data, dict):
            data = dict(data)
            
            is_all_day = data.get('is_all_day')
            start_datetime = data.get('start_datetime')
            end_datetime = data.get('end_datetime')
            
            # Only process if datetime fields are provided
            if start_datetime or end_datetime:
                # Helper function to convert datetime to UTC
                def to_utc(dt: Any) -> Any:
                    if dt is None:
                        return None
                    if not isinstance(dt, datetime):
                        return dt
                    # If timezone-aware, convert to UTC
                    if dt.tzinfo is not None:
                        return dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
                    # If naive, assume local time and convert to UTC
                    local_tz = datetime.now().astimezone().tzinfo
                    local_dt = dt.replace(tzinfo=local_tz)
                    return local_dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
                
                start_datetime = to_utc(start_datetime)
                end_datetime = to_utc(end_datetime)
                
                # For all-day events, normalize times to 08:00-23:00
                if is_all_day:
                    if start_datetime and isinstance(start_datetime, datetime):
                        start_date = start_datetime.date()
                        start_datetime = datetime.combine(start_date, time(8, 0))
                    if end_datetime and isinstance(end_datetime, datetime):
                        end_date = end_datetime.date()
                        end_datetime = datetime.combine(end_date, time(23, 0))
                
                data['start_datetime'] = start_datetime
                data['end_datetime'] = end_datetime
        
        return data


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
