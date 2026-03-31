"""
Unit tests for EventPayment service layer.

Tests follow TDD - define expected service behavior before implementation.
Tests should FAIL until services/event_payment.py is created.
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from models.event import EventStatus
from schemas.event_payment import EventPaymentCreate, PaymentType
import services.event_payment as payment_service


class TestCreatePayment:
    """Tests for payment creation service"""
    
    @patch('data.event.get_one')
    @patch('data.event_payment.get_payments_by_event')
    @patch('services.event_payment.create_payment_data')
    def test_create_payment_success(self, mock_create_data, mock_get_payments, mock_get_event):
        """Test successful payment creation"""
        # Arrange
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.price = Decimal("1000.00")
        mock_event.start_datetime = datetime.now() + timedelta(days=7)
        mock_get_event.return_value = mock_event
        
        # No existing payments
        mock_get_payments.return_value = []
        
        mock_payment = MagicMock()
        mock_payment.id = 1
        mock_payment.event_id = 1
        mock_payment.user_id = 1
        mock_payment.amount = Decimal("1000.00")
        mock_payment.payment_type = PaymentType.ADVANCE
        mock_payment.payment_date = datetime.now()
        mock_payment.created_at = datetime.now()
        mock_payment.notes = None
        mock_create_data.return_value = mock_payment
        
        # Act
        result = payment_service.create_payment(
            event_id=1,
            user_id=1,
            amount=Decimal("400.00"),
            payment_type=PaymentType.ADVANCE
        )
        
        # Assert
        assert result is not None
    
    @patch('data.event.get_one')
    @patch('data.event_payment.get_payments_by_event')
    def test_total_payment_fails_when_amount_not_equal_final_price(self, mock_get_payments, mock_get_event):
        """Test TOTAL payment fails when amount doesn't equal final price"""
        # Arrange
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.price = Decimal("1000.00")
        mock_event.start_datetime = datetime.now() + timedelta(days=7)
        mock_get_event.return_value = mock_event
        
        # No existing payments
        mock_get_payments.return_value = []
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            payment_service.create_payment(
                event_id=1,
                user_id=1,
                amount=Decimal("1500.00"),  # Different from final price
                payment_type=PaymentType.TOTAL
            )
        assert "must equal the event's final price" in str(exc_info.value)
    
    @patch('data.event.get_one')
    @patch('data.event_payment.get_payments_by_event')
    def test_total_payment_fails_when_already_exists(self, mock_get_payments, mock_get_event):
        """Test TOTAL payment fails when a TOTAL payment already exists"""
        # Arrange
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.price = Decimal("1000.00")
        mock_event.start_datetime = datetime.now() + timedelta(days=7)
        mock_get_event.return_value = mock_event
        
        # Existing TOTAL payment
        mock_existing_payment = MagicMock()
        mock_existing_payment.payment_type = PaymentType.TOTAL
        mock_get_payments.return_value = [mock_existing_payment]
        
        # Act & Assert
        from exceptions import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            payment_service.create_payment(
                event_id=1,
                user_id=1,
                amount=Decimal("1000.00"),
                payment_type=PaymentType.TOTAL
            )
        assert "TOTAL payment has already been made" in str(exc_info.value)
    
    @patch('data.event.get_one')
    @patch('data.event_payment.get_payments_by_event')
    def test_advance_payment_exceeds_remaining_balance(self, mock_get_payments, mock_get_event):
        """Test ADVANCE payment fails when amount exceeds remaining balance"""
        # Arrange
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.price = Decimal("2500.00")
        mock_event.start_datetime = datetime.now() + timedelta(days=7)
        mock_get_event.return_value = mock_event
        
        # Existing ADVANCE payment of 800
        mock_existing_payment = MagicMock()
        mock_existing_payment.amount = Decimal("800.00")
        mock_existing_payment.payment_type = PaymentType.ADVANCE
        mock_get_payments.return_value = [mock_existing_payment]
        
        # Act & Assert
        from exceptions import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            payment_service.create_payment(
                event_id=1,
                user_id=1,
                amount=Decimal("2800.00"),  # Exceeds remaining 1700
                payment_type=PaymentType.ADVANCE
            )
        assert "exceeds remaining balance" in str(exc_info.value)


class TestGetPaymentSummary:
    """Tests for payment summary service"""
    
    def test_get_summary_fully_paid(self):
        """Test summary when event is fully paid"""
        # Act
        result = payment_service.get_event_payment_summary(
            event_id=1,
            final_price=Decimal("1000.00")
        )
        
        # Assert - will call actual data function
        assert result.event_id == 1
        assert result.final_price == Decimal("1000.00")
    
    def test_get_summary_partially_paid(self):
        """Test summary when event is partially paid"""
        # Act
        result = payment_service.get_event_payment_summary(
            event_id=1,
            final_price=Decimal("1000.00")
        )
        
        # Assert - will call actual data function
        assert result.event_id == 1
        assert result.final_price == Decimal("1000.00")


class TestValidatePayment:
    """Tests for payment validation service"""
    
    def test_validate_advance_minimum_30_percent(self):
        """Test ADVANCE payment must be at least 30%"""
        # Should validate 30% minimum for advance payments
        from services.event_payment import validate_payment_amount
        result = validate_payment_amount(
            amount=Decimal("300.00"),
            payment_type=PaymentType.ADVANCE,
            final_price=Decimal("1000.00")
        )
        assert result is True
    
    def test_advance_below_minimum_fails(self):
        """Test ADVANCE payment below 30% fails"""
        from services.event_payment import validate_payment_amount
        with pytest.raises(ValueError):
            validate_payment_amount(
                amount=Decimal("200.00"),
                payment_type=PaymentType.ADVANCE,
                final_price=Decimal("1000.00")
            )
    
    def test_total_payment_no_minimum(self):
        """Test TOTAL payment must equal final price"""
        from services.event_payment import validate_payment_amount
        # TOTAL payment equal to final price should pass
        result = validate_payment_amount(
            amount=Decimal("1000.00"),
            payment_type=PaymentType.TOTAL,
            final_price=Decimal("1000.00")
        )
        assert result is True
    
    def test_total_payment_must_equal_final_price(self):
        """Test TOTAL payment fails when amount doesn't equal final price"""
        from services.event_payment import validate_payment_amount
        with pytest.raises(ValueError) as exc_info:
            validate_payment_amount(
                amount=Decimal("500.00"),
                payment_type=PaymentType.TOTAL,
                final_price=Decimal("1000.00")
            )
        assert "must equal the event's final price" in str(exc_info.value)
    
    def test_validate_payment_deadline(self):
        """Test payment validates event deadline"""
        from services.event_payment import validate_payment_deadline
        # Should fail if event is within 24 hours
        pass