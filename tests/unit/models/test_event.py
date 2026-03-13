import pytest
from models.event import Event, EventStatus
from datetime import date, time


def test_event_status_enum_values():
    """Test EventStatus enum has correct values"""
    assert EventStatus.PENDING == "PENDING"
    assert EventStatus.CONFIRMED == "CONFIRMED"
    assert EventStatus.CANCELLED == "CANCELLED"
    assert EventStatus.COMPLETED == "COMPLETED"


def test_event_creation_with_default_status():
    """Test creating an Event instance with default status (PENDING)"""
    event = Event(
        name="Rock Concert",
        place="Madison Square Garden",
        description="An amazing rock concert",
        date=date(2026, 3, 15),
        time=time(20, 0),
        created_by="John Doe",
        reference_phone="+1234567890"
    )
    assert event.name == "Rock Concert"
    assert event.place == "Madison Square Garden"
    assert event.description == "An amazing rock concert"
    assert event.date == date(2026, 3, 15)
    assert event.time == time(20, 0)
    assert event.created_by == "John Doe"
    assert event.reference_phone == "+1234567890"
    assert event.status == EventStatus.PENDING
    assert event.id is None  # ID is assigned by DB


def test_event_creation_with_explicit_status():
    """Test creating an Event instance with explicit status"""
    event = Event(
        name="Rock Concert",
        place="Madison Square Garden",
        description="An amazing rock concert",
        date=date(2026, 3, 15),
        time=time(20, 0),
        created_by="John Doe",
        reference_phone="+1234567890",
        status=EventStatus.CONFIRMED
    )
    assert event.status == EventStatus.CONFIRMED


def test_event_repr():
    """Test the __repr__ method of Event"""
    event = Event(
        name="Jazz Night",
        place="Blue Note",
        description="Smooth jazz evening",
        date=date(2026, 4, 20),
        time=time(21, 30),
        created_by="Jane Smith",
        reference_phone="+0987654321"
    )
    repr_str = repr(event)
    assert repr_str == "<Event(name=Jazz Night, place=Blue Note)>"


def test_event_optional_description():
    """Test Event with optional description as None"""
    event = Event(
        name="Simple Event",
        place="Local Club",
        description=None,
        date=date(2026, 5, 1),
        time=time(19, 0),
        created_by="Bob Wilson",
        reference_phone="+1122334455"
    )
    assert event.name == "Simple Event"
    assert event.description is None


def test_event_table_name():
    """Test that the table name is correctly set"""
    assert Event.__tablename__ == "events"


def test_event_status_can_be_changed():
    """Test that event status can be modified"""
    event = Event(
        name="Rock Concert",
        place="Madison Square Garden",
        description="An amazing rock concert",
        date=date(2026, 3, 15),
        time=time(20, 0),
        created_by="John Doe",
        reference_phone="+1234567890"
    )
    assert event.status == EventStatus.PENDING
    
    event.status = EventStatus.CONFIRMED
    assert event.status == EventStatus.CONFIRMED
    
    event.status = EventStatus.COMPLETED
    assert event.status == EventStatus.COMPLETED
    
    event.status = EventStatus.CANCELLED
    assert event.status == EventStatus.CANCELLED
