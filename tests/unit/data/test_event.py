import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from models.event import Event, EventStatus
import data.event as event_data


class TestEventDataCreate:
    """Tests for event creation in data layer"""
    
    @patch('data.event.SessionLocal')
    def test_create_event_success(self, mock_session_local):
        """Test successful event creation"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            description="An amazing rock concert",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            is_all_day=False,
            user_id=1,
            status=EventStatus.PENDING
        )
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh = lambda x: setattr(x, 'id', 1)
        
        # Act
        result = event_data.create(mock_event)
        
        # Assert
        assert result is not None
        mock_db.add.assert_called_once_with(mock_event)
        mock_db.commit.assert_called_once()

    @patch('data.event.SessionLocal')
    def test_create_event_raises_database_error(self, mock_session_local):
        """Test event creation raises DatabaseError on failure"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        # Use SQLAlchemyError to match the actual exception handling
        from sqlalchemy.exc import SQLAlchemyError
        mock_db.commit.side_effect = SQLAlchemyError("Database error")
        
        mock_event = Event(
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1
        )
        
        # Act & Assert
        from exceptions import DatabaseError
        with pytest.raises(DatabaseError):
            event_data.create(mock_event)


class TestEventDataGet:
    """Tests for retrieving events in data layer"""
    
    @patch('data.event.SessionLocal')
    def test_get_one_by_id_found(self, mock_session_local):
        """Test getting event by ID when it exists"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_event
        
        # Act
        result = event_data.get_one_by_id(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert result.name == "Rock Concert"

    @patch('data.event.SessionLocal')
    def test_get_one_by_id_not_found(self, mock_session_local):
        """Test getting event by ID when it doesn't exist"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = event_data.get_one_by_id(999)
        
        # Assert
        assert result is None

    @patch('data.event.SessionLocal')
    def test_get_all_returns_list(self, mock_session_local):
        """Test getting all events"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_events = [
            Event(id=1, name="Event 1", place="Place 1", start_datetime=datetime(2026, 3, 15, 20, 0), end_datetime=datetime(2026, 3, 15, 23, 0), user_id=1),
            Event(id=2, name="Event 2", place="Place 2", start_datetime=datetime(2026, 3, 16, 20, 0), end_datetime=datetime(2026, 3, 16, 23, 0), user_id=2),
        ]
        mock_db.query.return_value.all.return_value = mock_events
        
        # Act
        result = event_data.get_all()
        
        # Assert
        assert len(result) == 2


class TestEventDataModify:
    """Tests for modifying events in data layer"""
    
    @patch('data.event.SessionLocal')
    def test_modify_event_success(self, mock_session_local):
        """Test successful event modification"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        existing_event = Event(
            id=1,
            name="Old Name",
            place="Old Place",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1
        )
        mock_db.query.return_value.filter.return_value.first.return_value = existing_event
        mock_db.commit.return_value = None
        
        updated_event = Event(
            id=1,
            name="New Name",
            place="New Place",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1
        )
        
        # Act
        result = event_data.modify(updated_event)
        
        # Assert
        assert result is not None
        assert result.name == "New Name"
        mock_db.commit.assert_called_once()

    @patch('data.event.SessionLocal')
    def test_modify_event_not_found(self, mock_session_local):
        """Test modifying non-existent event returns None"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        updated_event = Event(
            id=999,
            name="New Name",
            place="New Place",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1
        )
        
        # Act
        result = event_data.modify(updated_event)
        
        # Assert
        assert result is None


class TestEventDataDelete:
    """Tests for deleting events in data layer"""
    
    @patch('data.event.SessionLocal')
    def test_delete_event_success(self, mock_session_local):
        """Test successful event deletion"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_event = Event(
            id=1,
            name="Event to Delete",
            place="Place",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_event
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None
        
        # Act
        result = event_data.delete(1)
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_event)
        mock_db.commit.assert_called_once()

    @patch('data.event.SessionLocal')
    def test_delete_event_not_found(self, mock_session_local):
        """Test deleting non-existent event returns False"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = event_data.delete(999)
        
        # Assert
        assert result is False
