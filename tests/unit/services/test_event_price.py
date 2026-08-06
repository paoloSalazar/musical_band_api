"""Tests for event price in service layer."""

import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime
from models.event import Event, EventStatus
import services.event as event_service
from exceptions import NotFoundError, DatabaseError


class TestEventServiceSetPrice:
    """Tests for setting event price in service layer"""

    @patch('services.event.data.set_price')
    def test_set_price_success(self, mock_data_set_price):
        """Test successfully setting price on an event"""
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
        mock_data_set_price.return_value = mock_event

        # Act
        result = event_service.set_price(1, Decimal("5000.00"))

        # Assert
        assert result is not None
        assert result.price == Decimal("5000.00")
        mock_data_set_price.assert_called_once_with(1, Decimal("5000.00"))

    @patch('services.event.data.set_price')
    def test_set_price_not_found(self, mock_data_set_price):
        """Test setting price on non-existent event raises NotFoundError"""
        # Arrange
        mock_data_set_price.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            event_service.set_price(999, Decimal("5000.00"))

    @patch('services.event.data.set_price')
    def test_set_price_database_error(self, mock_data_set_price):
        """Test setting price raises DatabaseError on failure"""
        # Arrange
        from exceptions import DatabaseError as DBError
        mock_data_set_price.side_effect = DBError("Database error")

        # Act & Assert
        with pytest.raises(DatabaseError):
            event_service.set_price(1, Decimal("5000.00"))


class TestEventServiceGetPrice:
    """Tests for getting event price in service layer"""

    @patch('services.event.data.get_price')
    def test_get_price_success(self, mock_data_get_price):
        """Test successfully getting price of an event"""
        # Arrange
        mock_data_get_price.return_value = Decimal("5000.00")

        # Act
        result = event_service.get_price(1)

        # Assert
        assert result == Decimal("5000.00")
        mock_data_get_price.assert_called_once_with(1)

    @patch('services.event.data.get_price')
    def test_get_price_not_found(self, mock_data_get_price):
        """Test getting price of non-existent event raises NotFoundError"""
        # Arrange
        mock_data_get_price.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            event_service.get_price(999)

    @patch('services.event.data.get_price')
    def test_get_price_database_error(self, mock_data_get_price):
        """Test getting price raises DatabaseError on failure"""
        # Arrange
        from exceptions import DatabaseError as DBError
        mock_data_get_price.side_effect = DBError("Database error")

        # Act & Assert
        with pytest.raises(DatabaseError):
            event_service.get_price(1)

    @patch('services.event.data.get_price')
    def test_get_price_returns_none_when_not_set(self, mock_data_get_price):
        """Test getting price returns None when price is not set"""
        # Arrange
        mock_data_get_price.return_value = None

        # Act
        result = event_service.get_price(1)

        # Assert
        assert result is None