"""
Unit tests for EventPayment schemas.

These tests follow TDD approach - they define expected schema behavior before implementation.
Tests should FAIL until schemas/event_payment.py is created.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError
from schemas.event_payment import EventPaymentBase, EventPaymentCreate, EventPaymentResponse, PaymentType


class TestPaymentTypeEnum:
    """Tests for PaymentType enum in schemas"""
    
    def test_payment_type_advance(self):
        """Test PaymentType.ADVANCE value"""
        assert PaymentType.ADVANCE == "ADVANCE"
    
    def test_payment_type_remaining(self):
        """Test PaymentType.REMAINING value"""
        assert PaymentType.REMAINING == "REMAINING"
    
    def test_payment_type_total(self):
        """Test PaymentType.TOTAL value"""
        assert PaymentType.TOTAL == "TOTAL"


class TestEventPaymentBase:
    """Tests for EventPaymentBase schema"""
    
    def test_base_schema_fields(self):
        """Test EventPaymentBase has required fields"""
        payment = EventPaymentBase(
            event_id=1,
            user_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE
        )
        assert payment.event_id == 1
        assert payment.user_id == 1
        assert payment.amount == Decimal("1000.00")
        assert payment.payment_type == PaymentType.ADVANCE
    
    def test_base_schema_optional_notes(self):
        """Test EventPaymentBase notes is optional"""
        payment = EventPaymentBase(
            event_id=1,
            user_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.TOTAL
        )
        assert payment.notes is None
    
    def test_base_schema_with_notes(self):
        """Test EventPaymentBase with notes provided"""
        payment = EventPaymentBase(
            event_id=1,
            user_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE,
            notes="Down payment"
        )
        assert payment.notes == "Down payment"


class TestEventPaymentCreate:
    """Tests for EventPaymentCreate schema"""
    
    def test_create_schema_fields(self):
        """Test EventPaymentCreate has all fields"""
        payment = EventPaymentCreate(
            event_id=1,
            user_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE
        )
        assert payment.event_id == 1
        assert payment.user_id == 1
        assert payment.amount == Decimal("1000.00")
        assert payment.payment_type == PaymentType.ADVANCE
    
    def test_create_schema_user_id_required(self):
        """Test EventPaymentCreate user_id is required"""
        with pytest.raises(ValidationError):
            EventPaymentCreate(
                event_id=1,
                amount=Decimal("1000.00"),
                payment_type=PaymentType.ADVANCE
            )


class TestEventPaymentResponse:
    """Tests for EventPaymentResponse schema"""
    
    def test_response_schema_has_id(self):
        """Test EventPaymentResponse includes id field"""
        payment = EventPaymentResponse(
            id=1,
            event_id=1,
            user_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE,
            created_at=datetime.now(),
            payment_date=datetime.now()
        )
        assert payment.id == 1
    
    def test_response_schema_has_timestamps(self):
        """Test EventPaymentResponse includes timestamps"""
        now = datetime.now()
        payment = EventPaymentResponse(
            id=1,
            event_id=1,
            user_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE,
            created_at=now,
            payment_date=now
        )
        assert payment.created_at is not None
        assert payment.payment_date is not None