import pytest
from schemas.event import EventBase, EventCreate, EventResponse, EventUpdate, EventStatusEnum
from datetime import datetime


def test_event_base_creation():
    """Test creating an EventBase instance"""
    event = EventBase(
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


def test_event_base_optional_description():
    """Test EventBase with optional description as None"""
    event = EventBase(
        name="Simple Event",
        place="Local Club",
        description=None,
        start_datetime=datetime(2026, 5, 1, 19, 0),
        end_datetime=datetime(2026, 5, 1, 22, 0),
        is_all_day=False,
        user_id=2
    )
    assert event.name == "Simple Event"
    assert event.description is None


def test_event_base_is_all_day_true():
    """Test EventBase with is_all_day=True"""
    event = EventBase(
        name="All Day Conference",
        place="Convention Center",
        description="Full day event",
        start_datetime=datetime(2026, 6, 15, 9, 0),
        end_datetime=datetime(2026, 6, 15, 18, 0),
        is_all_day=True,
        user_id=3
    )
    assert event.is_all_day is True


def test_event_create():
    """Test EventCreate inherits from EventBase"""
    event = EventCreate(
        name="Jazz Night",
        place="Blue Note",
        description="Smooth jazz evening",
        start_datetime=datetime(2026, 4, 20, 21, 30),
        end_datetime=datetime(2026, 4, 21, 0, 30),
        is_all_day=False,
        user_id=4
    )
    assert event.name == "Jazz Night"
    assert event.place == "Blue Note"
    assert event.description == "Smooth jazz evening"
    assert event.start_datetime == datetime(2026, 4, 20, 21, 30)
    assert event.end_datetime == datetime(2026, 4, 21, 0, 30)
    assert event.is_all_day is False
    assert event.user_id == 4


def test_event_response():
    """Test EventResponse with id"""
    event = EventResponse(
        id=1,
        name="Rock Concert",
        place="Madison Square Garden",
        description="An amazing rock concert",
        start_datetime=datetime(2026, 3, 15, 20, 0),
        end_datetime=datetime(2026, 3, 15, 23, 0),
        is_all_day=False,
        status=EventStatusEnum.PENDING,
        user_id=1,
        created_at=datetime(2026, 1, 1, 10, 0),
        updated_at=datetime(2026, 1, 1, 10, 0)
    )
    assert event.id == 1
    assert event.name == "Rock Concert"
    assert event.place == "Madison Square Garden"
    assert event.description == "An amazing rock concert"
    assert event.start_datetime == datetime(2026, 3, 15, 20, 0)
    assert event.end_datetime == datetime(2026, 3, 15, 23, 0)
    assert event.is_all_day is False
    assert event.status == EventStatusEnum.PENDING
    assert event.user_id == 1


def test_event_response_confirmed_status():
    """Test EventResponse with CONFIRMED status"""
    event = EventResponse(
        id=1,
        name="Confirmed Event",
        place="Venue",
        description="Event description",
        start_datetime=datetime(2026, 3, 15, 20, 0),
        end_datetime=datetime(2026, 3, 15, 23, 0),
        is_all_day=False,
        status=EventStatusEnum.CONFIRMED,
        user_id=1,
        created_at=datetime(2026, 1, 1, 10, 0),
        updated_at=datetime(2026, 1, 1, 10, 0)
    )
    assert event.status == EventStatusEnum.CONFIRMED


def test_event_from_dict():
    """Test creating Event from dictionary"""
    data = {
        "id": 2,
        "name": "Jazz Night",
        "place": "Blue Note",
        "description": "Smooth jazz evening",
        "start_datetime": datetime(2026, 4, 20, 21, 30),
        "end_datetime": datetime(2026, 4, 21, 0, 30),
        "is_all_day": False,
        "status": EventStatusEnum.PENDING,
        "user_id": 5,
        "created_at": datetime(2026, 1, 1, 10, 0),
        "updated_at": datetime(2026, 1, 1, 10, 0)
    }
    event = EventResponse(**data)
    assert event.id == 2
    assert event.name == "Jazz Night"
    assert event.place == "Blue Note"
    assert event.description == "Smooth jazz evening"
    assert event.start_datetime == datetime(2026, 4, 20, 21, 30)
    assert event.end_datetime == datetime(2026, 4, 21, 0, 30)
    assert event.is_all_day is False
    assert event.status == EventStatusEnum.PENDING
    assert event.user_id == 5


def test_event_to_dict():
    """Test converting Event to dictionary"""
    event = EventResponse(
        id=3,
        name="Pop Festival",
        place="Central Park",
        description="Summer pop festival",
        start_datetime=datetime(2026, 6, 15, 18, 0),
        end_datetime=datetime(2026, 6, 15, 23, 0),
        is_all_day=False,
        status=EventStatusEnum.CONFIRMED,
        user_id=6,
        created_by=None
    )
    data = event.model_dump()
    expected = {
        "id": 3,
        "name": "Pop Festival",
        "place": "Central Park",
        "description": "Summer pop festival",
        "start_datetime": datetime(2026, 6, 15, 18, 0),
        "end_datetime": datetime(2026, 6, 15, 23, 0),
        "is_all_day": False,
        "status": EventStatusEnum.CONFIRMED,
        "user_id": 6,
        "created_by": None
    }
    assert data == expected


def test_event_update_all_fields_optional():
    """Test EventUpdate with all fields optional"""
    event = EventUpdate()
    assert event.name is None
    assert event.place is None
    assert event.description is None
    assert event.start_datetime is None
    assert event.end_datetime is None
    assert event.is_all_day is None


def test_event_update_partial():
    """Test EventUpdate with partial fields"""
    event = EventUpdate(
        name="Updated Event Name",
        place="New Venue"
    )
    assert event.name == "Updated Event Name"
    assert event.place == "New Venue"
    assert event.description is None
    assert event.start_datetime is None
    assert event.end_datetime is None
    assert event.is_all_day is None


def test_event_response_config_from_attributes():
    """Test EventResponse has from_attributes config"""
    event = EventResponse(
        id=1,
        name="Test Event",
        place="Test Place",
        description="Test Description",
        start_datetime=datetime(2026, 1, 1, 12, 0),
        end_datetime=datetime(2026, 1, 1, 14, 0),
        is_all_day=False,
        status=EventStatusEnum.PENDING,
        user_id=1,
        created_at=datetime(2026, 1, 1, 10, 0),
        updated_at=datetime(2026, 1, 1, 10, 0)
    )
    # Verify the config is set
    assert event.model_config.get('from_attributes') is True
