"""
Unit tests for MusicianEventPayment schemas.

These tests follow TDD approach - they define expected schema behavior before implementation.
Tests should FAIL until schemas/musician_event_payment.py is created.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from pydantic import ValidationError
from schemas.musician_event_payment import (
    MusicianEventPaymentBase,
    MusicianEventPaymentCreate,
    MusicianEventPaymentResponse,
    MusicianPaymentSummaryResponse
)
from schemas.event_payment import PaymentType


class TestMusicianEventPaymentBase:
    """Tests for MusicianEventPaymentBase schema"""

    def test_base_schema_fields(self):
        """Test MusicianEventPaymentBase has required fields"""
        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        payment = MusicianEventPaymentBase(
            event_id=1,
            musician_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date
        )
        assert payment.event_id == 1
        assert payment.musician_id == 1
        assert payment.amount == Decimal("1000.00")
        assert payment.payment_type == PaymentType.ADVANCE
        assert payment.payment_date == payment_date

    def test_base_schema_payment_date_defaults_to_now(self):
        """Test MusicianEventPaymentBase payment_date defaults to current time"""
        payment = MusicianEventPaymentBase(
            event_id=1,
            musician_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE
        )
        assert payment.payment_date is not None
        assert isinstance(payment.payment_date, datetime)

    def test_base_schema_optional_notes(self):
        """Test MusicianEventPaymentBase notes is optional"""
        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        payment = MusicianEventPaymentBase(
            event_id=1,
            musician_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.TOTAL,
            payment_date=payment_date
        )
        assert payment.notes is None

    def test_base_schema_with_notes(self):
        """Test MusicianEventPaymentBase with notes provided"""
        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        payment = MusicianEventPaymentBase(
            event_id=1,
            musician_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date,
            notes="Musician advance payment"
        )
        assert payment.notes == "Musician advance payment"


class TestMusicianEventPaymentCreate:
    """Tests for MusicianEventPaymentCreate schema"""

    def test_create_schema_fields(self):
        """Test MusicianEventPaymentCreate has all fields"""
        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        payment = MusicianEventPaymentCreate(
            event_id=1,
            musician_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date
        )
        assert payment.event_id == 1
        assert payment.musician_id == 1
        assert payment.amount == Decimal("1000.00")
        assert payment.payment_type == PaymentType.ADVANCE
        assert payment.payment_date == payment_date

    def test_create_schema_musician_id_required(self):
        """Test MusicianEventPaymentCreate musician_id is required"""
        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValidationError):
            MusicianEventPaymentCreate(
                event_id=1,
                amount=Decimal("1000.00"),
                payment_type=PaymentType.ADVANCE,
                payment_date=payment_date
            )

    def test_create_schema_amount_positive(self):
        """Test MusicianEventPaymentCreate amount must be positive"""
        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValidationError, match="Amount must be positive"):
            MusicianEventPaymentCreate(
                event_id=1,
                musician_id=1,
                amount=Decimal("0.00"),
                payment_type=PaymentType.ADVANCE,
                payment_date=payment_date
            )

    def test_create_schema_amount_negative(self):
        """Test MusicianEventPaymentCreate amount must be positive (negative)"""
        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValidationError, match="Amount must be positive"):
            MusicianEventPaymentCreate(
                event_id=1,
                musician_id=1,
                amount=Decimal("-100.00"),
                payment_type=PaymentType.ADVANCE,
                payment_date=payment_date
            )

    def test_create_schema_payment_date_defaults_to_now(self):
        """Test MusicianEventPaymentCreate payment_date defaults to current time"""
        payment = MusicianEventPaymentCreate(
            event_id=1,
            musician_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE
        )
        assert payment.payment_date is not None
        # Check that it's a datetime object (close to current time)
        assert isinstance(payment.payment_date, datetime)


class TestMusicianEventPaymentResponse:
    """Tests for MusicianEventPaymentResponse schema"""

    def test_response_schema_has_id(self):
        """Test MusicianEventPaymentResponse includes id field"""
        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        payment = MusicianEventPaymentResponse(
            id=1,
            event_id=1,
            musician_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date,
            created_at=now,
            updated_at=now
        )
        assert payment.id == 1

    def test_response_schema_has_timestamps(self):
        """Test MusicianEventPaymentResponse includes timestamps"""
        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        payment = MusicianEventPaymentResponse(
            id=1,
            event_id=1,
            musician_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date,
            created_at=now,
            updated_at=now
        )
        assert payment.created_at is not None
        assert payment.updated_at is not None
        assert payment.payment_date == payment_date


class TestMusicianPaymentSummaryResponse:
    """Tests for MusicianPaymentSummaryResponse schema"""

    def test_summary_schema_fields(self):
        """Test MusicianPaymentSummaryResponse has required fields"""
        summary = MusicianPaymentSummaryResponse(
            musician_id=1,
            total_paid=Decimal("2500.00"),
            payment_count=3
        )
        assert summary.musician_id == 1
        assert summary.total_paid == Decimal("2500.00")
        assert summary.payment_count == 3