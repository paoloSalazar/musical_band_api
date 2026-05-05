"""
Unit tests for MusicianEventPayment data layer.

These tests follow TDD approach - they define expected behavior before the data layer exists.
Tests should FAIL until the data/musician_event_payment.py module is implemented.
"""
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime, timezone
from models.musician_event_payment import MusicianEventPayment
from models.event_payment import PaymentType
import data.musician_event_payment as payment_data


class TestMusicianEventPaymentDataCreate:
    """Tests for payment creation in data layer"""

    @patch('data.musician_event_payment.SessionLocal')
    def test_create_payment_success(self, mock_session_local):
        """Test successful payment creation"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_payment = MusicianEventPayment(
            id=1,
            event_id=1,
            musician_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date,
            notes="Initial musician payment"
        )
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh = lambda x: setattr(x, 'id', 1)

        # Act
        result = payment_data.create(mock_payment)

        # Assert
        assert result is not None
        mock_db.add.assert_called_once_with(mock_payment)
        mock_db.commit.assert_called_once()


class TestMusicianEventPaymentDataGet:
    """Tests for getting payments from data layer"""

    @patch('data.musician_event_payment.SessionLocal')
    def test_get_one_payment_success(self, mock_session_local):
        """Test getting a single payment by ID"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_payment = MusicianEventPayment(
            id=1,
            event_id=1,
            musician_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_payment

        # Act
        result = payment_data.get_one(1)

        # Assert
        assert result is not None
        assert result.id == 1
        mock_db.query.assert_called_once()


class TestMusicianEventPaymentDataGetByEvent:
    """Tests for getting payments by event"""

    @patch('data.musician_event_payment.SessionLocal')
    def test_get_payments_by_event_success(self, mock_session_local):
        """Test getting all payments for an event"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_payments = [
            MusicianEventPayment(id=1, event_id=1, musician_id=1, amount=Decimal("500.00"), payment_type=PaymentType.ADVANCE, payment_date=payment_date),
            MusicianEventPayment(id=2, event_id=1, musician_id=2, amount=Decimal("500.00"), payment_type=PaymentType.REMAINING, payment_date=payment_date)
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_payments

        # Act
        result = payment_data.get_payments_by_event(1)

        # Assert
        assert len(result) == 2
        mock_db.query.assert_called_once()


class TestMusicianEventPaymentDataGetByMusician:
    """Tests for getting payments by musician"""

    @patch('data.musician_event_payment.SessionLocal')
    def test_get_payments_by_musician_success(self, mock_session_local):
        """Test getting all payments for a musician"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_payments = [
            MusicianEventPayment(id=1, event_id=1, musician_id=1, amount=Decimal("500.00"), payment_type=PaymentType.ADVANCE, payment_date=payment_date),
            MusicianEventPayment(id=2, event_id=2, musician_id=1, amount=Decimal("300.00"), payment_type=PaymentType.REMAINING, payment_date=payment_date)
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_payments

        # Act
        result = payment_data.get_payments_by_musician(1)

        # Assert
        assert len(result) == 2
        mock_db.query.assert_called_once()


class TestMusicianEventPaymentDataGetByEventAndMusician:
    """Tests for getting payments by event and musician"""

    @patch('data.musician_event_payment.SessionLocal')
    def test_get_payments_by_event_and_musician_success(self, mock_session_local):
        """Test getting payments for specific event-musician pair"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_payments = [
            MusicianEventPayment(id=1, event_id=1, musician_id=1, amount=Decimal("500.00"), payment_type=PaymentType.ADVANCE, payment_date=payment_date),
            MusicianEventPayment(id=2, event_id=1, musician_id=1, amount=Decimal("300.00"), payment_type=PaymentType.REMAINING, payment_date=payment_date)
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_payments

        # Act
        result = payment_data.get_payments_by_event_and_musician(1, 1)

        # Assert
        assert len(result) == 2
        mock_db.query.assert_called_once()


class TestMusicianEventPaymentCalculations:
    """Tests for payment calculation helpers"""

    @patch('data.musician_event_payment.SessionLocal')
    def test_get_total_paid_by_musician_for_event_success(self, mock_session_local):
        """Test getting total paid by musician for specific event"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Mock a query result that returns a tuple with total
        mock_db.query.return_value.filter.return_value.scalar.return_value = Decimal("1000.00")

        # Act
        result = payment_data.get_total_paid_by_musician_for_event(1, 1)

        # Assert
        assert result == Decimal("1000.00")

    @patch('data.musician_event_payment.SessionLocal')
    def test_get_total_paid_by_musician_success(self, mock_session_local):
        """Test getting total paid by musician across all events"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.scalar.return_value = Decimal("2500.00")

        # Act
        result = payment_data.get_total_paid_by_musician(1)

        # Assert
        assert result == Decimal("2500.00")


class TestMusicianEventPaymentDataModify:
    """Tests for modifying payments"""

    @patch('data.musician_event_payment.SessionLocal')
    def test_modify_payment_success(self, mock_session_local):
        """Test modifying a payment"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_existing = MusicianEventPayment(
            id=1,
            event_id=1,
            musician_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing
        mock_db.commit.return_value = None

        # Act
        mock_existing.amount = Decimal("750.00")
        result = payment_data.modify(mock_existing)

        # Assert
        mock_db.commit.assert_called_once()
        assert result.amount == Decimal("750.00")


class TestMusicianEventPaymentDataDelete:
    """Tests for deleting payments"""

    @patch('data.musician_event_payment.check_integrity_before_deletion')
    @patch('data.musician_event_payment.SessionLocal')
    def test_delete_payment_success(self, mock_session_local, mock_integrity_check):
        """Test deleting a payment"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_integrity_check.return_value = None  # No integrity violations

        payment_date = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_payment = MusicianEventPayment(
            id=1,
            event_id=1,
            musician_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_date
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_payment
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None

        # Act
        result = payment_data.delete(1)

        # Assert
        assert result is True
        mock_integrity_check.assert_called_once_with('musician_event_payment', 1)
        mock_db.delete.assert_called_once_with(mock_payment)
        mock_db.commit.assert_called_once()