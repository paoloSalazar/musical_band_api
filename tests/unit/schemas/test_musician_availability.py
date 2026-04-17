import pytest
from datetime import date, datetime, timedelta
from schemas.musician_availability import (
    MusicianAvailabilityCreate,
    MusicianAvailabilityUpdate,
    MusicianAvailabilityResponse,
    MusicianAvailabilitySummaryResponse,
)


def test_musician_availability_create_valid():
    """Test creating MusicianAvailabilityCreate with valid future date"""
    future_date = date.today() + timedelta(days=1)
    schema = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=future_date,
        reason="Holiday"
    )
    assert schema.musician_id == 1
    assert schema.unavailable_date == future_date
    assert schema.reason == "Holiday"


def test_musician_availability_create_today():
    """Test creating MusicianAvailabilityCreate with today's date (should be valid)"""
    today = date.today()
    schema = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=today
    )
    assert schema.unavailable_date == today


def test_musician_availability_create_past_date():
    """Test that MusicianAvailabilityCreate accepts past date (validation moved to service layer)"""
    past_date = date.today() - timedelta(days=1)
    schema = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=past_date
    )
    assert schema.unavailable_date == past_date


def test_musician_availability_create_no_reason():
    """Test creating MusicianAvailabilityCreate without reason"""
    future_date = date.today() + timedelta(days=1)
    schema = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=future_date
    )
    assert schema.reason is None


def test_musician_availability_update_empty():
    """Test MusicianAvailabilityUpdate with no fields"""
    schema = MusicianAvailabilityUpdate()
    assert schema.unavailable_date is None
    assert schema.reason is None


def test_musician_availability_update_partial():
    """Test MusicianAvailabilityUpdate with partial fields"""
    schema = MusicianAvailabilityUpdate(reason="Updated reason")
    assert schema.reason == "Updated reason"
    assert schema.unavailable_date is None


def test_musician_availability_update_valid_date():
    """Test MusicianAvailabilityUpdate with valid future date"""
    future_date = date.today() + timedelta(days=1)
    schema = MusicianAvailabilityUpdate(unavailable_date=future_date)
    assert schema.unavailable_date == future_date


def test_musician_availability_update_past_date():
    """Test that MusicianAvailabilityUpdate accepts past date (validation moved to service layer)"""
    past_date = date.today() - timedelta(days=1)
    schema = MusicianAvailabilityUpdate(unavailable_date=past_date)
    assert schema.unavailable_date == past_date


def test_musician_availability_response():
    """Test MusicianAvailabilityResponse schema"""
    today = date.today()
    now = datetime.combine(today, datetime.min.time())
    schema = MusicianAvailabilityResponse(
        id=1,
        musician_id=1,
        unavailable_date=today,
        reason="Holiday",
        created_at=now,
        updated_at=now
    )
    assert schema.id == 1
    assert schema.musician_id == 1
    assert schema.unavailable_date == today
    assert schema.reason == "Holiday"
    assert schema.created_at == now
    assert schema.updated_at == now


def test_musician_availability_response_from_attributes():
    """Test MusicianAvailabilityResponse from model attributes"""
    today = date.today()
    
    class MockMusicianAvailability:
        id = 1
        musician_id = 1
        unavailable_date = today
        reason = "Sick"
        created_at = today
        updated_at = today
    
    schema = MusicianAvailabilityResponse.model_validate(MockMusicianAvailability())
    assert schema.id == 1
    assert schema.musician_id == 1
    assert schema.unavailable_date == today
    assert schema.reason == "Sick"


def test_musician_availability_summary_response():
    """Test MusicianAvailabilitySummaryResponse schema"""
    dates = [date.today() + timedelta(days=i) for i in range(3)]
    schema = MusicianAvailabilitySummaryResponse(
        musician_id=1,
        musician_name="John Doe",
        unavailable_dates=dates,
        total_unavailable_days=3
    )
    assert schema.musician_id == 1
    assert schema.musician_name == "John Doe"
    assert schema.unavailable_dates == dates
    assert schema.total_unavailable_days == 3


def test_musician_availability_create_to_dict():
    """Test converting MusicianAvailabilityCreate to dictionary"""
    future_date = date.today() + timedelta(days=1)
    schema = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=future_date,
        reason="Holiday"
    )
    data = schema.model_dump()
    assert data == {
        "musician_id": 1,
        "unavailable_date": future_date,
        "reason": "Holiday"
    }


def test_musician_availability_response_to_dict():
    """Test converting MusicianAvailabilityResponse to dictionary"""
    today = date.today()
    now = datetime.combine(today, datetime.min.time())
    schema = MusicianAvailabilityResponse(
        id=1,
        musician_id=1,
        unavailable_date=today,
        reason="Holiday",
        created_at=now,
        updated_at=now
    )
    data = schema.model_dump()
    assert data == {
        "id": 1,
        "musician_id": 1,
        "unavailable_date": today,
        "reason": "Holiday",
        "created_at": now,
        "updated_at": now
    }