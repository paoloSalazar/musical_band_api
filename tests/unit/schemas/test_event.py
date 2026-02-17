import pytest
from schemas.event import EventBase, EventCreate, EventResponse, EventUpdate
from datetime import date as date_type
from datetime import time as time_type


def test_event_base_creation():
    """Test creating an EventBase instance"""
    event = EventBase(
        name="Rock Concert",
        place="Madison Square Garden",
        description="An amazing rock concert",
        date=date_type(2026, 3, 15),
        time=time_type(20, 0),
        created_by="John Doe",
        reference_phone="+1234567890"
    )
    assert event.name == "Rock Concert"
    assert event.place == "Madison Square Garden"
    assert event.description == "An amazing rock concert"
    assert event.date == date_type(2026, 3, 15)
    assert event.time == time_type(20, 0)
    assert event.created_by == "John Doe"
    assert event.reference_phone == "+1234567890"


def test_event_base_optional_description():
    """Test EventBase with optional description as None"""
    event = EventBase(
        name="Simple Event",
        place="Local Club",
        description=None,
        date=date_type(2026, 5, 1),
        time=time_type(19, 0),
        created_by="Bob Wilson",
        reference_phone="+1122334455"
    )
    assert event.name == "Simple Event"
    assert event.description is None


def test_event_create():
    """Test EventCreate inherits from EventBase"""
    event = EventCreate(
        name="Jazz Night",
        place="Blue Note",
        description="Smooth jazz evening",
        date=date_type(2026, 4, 20),
        time=time_type(21, 30),
        created_by="Jane Smith",
        reference_phone="+0987654321"
    )
    assert event.name == "Jazz Night"
    assert event.place == "Blue Note"
    assert event.description == "Smooth jazz evening"
    assert event.date == date_type(2026, 4, 20)
    assert event.time == time_type(21, 30)
    assert event.created_by == "Jane Smith"
    assert event.reference_phone == "+0987654321"


def test_event_response():
    """Test EventResponse with id"""
    event = EventResponse(
        id=1,
        name="Rock Concert",
        place="Madison Square Garden",
        description="An amazing rock concert",
        date=date_type(2026, 3, 15),
        time=time_type(20, 0),
        created_by="John Doe",
        reference_phone="+1234567890"
    )
    assert event.id == 1
    assert event.name == "Rock Concert"
    assert event.place == "Madison Square Garden"
    assert event.description == "An amazing rock concert"
    assert event.date == date_type(2026, 3, 15)
    assert event.time == time_type(20, 0)
    assert event.created_by == "John Doe"
    assert event.reference_phone == "+1234567890"


def test_event_from_dict():
    """Test creating Event from dictionary"""
    data = {
        "id": 2,
        "name": "Jazz Night",
        "place": "Blue Note",
        "description": "Smooth jazz evening",
        "date": date_type(2026, 4, 20),
        "time": time_type(21, 30),
        "created_by": "Jane Smith",
        "reference_phone": "+0987654321"
    }
    event = EventResponse(**data)
    assert event.id == 2
    assert event.name == "Jazz Night"
    assert event.place == "Blue Note"
    assert event.description == "Smooth jazz evening"
    assert event.date == date_type(2026, 4, 20)
    assert event.time == time_type(21, 30)
    assert event.created_by == "Jane Smith"
    assert event.reference_phone == "+0987654321"


def test_event_to_dict():
    """Test converting Event to dictionary"""
    event = EventResponse(
        id=3,
        name="Pop Festival",
        place="Central Park",
        description="Summer pop festival",
        date=date_type(2026, 6, 15),
        time=time_type(18, 0),
        created_by="Alice Brown",
        reference_phone="+5566778899"
    )
    data = event.model_dump()
    expected = {
        "id": 3,
        "name": "Pop Festival",
        "place": "Central Park",
        "description": "Summer pop festival",
        "date": date_type(2026, 6, 15),
        "time": time_type(18, 0),
        "created_by": "Alice Brown",
        "reference_phone": "+5566778899"
    }
    assert data == expected


def test_event_update_all_fields_optional():
    """Test EventUpdate with all fields optional"""
    event = EventUpdate()
    assert event.name is None
    assert event.place is None
    assert event.description is None
    assert event.date is None
    assert event.time is None
    assert event.reference_phone is None


def test_event_update_partial():
    """Test EventUpdate with partial fields"""
    event = EventUpdate(
        name="Updated Event Name",
        place="New Venue"
    )
    assert event.name == "Updated Event Name"
    assert event.place == "New Venue"
    assert event.description is None
    assert event.date is None
    assert event.time is None
    assert event.reference_phone is None


def test_event_response_config_from_attributes():
    """Test EventResponse has from_attributes config"""
    event = EventResponse(
        id=1,
        name="Test Event",
        place="Test Place",
        description="Test Description",
        date=date_type(2026, 1, 1),
        time=time_type(12, 0),
        created_by="Test User",
        reference_phone="+1111111111"
    )
    # Verify the config is set
    assert event.model_config.get('from_attributes') is True
