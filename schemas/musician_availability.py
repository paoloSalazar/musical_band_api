from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date
from typing import Optional


class MusicianAvailabilityBase(BaseModel):
    musician_id: int
    unavailable_date: date
    reason: Optional[str] = None


class MusicianAvailabilityCreate(MusicianAvailabilityBase):
    """Schema for creating musician availability"""

    @field_validator('unavailable_date')
    @classmethod
    def validate_unavailable_date(cls, v):
        if v < date.today():
            raise ValueError('Unavailable date cannot be in the past')
        return v


class MusicianAvailabilityUpdate(BaseModel):
    """Schema for updating musician availability (all fields optional for PATCH)"""
    unavailable_date: Optional[date] = None
    reason: Optional[str] = None

    @field_validator('unavailable_date')
    @classmethod
    def validate_unavailable_date(cls, v):
        if v and v < date.today():
            raise ValueError('Unavailable date cannot be in the past')
        return v


class MusicianAvailabilityResponse(MusicianAvailabilityBase):
    """Schema for musician availability responses"""
    id: int
    created_at: date
    updated_at: date

    model_config = ConfigDict(from_attributes=True)


class MusicianAvailabilitySummaryResponse(BaseModel):
    """Schema for availability summary queries"""
    musician_id: int
    musician_name: str
    unavailable_dates: list[date]
    total_unavailable_days: int

    model_config = ConfigDict(from_attributes=True)