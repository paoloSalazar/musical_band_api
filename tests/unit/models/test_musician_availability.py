import pytest
from models.musician_availability import MusicianAvailability
from datetime import date

def test_musician_availability_creation():
    availability = MusicianAvailability(
        musician_id=1,
        unavailable_date=date(2026, 12, 25),
        reason="Holiday"
    )
    assert availability.musician_id == 1
    assert availability.unavailable_date == date(2026, 12, 25)
    assert availability.reason == "Holiday"
    assert availability.id is None  # ID assigned by DB

def test_musician_availability_date_validation():
    # Test that unavailable_date cannot be in the past
    past_date = date(2020, 1, 1)
    with pytest.raises(ValueError):
        MusicianAvailability(
            musician_id=1,
            unavailable_date=past_date
        )

def test_musician_availability_relationship():
    # Test relationship with User (musician)
    # This would require setting up a mock or actual user in tests
    # For now, just check the attribute exists
    availability = MusicianAvailability(musician_id=1, unavailable_date=date(2026, 12, 25))
    assert hasattr(availability, 'musician_id')