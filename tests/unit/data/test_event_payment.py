"""
Unit tests for EventPayment data layer.

These tests follow TDD approach - they define expected behavior before the data layer exists.
Tests should FAIL until the data/event_payment.py module is implemented.
"""
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime
from models.event_payment import EventPayment, PaymentType
import data.event_payment as payment_data


class TestEventPaymentDataCreate:
    """Tests for payment creation in data layer"""
    
    @patch('data.event_payment.SessionLocal')
    def test_create_payment_success(self, mock_session_local):
        """Test successful payment creation"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_payment = EventPayment(
            id=1,
            event_id=1,
            user_id=1,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.ADVANCE,
            notes="Initial payment"
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


class TestEventPaymentDataGet:
    """Tests for getting payments from data layer"""
    
    @patch('data.event_payment.SessionLocal')
    def test_get_one_payment_success(self, mock_session_local):
        """Test getting a single payment by ID"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_payment = EventPayment(
            id=1,
            event_id=1,
            user_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_payment
        
        # Act
        result = payment_data.get_one(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_db.query.assert_called_once()


class TestEventPaymentDataGetByEvent:
    """Tests for getting payments by event"""
    
    @patch('data.event_payment.SessionLocal')
    def test_get_payments_by_event_success(self, mock_session_local):
        """Test getting all payments for an event"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_payments = [
            EventPayment(id=1, event_id=1, user_id=1, amount=Decimal("500.00"), payment_type=PaymentType.ADVANCE),
            EventPayment(id=2, event_id=1, user_id=1, amount=Decimal("500.00"), payment_type=PaymentType.REMAINING)
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_payments
        
        # Act
        result = payment_data.get_payments_by_event(1)
        
        # Assert
        assert len(result) == 2
        mock_db.query.assert_called_once()


class TestEventPaymentCalculations:
    """Tests for payment calculation helpers"""
    
    @patch('data.event_payment.SessionLocal')
    def test_get_total_paid_success(self, mock_session_local):
        """Test getting total paid for an event"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock a query result that returns a tuple with total
        mock_db.query.return_value.filter.return_value.scalar.return_value = Decimal("1000.00")
        
        # Act
        result = payment_data.get_total_paid(1)
        
        # Assert
        assert result == Decimal("1000.00")
    
    @patch('data.event_payment.SessionLocal')
    def test_get_pending_balance_success(self, mock_session_local):
        """Test getting pending balance for an event"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock query for total paid (returns 500)
        # Mock query for final price (returns 1000 via event query)
        def mock_query_side_effect(table):
            mock_q = MagicMock()
            if hasattr(table, '__name__') and table.__name__ == 'Event':
                mock_q.filter.return_value.first.return_value = MagicMock(final_price=Decimal("1000.00"))
            else:
                mock_q.filter.return_value.scalar.return_value = Decimal("500.00")
            return mock_q
        
        mock_db.query.side_effect = mock_query_side_effect
        
        # Act
        result = payment_data.get_pending_balance(1, 1000)
        
        # Assert
        assert result == Decimal("500.00")


class TestEventPaymentDataModify:
    """Tests for modifying payments"""
    
    @patch('data.event_payment.SessionLocal')
    def test_modify_payment_success(self, mock_session_local):
        """Test modifying a payment"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_existing = EventPayment(
            id=1,
            event_id=1,
            user_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing
        mock_db.commit.return_value = None
        
        # Act
        mock_existing.amount = Decimal("750.00")
        result = payment_data.modify(mock_existing)
        
        # Assert
        mock_db.commit.assert_called_once()
        assert result.amount == Decimal("750.00")


class TestEventPaymentDataDelete:
    """Tests for deleting payments"""
    
    @patch('data.event_payment.check_integrity_before_deletion')
    @patch('data.event_payment.SessionLocal')
    def test_delete_payment_success(self, mock_session_local, mock_integrity_check):
        """Test deleting a payment"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_integrity_check.return_value = None  # No integrity violations

        mock_payment = EventPayment(
            id=1,
            event_id=1,
            user_id=1,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_payment
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None

        # Act
        result = payment_data.delete(1)

        # Assert
        assert result is True
        mock_integrity_check.assert_called_once_with('event_payment', 1)
        mock_db.delete.assert_called_once_with(mock_payment)
        mock_db.commit.assert_called_once()