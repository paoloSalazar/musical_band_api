import pytest
from datetime import datetime
from decimal import Decimal
from schemas.event_musician import (
    EventMusicianCreate,
    EventMusicianUpdate,
    EventMusicianResponse,
    MusicianSummaryResponse,
    PaymentStatus,
)


def test_event_musician_create_valid():
    """Test creating EventMusicianCreate with valid data"""
    schema = EventMusicianCreate(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status=PaymentStatus.PENDING
    )
    assert schema.event_id == 1
    assert schema.musician_id == 2
    assert schema.role == "Lead Guitarist"
    assert schema.salary == Decimal("1500.00")
    assert schema.payment_status == PaymentStatus.PENDING


def test_event_musician_create_minimal():
    """Test creating EventMusicianCreate with minimal required fields"""
    schema = EventMusicianCreate(
        event_id=1,
        musician_id=2,
        salary=Decimal("1000.00")
    )
    assert schema.event_id == 1
    assert schema.musician_id == 2
    assert schema.role is None
    assert schema.salary == Decimal("1000.00")
    assert schema.payment_status == PaymentStatus.PENDING


def test_event_musician_create_zero_salary():
    """Test that EventMusicianCreate raises error for zero salary"""
    with pytest.raises(ValueError, match="Salary must be positive"):
        EventMusicianCreate(
            event_id=1,
            musician_id=2,
            salary=Decimal("0.00")
        )


def test_event_musician_create_negative_salary():
    """Test that EventMusicianCreate raises error for negative salary"""
    with pytest.raises(ValueError, match="Salary must be positive"):
        EventMusicianCreate(
            event_id=1,
            musician_id=2,
            salary=Decimal("-100.00")
        )


def test_event_musician_update_empty():
    """Test EventMusicianUpdate with no fields"""
    schema = EventMusicianUpdate()
    assert schema.role is None
    assert schema.salary is None
    assert schema.payment_status is None


def test_event_musician_update_partial():
    """Test EventMusicianUpdate with partial fields"""
    schema = EventMusicianUpdate(role="Updated role", payment_status=PaymentStatus.COMPLETED)
    assert schema.role == "Updated role"
    assert schema.salary is None
    assert schema.payment_status == PaymentStatus.COMPLETED


def test_event_musician_update_valid_salary():
    """Test EventMusicianUpdate with valid positive salary"""
    schema = EventMusicianUpdate(salary=Decimal("2000.00"))
    assert schema.salary == Decimal("2000.00")


def test_event_musician_update_zero_salary():
    """Test that EventMusicianUpdate raises error for zero salary"""
    with pytest.raises(ValueError, match="Salary must be positive"):
        EventMusicianUpdate(salary=Decimal("0.00"))


def test_event_musician_update_negative_salary():
    """Test that EventMusicianUpdate raises error for negative salary"""
    with pytest.raises(ValueError, match="Salary must be positive"):
        EventMusicianUpdate(salary=Decimal("-50.00"))


def test_event_musician_response():
    """Test EventMusicianResponse schema"""
    now = datetime.now()
    schema = EventMusicianResponse(
        id=1,
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status=PaymentStatus.PENDING,
        musician_name="John",
        musician_lastname="Doe",
        created_at=now,
        updated_at=now
    )
    assert schema.id == 1
    assert schema.event_id == 1
    assert schema.musician_id == 2
    assert schema.role == "Lead Guitarist"
    assert schema.salary == Decimal("1500.00")
    assert schema.payment_status == PaymentStatus.PENDING
    assert schema.created_at == now
    assert schema.updated_at == now


def test_event_musician_response_from_attributes():
    """Test EventMusicianResponse from model attributes"""
    now = datetime.now()
    
    class MockEventMusician:
        id = 1
        event_id = 1
        musician_id = 2
        role = "Drummer"
        salary = Decimal("1200.00")
        payment_status = "PENDING"
        created_at = now
        updated_at = now
    
    schema = EventMusicianResponse.model_validate(MockEventMusician())
    assert schema.id == 1
    assert schema.event_id == 1
    assert schema.musician_id == 2
    assert schema.role == "Drummer"
    assert schema.salary == Decimal("1200.00")
    assert schema.payment_status == PaymentStatus.PENDING


def test_musician_summary_response():
    """Test MusicianSummaryResponse schema"""
    schema = MusicianSummaryResponse(
        id=1,
        musician_id=2,
        musician_name="Jane Smith",
        role="Bassist",
        salary=Decimal("1300.00"),
        payment_status=PaymentStatus.COMPLETED
    )
    assert schema.id == 1
    assert schema.musician_id == 2
    assert schema.musician_name == "Jane Smith"
    assert schema.role == "Bassist"
    assert schema.salary == Decimal("1300.00")
    assert schema.payment_status == PaymentStatus.COMPLETED


def test_event_musician_create_to_dict():
    """Test converting EventMusicianCreate to dictionary"""
    schema = EventMusicianCreate(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status=PaymentStatus.PENDING
    )
    data = schema.model_dump()
    assert data == {
        "event_id": 1,
        "musician_id": 2,
        "role": "Lead Guitarist",
        "salary": Decimal("1500.00"),
        "payment_status": PaymentStatus.PENDING
    }


def test_event_musician_response_to_dict():
    """Test converting EventMusicianResponse to dictionary"""
    now = datetime.now()
    schema = EventMusicianResponse(
        id=1,
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status=PaymentStatus.PENDING,
        musician_name="John",
        musician_lastname="Doe",
        created_at=now,
        updated_at=now
    )
    data = schema.model_dump()
    expected = {
        "id": 1,
        "event_id": 1,
        "musician_id": 2,
        "role": "Lead Guitarist",
        "salary": Decimal("1500.00"),
        "payment_status": PaymentStatus.PENDING,
        "musician_name": "John",
        "musician_lastname": "Doe",
        "created_at": now,
        "updated_at": now
    }
    assert data == expected