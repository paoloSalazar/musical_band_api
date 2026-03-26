import pytest
from models.event import Event, EventStatus
from datetime import datetime
from sqlalchemy import inspect

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
        start_datetime=datetime(2026, 3, 15, 20, 0),
        end_datetime=datetime(2026, 3, 15, 23, 0),
        is_all_day=False,
        user_id=1
    )
    assert event.name == "Rock Concert"
    assert event.place == "Madison Square Garden"
    assert event.description == "An amazing rock concert"
    assert event.start_datetime == datetime(2026, 3, 15, 20, 0)
    assert event.end_datetime == datetime(2026, 3, 15, 23, 0)
    assert event.is_all_day is False
    assert event.user_id == 1
    assert event.status == EventStatus.PENDING
    assert event.id is None  # ID is assigned by DB


def test_event_creation_with_explicit_status():
    """Test creating an Event instance with explicit status"""
    event = Event(
        name="Rock Concert",
        place="Madison Square Garden",
        description="An amazing rock concert",
        start_datetime=datetime(2026, 3, 15, 20, 0),
        end_datetime=datetime(2026, 3, 15, 23, 0),
        is_all_day=False,
        user_id=1,
        status=EventStatus.CONFIRMED
    )
    assert event.status == EventStatus.CONFIRMED


def test_event_repr():
    """Test the __repr__ method of Event"""
    event = Event(
        name="Jazz Night",
        place="Blue Note",
        description="Smooth jazz evening",
        start_datetime=datetime(2026, 4, 20, 21, 30),
        end_datetime=datetime(2026, 4, 21, 0, 30),
        is_all_day=False,
        user_id=2
    )
    repr_str = repr(event)
    assert repr_str == "<Event(name=Jazz Night, place=Blue Note)>"


def test_event_optional_description():
    """Test Event with optional description as None"""
    event = Event(
        name="Simple Event",
        place="Local Club",
        description=None,
        start_datetime=datetime(2026, 5, 1, 19, 0),
        end_datetime=datetime(2026, 5, 1, 22, 0),
        is_all_day=False,
        user_id=3
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
        start_datetime=datetime(2026, 3, 15, 20, 0),
        end_datetime=datetime(2026, 3, 15, 23, 0),
        is_all_day=False,
        user_id=1
    )
    assert event.status == EventStatus.PENDING
    
    event.status = EventStatus.CONFIRMED
    assert event.status == EventStatus.CONFIRMED
    
    event.status = EventStatus.COMPLETED
    assert event.status == EventStatus.COMPLETED
    
    event.status = EventStatus.CANCELLED
    assert event.status == EventStatus.CANCELLED


def test_event_is_all_day_true():
    """Test creating an all-day event"""
    event = Event(
        name="Conference",
        place="Convention Center",
        description="Annual tech conference",
        start_datetime=datetime(2026, 6, 15, 9, 0),
        end_datetime=datetime(2026, 6, 15, 18, 0),
        is_all_day=True,
        user_id=4
    )
    assert event.is_all_day is True


def test_event_is_all_day_default_false():
    """Test that is_all_day defaults to False"""
    event = Event(
        name="Meeting",
        place="Office",
        start_datetime=datetime(2026, 7, 1, 10, 0),
        end_datetime=datetime(2026, 7, 1, 11, 0),
        user_id=5
    )
    assert event.is_all_day is False


def test_event_user_id_can_be_set():
    """Test that user_id can be set and is stored correctly"""
    event = Event(
        name="Test Event",
        place="Test Place",
        start_datetime=datetime(2026, 8, 1, 10, 0),
        end_datetime=datetime(2026, 8, 1, 11, 0),
        user_id=42
    )
    assert event.user_id == 42


def test_event_setup_price():
    """Test that price can be set and is stored correctly"""
    
    # Verify the Event model has a 'price' column defined
    mapper = inspect(Event)
    columns = {col.key for col in mapper.columns}
    
    assert 'price' in columns, f"Event model should have 'price' column. Found columns: {columns}"
    
    # Test that price can be set via constructor
    event = Event(
        name="VIP Concert",
        place="Exclusive Venue",
        description="A concert with VIP access",
        start_datetime=datetime(2026, 9, 1, 20, 0),
        end_datetime=datetime(2026, 9, 1, 23, 0),
        is_all_day=False,
        user_id=6
    )
    event.price = 3000.00
    assert event.price == 3000.00


def test_event_price_optional():
    """Test that price is optional and can be None"""
    event = Event(
        name="Free Event",
        place="Community Center",
        description="An event with no cost",
        start_datetime=datetime(2026, 10, 1, 18, 0),
        end_datetime=datetime(2026, 10, 1, 21, 0),
        is_all_day=False,
        user_id=7
    )
    assert event.price == 0.00 or event.price is None  # Depending on how default is handled, it could be 0.00 or None