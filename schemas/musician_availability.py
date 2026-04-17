from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional


class MusicianAvailabilityBase(BaseModel):
    musician_id: int
    unavailable_date: date
    reason: Optional[str] = None


class MusicianAvailabilityCreate(MusicianAvailabilityBase):
    """Schema for creating musician availability"""


class MusicianAvailabilityUpdate(BaseModel):
    """Schema for updating musician availability (all fields optional for PATCH)"""
    unavailable_date: Optional[date] = None
    reason: Optional[str] = None


class MusicianAvailabilityResponse(MusicianAvailabilityBase):
    """Schema for musician availability responses"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MusicianAvailabilitySummaryResponse(BaseModel):
    """Schema for availability summary queries"""
    musician_id: int
    musician_name: str
    unavailable_dates: list[date]
    total_unavailable_days: int

    model_config = ConfigDict(from_attributes=True)