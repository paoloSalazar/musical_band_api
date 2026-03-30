"""Tests for event payment endpoints in web layer."""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from datetime import datetime
from models.event import Event, EventStatus
from models.event_payment import EventPayment, PaymentType
from schemas.event_payment import (
    EventPaymentCreate,
    EventPaymentResponse,
    EventPaymentSummary,
    PaymentType as SchemaPaymentType
)
import services.event_payment as payment_service
import services.event as event_service
from exceptions import NotFoundError, DatabaseError
from fastapi import HTTPException


class TestAddPayment:
    """Tests for adding payment endpoint"""

    def test_add_payment_success(self, mocker):
        """Test successfully adding a payment for an event"""
        # Arrange
        mock_service = mocker.patch('web.event_payment.payment_service.create_payment')
        mock_response = EventPaymentResponse(
            id=1,
            event_id=1,
            user_id=1,
            amount=Decimal("1000.00"),
            payment_type=SchemaPaymentType.ADVANCE,
            payment_date=datetime(2026, 3, 15, 10, 0),
            notes="Advance payment",
            created_at=datetime(2026, 3, 10, 10, 0)
        )
        mock_service.return_value = mock_response
        
        mock_current_user = {"sub": "user@example.com", "role": "user"}
        payment_data = EventPaymentCreate(
            event_id=1,
            user_id=1,
            amount=Decimal("1000.00"),
            payment_type=SchemaPaymentType.ADVANCE,
            notes="Advance payment"
        )
        
        # Act
        import web.event_payment as payment_web
        result = payment_web.add_payment(
            current_user=mock_current_user,
            event_id=1,
            payment_data=payment_data
        )
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert result.amount == Decimal("1000.00")
        mock_service.assert_called_once()

    def test_add_payment_event_not_found(self, mocker):
        """Test adding payment to non-existent event raises HTTPException"""
        # Arrange
        mock_service = mocker.patch('web.event_payment.payment_service.create_payment')
        mock_service.side_effect = NotFoundError("Event not found")
        
        mock_current_user = {"sub": "user@example.com", "role": "user"}
        payment_data = EventPaymentCreate(
            event_id=999,
            user_id=1,
            amount=Decimal("1000.00"),
            payment_type=SchemaPaymentType.ADVANCE
        )
        
        # Act & Assert
        import web.event_payment as payment_web
        with pytest.raises(HTTPException) as exc_info:
            payment_web.add_payment(
                current_user=mock_current_user,
                event_id=999,
                payment_data=payment_data
            )
        assert exc_info.value.status_code == 404


class TestListPayments:
    """Tests for listing payments endpoint"""

    def test_list_payments_success(self, mocker):
        """Test successfully listing payments for an event"""
        # Arrange
        mock_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            price=Decimal("5000.00")
        )
        
        mock_payment = EventPayment(
            id=1,
            event_id=1,
            user_id=1,
            amount=Decimal("1000.00"),
            payment_type="ADVANCE",
            payment_date=datetime(2026, 3, 10, 10, 0),
            notes="Advance",
            created_at=datetime(2026, 3, 10, 10, 0)
        )
        
        mock_event_service = mocker.patch('web.event_payment.event_service.get_one')
        mock_event_service.return_value = mock_event
        
        mock_get_payments = mocker.patch('web.event_payment.payment_data.get_payments_by_event')
        mock_get_payments.return_value = [mock_payment]
        
        mock_current_user = {"sub": "user@example.com", "role": "user"}
        
        # Act
        import web.event_payment as payment_web
        result = payment_web.list_payments(
            current_user=mock_current_user,
            event_id=1
        )
        
        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0].id == 1

    def test_list_payments_event_not_found(self, mocker):
        """Test listing payments for non-existent event"""
        # Arrange
        mock_service = mocker.patch('web.event_payment.event_service.get_one')
        mock_service.return_value = None
        
        mock_current_user = {"sub": "user@example.com", "role": "user"}
        
        # Act & Assert
        import web.event_payment as payment_web
        with pytest.raises(HTTPException) as exc_info:
            payment_web.list_payments(
                current_user=mock_current_user,
                event_id=999
            )
        assert exc_info.value.status_code == 404


class TestGetPaymentSummary:
    """Tests for payment summary endpoint"""

    def test_get_summary_success(self, mocker):
        """Test successfully getting payment summary"""
        # Arrange
        mock_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            price=Decimal("5000.00")
        )
        
        mock_event_service = mocker.patch('web.event_payment.event_service.get_one')
        mock_event_service.return_value = mock_event
        
        mock_summary = EventPaymentSummary(
            event_id=1,
            total_paid=Decimal("1000.00"),
            pending_balance=Decimal("4000.00"),
            final_price=Decimal("5000.00"),
            is_fully_paid=False
        )
        
        mock_summary_service = mocker.patch('web.event_payment.payment_service.get_event_payment_summary')
        mock_summary_service.return_value = mock_summary
        
        mock_current_user = {"sub": "user@example.com", "role": "user"}
        
        # Act
        import web.event_payment as payment_web
        result = payment_web.get_payment_summary(
            current_user=mock_current_user,
            event_id=1
        )
        
        # Assert
        assert result is not None
        assert result.event_id == 1
        assert result.total_paid == Decimal("1000.00")
        assert result.pending_balance == Decimal("4000.00")

    def test_get_summary_event_not_found(self, mocker):
        """Test getting summary for non-existent event"""
        # Arrange
        mock_service = mocker.patch('web.event_payment.event_service.get_one')
        mock_service.return_value = None
        
        mock_current_user = {"sub": "user@example.com", "role": "user"}
        
        # Act & Assert
        import web.event_payment as payment_web
        with pytest.raises(HTTPException) as exc_info:
            payment_web.get_payment_summary(
                current_user=mock_current_user,
                event_id=999
            )
        assert exc_info.value.status_code == 404

    def test_get_summary_price_not_set(self, mocker):
        """Test getting summary when event price not set"""
        # Arrange
        mock_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            price=None  # Price not set
        )
        
        mock_event_service = mocker.patch('web.event_payment.event_service.get_one')
        mock_event_service.return_value = mock_event
        
        mock_current_user = {"sub": "user@example.com", "role": "user"}
        
        # Act & Assert
        import web.event_payment as payment_web
        with pytest.raises(HTTPException) as exc_info:
            payment_web.get_payment_summary(
                current_user=mock_current_user,
                event_id=1
            )
        assert exc_info.value.status_code == 400