"""
Unit tests for MusicianEventPayment model.

These tests follow TDD approach - they define expected behavior before the model exists.
Tests should FAIL until the MusicianEventPayment model is implemented.
"""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from models.musician_event_payment import MusicianEventPayment
from models.event_payment import PaymentType
from sqlalchemy import inspect


def test_musician_event_payment_creation():
    """Test creating a MusicianEventPayment instance"""
    payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    payment = MusicianEventPayment(
        event_id=1,
        musician_id=1,
        amount=Decimal("1000.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=payment_date,
        notes="Initial musician payment"
    )
    assert payment.event_id == 1
    assert payment.musician_id == 1
    assert payment.amount == Decimal("1000.00")
    assert payment.payment_type == PaymentType.ADVANCE
    assert payment.payment_date == payment_date
    assert payment.notes == "Initial musician payment"
    assert payment.id is None  # ID is assigned by DB


def test_musician_event_payment_table_name():
    """Test that the table name is correctly set"""
    assert MusicianEventPayment.__tablename__ == "musician_event_payments"


def test_musician_event_payment_has_required_columns():
    """Test that MusicianEventPayment model has all required columns"""
    mapper = inspect(MusicianEventPayment)
    columns = {col.key for col in mapper.columns}

    required_columns = {'id', 'event_id', 'musician_id', 'amount', 'payment_type', 'payment_date', 'notes', 'created_at', 'updated_at'}
    for col in required_columns:
        assert col in columns, f"MusicianEventPayment should have '{col}' column"


def test_musician_event_payment_foreign_keys():
    """Test that foreign keys are properly defined"""
    mapper = inspect(MusicianEventPayment)
    columns = {col.key: col for col in mapper.columns}

    # Check foreign keys exist
    assert 'event_id' in columns
    assert 'musician_id' in columns

    # Check they are foreign keys
    assert columns['event_id'].foreign_keys
    assert columns['musician_id'].foreign_keys


def test_musician_event_payment_amount_numeric():
    """Test that amount is stored as numeric/decimal"""
    payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    payment = MusicianEventPayment(
        event_id=1,
        musician_id=1,
        amount=Decimal("2500.50"),
        payment_type=PaymentType.TOTAL,
        payment_date=payment_date
    )
    assert isinstance(payment.amount, Decimal)


def test_musician_event_payment_optional_notes():
    """Test that notes is optional"""
    payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    payment = MusicianEventPayment(
        event_id=1,
        musician_id=1,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=payment_date
    )
    assert payment.notes is None


def test_musician_event_payment_repr():
    """Test the __repr__ method of MusicianEventPayment"""
    payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    payment = MusicianEventPayment(
        event_id=1,
        musician_id=1,
        amount=Decimal("1500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=payment_date
    )
    repr_str = repr(payment)
    assert "MusicianEventPayment" in repr_str
    assert "1500" in repr_str


def test_payment_type_can_be_changed():
    """Test that payment_type can be changed"""
    payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    payment = MusicianEventPayment(
        event_id=1,
        musician_id=1,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=payment_date
    )
    assert payment.payment_type == PaymentType.ADVANCE

    payment.payment_type = PaymentType.REMAINING
    assert payment.payment_type == PaymentType.REMAINING

    payment.payment_type = PaymentType.TOTAL
    assert payment.payment_type == PaymentType.TOTAL


def test_amount_must_be_positive():
    """Test that amount must be positive"""
    payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="Amount must be positive"):
        MusicianEventPayment(
            event_id=1,
            musician_id=1,
            amount=Decimal("0.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date
        )

    with pytest.raises(ValueError, match="Amount must be positive"):
        MusicianEventPayment(
            event_id=1,
            musician_id=1,
            amount=Decimal("-100.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date
        )


def test_invalid_payment_type():
    """Test that invalid payment_type raises ValueError"""
    payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="Invalid payment type"):
        MusicianEventPayment(
            event_id=1,
            musician_id=1,
            amount=Decimal("500.00"),
            payment_type="INVALID",
            payment_date=payment_date
        )