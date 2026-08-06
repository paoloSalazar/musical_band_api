"""Tests for setting event price in data layer."""

import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime
from models.event import Event, EventStatus
import data.event as event_data


class TestEventDataSetPrice:
    """Tests for setting price on events in data layer"""

    @patch('data.event.SessionLocal')
    def test_set_price_on_event_success(self, mock_session_local):
        """Test successfully setting price on an existing event"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        existing_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            price=None
        )
        mock_db.query.return_value.filter.return_value.first.return_value = existing_event
        mock_db.commit.return_value = None

        # Act
        result = event_data.set_price(1, Decimal("5000.00"))

        # Assert
        assert result is not None
        assert result.price == Decimal("5000.00")
        mock_db.commit.assert_called_once()

    @patch('data.event.SessionLocal')
    def test_set_price_event_not_found(self, mock_session_local):
        """Test setting price on non-existent event returns None"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = event_data.set_price(999, Decimal("5000.00"))

        # Assert
        assert result is None

    @patch('data.event.SessionLocal')
    def test_set_price_updates_existing_value(self, mock_session_local):
        """Test updating an event that already has a price"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        existing_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            price=Decimal("1000.00")
        )
        mock_db.query.return_value.filter.return_value.first.return_value = existing_event
        mock_db.commit.return_value = None

        # Act
        result = event_data.set_price(1, Decimal("7500.00"))

        # Assert
        assert result is not None
        assert result.price == Decimal("7500.00")
        mock_db.commit.assert_called_once()


class TestEventDataGetPrice:
    """Tests for getting price from events in data layer"""

    @patch('data.event.SessionLocal')
    def test_get_price_returns_correct_value(self, mock_session_local):
        """Test getting price returns the correct value"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        existing_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            price=Decimal("5000.00")
        )
        mock_db.query.return_value.filter.return_value.first.return_value = existing_event

        # Act
        result = event_data.get_price(1)

        # Assert
        assert result == Decimal("5000.00")

    @patch('data.event.SessionLocal')
    def test_get_price_returns_none_when_no_price(self, mock_session_local):
        """Test getting price returns None when price is not set"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        existing_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            price=None
        )
        mock_db.query.return_value.filter.return_value.first.return_value = existing_event

        # Act
        result = event_data.get_price(1)

        # Assert
        assert result is None

    @patch('data.event.SessionLocal')
    def test_get_price_returns_none_when_event_not_found(self, mock_session_local):
        """Test getting price returns None when event doesn't exist"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = event_data.get_price(999)

        # Assert
        assert result is None