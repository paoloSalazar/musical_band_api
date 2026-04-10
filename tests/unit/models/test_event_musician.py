import pytest
from models.event_musician import EventMusician
from decimal import Decimal

def test_event_musician_creation():
    musician = EventMusician(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status="PENDING"
    )
    assert musician.event_id == 1
    assert musician.musician_id == 2
    assert musician.role == "Lead Guitarist"
    assert musician.salary == Decimal("1500.00")
    assert musician.payment_status == "PENDING"
    assert musician.id is None  # ID assigned by DB

def test_event_musician_salary_validation():
    # Test that salary must be positive
    with pytest.raises(ValueError):
        EventMusician(
            event_id=1,
            musician_id=2,
            salary=Decimal("0.00")
        )
    
    with pytest.raises(ValueError):
        EventMusician(
            event_id=1,
            musician_id=2,
            salary=Decimal("-100.00")
        )

def test_event_musician_payment_status_enum():
    # Test valid payment statuses
    musician = EventMusician(event_id=1, musician_id=2, salary=Decimal("1000.00"), payment_status="PENDING")
    assert musician.payment_status == "PENDING"
    
    musician = EventMusician(event_id=1, musician_id=2, salary=Decimal("1000.00"), payment_status="COMPLETED")
    assert musician.payment_status == "COMPLETED"
    
    musician = EventMusician(event_id=1, musician_id=2, salary=Decimal("1000.00"), payment_status="PARTIAL")
    assert musician.payment_status == "PARTIAL"

def test_event_musician_relationships():
    # Test relationship attributes exist
    musician = EventMusician(event_id=1, musician_id=2, salary=Decimal("1000.00"))
    assert hasattr(musician, 'event')
    assert hasattr(musician, 'musician')