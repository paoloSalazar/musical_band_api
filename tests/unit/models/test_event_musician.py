import pytest
from models.event_musician import EventMusician, PaymentStatus
from decimal import Decimal


def test_payment_status_enum_values():
    """Test PaymentStatus enum has correct values"""
    assert PaymentStatus.PENDING == "PENDING"
    assert PaymentStatus.COMPLETED == "COMPLETED"


def test_event_musician_creation():
    """Test creating an EventMusician instance"""
    musician = EventMusician(
        event_id=1,
        musician_id=2,
        role="Guitarist",
        payment_status=PaymentStatus.PENDING,
        salary=Decimal("500.00")
    )
    assert musician.event_id == 1
    assert musician.musician_id == 2
    assert musician.role == "Guitarist"
    assert musician.payment_status == PaymentStatus.PENDING
    assert musician.salary == Decimal("500.00")
    assert musician.id is None  # ID is assigned by DB


def test_event_musician_default_payment_status():
    """Test default payment status"""
    musician = EventMusician(
        event_id=1,
        musician_id=2,
        salary=Decimal("300.00")
    )
    assert musician.payment_status == PaymentStatus.PENDING


def test_event_musician_optional_role():
    """Test role can be None"""
    musician = EventMusician(
        event_id=1,
        musician_id=2,
        salary=Decimal("400.00")
    )
    assert musician.role is None


def test_event_musician_table_name():
    """Test that the table name is correctly set"""
    assert EventMusician.__tablename__ == "event_musicians"


def test_event_musician_repr():
    """Test the __repr__ method of EventMusician"""
    musician = EventMusician(
        event_id=1,
        musician_id=2,
        salary=Decimal("250.00")
    )
    repr_str = repr(musician)
    assert "EventMusician" in repr_str
    assert "event_id=1" in repr_str
    assert "musician_id=2" in repr_str
    assert "salary=250.00" in repr_str


def test_event_musician_payment_status_can_be_changed():
    """Test that payment status can be modified"""
    musician = EventMusician(
        event_id=1,
        musician_id=2,
        salary=Decimal("500.00")
    )
    assert musician.payment_status == PaymentStatus.PENDING

    musician.payment_status = PaymentStatus.COMPLETED
    assert musician.payment_status == PaymentStatus.COMPLETED