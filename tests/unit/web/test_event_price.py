"""Tests for event price endpoints in web layer."""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from datetime import datetime
from models.event import Event, EventStatus
from schemas.event import EventResponse
import services.event as event_service
import web.event as event_web
from exceptions import NotFoundError, DatabaseError
from fastapi import HTTPException


class TestEventWebSetPrice:
    """Tests for setting event price endpoint"""

    def test_set_price_success(self, mocker):
        """Test successfully setting price on an event"""
        # Arrange
        mock_service = mocker.patch('web.event.event_service.set_price')
        mock_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            price=Decimal("5000.00")
        )
        mock_service.return_value = EventResponse(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            is_all_day=False,
            user_id=1,
            status="PENDING",
            price=5000.00
        )
        
        mock_current_user = {"sub": "admin@example.com", "role": "admin"}
        
        # Act
        result = event_web.set_price(
            current_user=mock_current_user,
            event_id=1,
            price=5000.00
        )
        
        # Assert
        assert result is not None
        mock_service.assert_called_once_with(1, Decimal("5000.00"))

    def test_set_price_not_found(self, mocker):
        """Test setting price on non-existent event raises HTTPException"""
        # Arrange
        mock_service = mocker.patch('web.event.event_service.set_price')
        mock_service.side_effect = NotFoundError("Event not found")
        
        mock_current_user = {"sub": "admin@example.com", "role": "admin"}
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            event_web.set_price(
                current_user=mock_current_user,
                event_id=999,
                price=5000.00
            )
        assert exc_info.value.status_code == 404

    def test_set_price_database_error(self, mocker):
        """Test setting price raises HTTPException on database error"""
        # Arrange
        mock_service = mocker.patch('web.event.event_service.set_price')
        mock_service.side_effect = DatabaseError("Database error")
        
        mock_current_user = {"sub": "admin@example.com", "role": "admin"}
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            event_web.set_price(
                current_user=mock_current_user,
                event_id=1,
                price=5000.00
            )
        assert exc_info.value.status_code == 500


class TestEventWebGetPrice:
    """Tests for getting event price endpoint"""

    def test_get_price_success(self, mocker):
        """Test successfully getting price of an event"""
        # Arrange
        mock_service = mocker.patch('web.event.event_service.get_price')
        mock_service.return_value = Decimal("5000.00")
        
        mock_current_user = {"sub": "admin@example.com", "role": "admin"}
        
        # Act
        result = event_web.get_price(
            current_user=mock_current_user,
            event_id=1
        )
        
        # Assert
        assert result == Decimal("5000.00")
        mock_service.assert_called_once_with(1)

    def test_get_price_not_found(self, mocker):
        """Test getting price of non-existent event raises HTTPException"""
        # Arrange
        mock_service = mocker.patch('web.event.event_service.get_price')
        mock_service.side_effect = NotFoundError("Event not found")
        
        mock_current_user = {"sub": "admin@example.com", "role": "admin"}
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            event_web.get_price(
                current_user=mock_current_user,
                event_id=999
            )
        assert exc_info.value.status_code == 404

    def test_get_price_database_error(self, mocker):
        """Test getting price raises HTTPException on database error"""
        # Arrange
        mock_service = mocker.patch('web.event.event_service.get_price')
        mock_service.side_effect = DatabaseError("Database error")
        
        mock_current_user = {"sub": "admin@example.com", "role": "admin"}
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            event_web.get_price(
                current_user=mock_current_user,
                event_id=1
            )
        assert exc_info.value.status_code == 500