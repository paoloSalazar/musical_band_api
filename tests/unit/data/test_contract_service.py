import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from models.event import Event
from models.user import User
import data.contract_service as contract_data


class TestGetContractData:
    """Tests for contract data retrieval"""

    @patch('data.contract_service.SessionLocal')
    def test_get_contract_data_success(self, mock_session_local):
        """Test successful contract data retrieval"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.name = "Concert"
        mock_event.place = "Venue"
        mock_event.start_datetime = datetime(2026, 6, 15, 20, 0)
        mock_event.end_datetime = datetime(2026, 6, 15, 23, 0)
        mock_event.price = 1000.0
        mock_event.user_id = 2

        mock_user = MagicMock()
        mock_user.name = "John"
        mock_user.lastname = "Doe"
        mock_user.phone_number = "12345678"

        mock_event.user = mock_user
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_event

        result = contract_data.get_contract_data(1)

        assert result is not None
        assert result["event_id"] == 1
        assert result["event_name"] == "Concert"
        assert result["event_location"] == "Venue"
        assert result["event_price"] == 1000.0
        assert result["client_name"] == "John Doe"
        assert result["client_phone"] == "12345678"

    @patch('data.contract_service.SessionLocal')
    def test_get_contract_data_event_not_found(self, mock_session_local):
        """Test contract data for non-existent event"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None

        result = contract_data.get_contract_data(999)

        assert result is None