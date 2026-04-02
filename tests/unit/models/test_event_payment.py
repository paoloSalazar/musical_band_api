"""
Unit tests for EventPayment model.

These tests follow TDD approach - they define expected behavior before the model exists.
Tests should FAIL until the EventPayment model is implemented.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from models.event_payment import EventPayment, PaymentType
from sqlalchemy import inspect


def test_payment_type_enum_values():
    """Test PaymentType enum has correct values"""
    assert PaymentType.ADVANCE == "ADVANCE"
    assert PaymentType.REMAINING == "REMAINING"
    assert PaymentType.TOTAL == "TOTAL"


def test_event_payment_creation():
    """Test creating an EventPayment instance"""
    payment = EventPayment(
        event_id=1,
        user_id=1,
        amount=Decimal("1000.00"),
        payment_type=PaymentType.ADVANCE,
        notes="Initial down payment"
    )
    assert payment.event_id == 1
    assert payment.user_id == 1
    assert payment.amount == Decimal("1000.00")
    assert payment.payment_type == PaymentType.ADVANCE
    assert payment.notes == "Initial down payment"
    assert payment.id is None  # ID is assigned by DB


def test_event_payment_table_name():
    """Test that the table name is correctly set"""
    assert EventPayment.__tablename__ == "event_payments"


def test_event_payment_has_required_columns():
    """Test that EventPayment model has all required columns"""
    mapper = inspect(EventPayment)
    columns = {col.key for col in mapper.columns}
    
    required_columns = {'id', 'event_id', 'user_id', 'amount', 'payment_type', 'payment_date', 'created_at'}
    for col in required_columns:
        assert col in columns, f"EventPayment should have '{col}' column"


def test_event_payment_foreign_keys():
    """Test that foreign keys are properly defined"""
    mapper = inspect(EventPayment)
    columns = {col.key: col for col in mapper.columns}
    
    # Check foreign keys exist
    assert 'event_id' in columns
    assert 'user_id' in columns
    
    # Check they are foreign keys
    assert columns['event_id'].foreign_keys
    assert columns['user_id'].foreign_keys


def test_event_payment_amount_numeric():
    """Test that amount is stored as numeric/decimal"""
    payment = EventPayment(
        event_id=1,
        user_id=1,
        amount=Decimal("2500.50"),
        payment_type=PaymentType.TOTAL
    )
    assert isinstance(payment.amount, Decimal)


def test_event_payment_optional_notes():
    """Test that notes is optional"""
    payment = EventPayment(
        event_id=1,
        user_id=1,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE
    )
    assert payment.notes is None


def test_event_payment_repr():
    """Test the __repr__ method of EventPayment"""
    payment = EventPayment(
        event_id=1,
        user_id=1,
        amount=Decimal("1500.00"),
        payment_type=PaymentType.ADVANCE
    )
    repr_str = repr(payment)
    assert "EventPayment" in repr_str
    assert "1500" in repr_str


def test_payment_type_can_be_changed():
    """Test that payment_type can be changed"""
    payment = EventPayment(
        event_id=1,
        user_id=1,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE
    )
    assert payment.payment_type == PaymentType.ADVANCE
    
    payment.payment_type = PaymentType.REMAINING
    assert payment.payment_type == PaymentType.REMAINING
    
    payment.payment_type = PaymentType.TOTAL
    assert payment.payment_type == PaymentType.TOTAL