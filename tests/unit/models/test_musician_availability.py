import pytest
from models.musician_availability import MusicianAvailability
from datetime import date


def test_musician_availability_creation():
    """Test creating a MusicianAvailability instance"""
    availability = MusicianAvailability(
        musician_id=1,
        unavailable_date=date(2026, 3, 15),
        reason="Vacation"
    )
    assert availability.musician_id == 1
    assert availability.unavailable_date == date(2026, 3, 15)
    assert availability.reason == "Vacation"
    assert availability.id is None  # ID is assigned by DB


def test_musician_availability_optional_reason():
    """Test reason can be None"""
    availability = MusicianAvailability(
        musician_id=1,
        unavailable_date=date(2026, 4, 20)
    )
    assert availability.reason is None


def test_musician_availability_table_name():
    """Test that the table name is correctly set"""
    assert MusicianAvailability.__tablename__ == "musician_availability"


def test_musician_availability_repr():
    """Test the __repr__ method of MusicianAvailability"""
    availability = MusicianAvailability(
        musician_id=1,
        unavailable_date=date(2026, 5, 10)
    )
    repr_str = repr(availability)
    assert "MusicianAvailability" in repr_str
    assert "musician_id=1" in repr_str
    assert "date=2026-05-10" in repr_str