import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from models.event import Event
from models.user import User
from models.event_payment import EventPayment
from models.user_detail import UserDetail
import data.receipt_service as receipt_data


class TestGetReceiptData:
    """Tests for receipt data retrieval"""

    @patch('data.receipt_service.SessionLocal')
    def test_get_receipt_data_success(self, mock_session_local):
        """Test successful receipt data retrieval"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.name = "Concert"
        mock_event.price = 1000.0
        mock_event.user_id = 2

        mock_user = MagicMock()
        mock_user.name = "John"
        mock_user.lastname = "Doe"
        mock_user.phone_number = "12345678"
        mock_user.ci = None

        mock_payment = MagicMock()
        mock_payment.amount = 500.0

        mock_event.user = mock_user
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_event
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_payment]

        with patch('data.receipt_service.UserDetail') as mock_user_detail:
            mock_detail = MagicMock()
            mock_detail.detail_value = "12345678"
            mock_user_detail.query.return_value.filter.return_value.first.return_value = mock_detail

            result = receipt_data.get_receipt_data(1)

        assert result is not None
        assert result["event_id"] == 1
        assert result["event_name"] == "Concert"
        assert result["event_price"] == 1000.0
        assert result["client_name"] == "John Doe"
        assert result["total_paid"] == 500.0
        assert result["balance"] == 500.0

    @patch('data.receipt_service.SessionLocal')
    def test_get_receipt_data_event_not_found(self, mock_session_local):
        """Test receipt data for non-existent event"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None

        result = receipt_data.get_receipt_data(999)

        assert result is None

    @patch('data.receipt_service.SessionLocal')
    def test_get_receipt_data_no_payments(self, mock_session_local):
        """Test receipt data with no payments"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.name = "Concert"
        mock_event.price = 1000.0
        mock_event.user_id = 2

        mock_user = MagicMock()
        mock_user.name = "John"
        mock_user.lastname = "Doe"
        mock_user.phone_number = None
        mock_user.ci = None

        mock_event.user = mock_user
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_event
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = receipt_data.get_receipt_data(1)

        assert result is not None
        assert result["total_paid"] == 0
        assert result["balance"] == 1000.0