import pytest
from models.musician_event_payment import MusicianEventPayment
from decimal import Decimal
from datetime import datetime


def test_musician_event_payment_creation():
    """Test creating a MusicianEventPayment instance"""
    payment = MusicianEventPayment(
        event_id=1,
        user_id=2,
        payment_date=datetime(2026, 3, 15, 10, 0),
        amount=Decimal("250.00"),
        payment_type="ADVANCE"
    )
    assert payment.event_id == 1
    assert payment.user_id == 2
    assert payment.payment_date == datetime(2026, 3, 15, 10, 0)
    assert payment.amount == Decimal("250.00")
    assert payment.payment_type == "ADVANCE"
    assert payment.id is None  # ID is assigned by DB


def test_musician_event_payment_table_name():
    """Test that the table name is correctly set"""
    assert MusicianEventPayment.__tablename__ == "musician_event_payments"


def test_musician_event_payment_repr():
    """Test the __repr__ method of MusicianEventPayment"""
    payment = MusicianEventPayment(
        event_id=1,
        user_id=2,
        amount=Decimal("150.00")
    )
    repr_str = repr(payment)
    assert "MusicianEventPayment" in repr_str
    assert "event_id=1" in repr_str
    assert "user_id=2" in repr_str
    assert "amount=150.00" in repr_str