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
    
    @patch('data.event.check_integrity_before_deletion')
    @patch('data.event.SessionLocal')
    def test_delete_event_success(self, mock_session_local, mock_integrity_check):
        """Test successful event deletion"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_integrity_check.return_value = None  # No integrity violations

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
        mock_integrity_check.assert_called_once_with('event', 1)
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


# Note: Pagination and calendar functionality is tested in service layer tests
# See tests/unit/services/test_event.py::TestEventServicePaginated
# and tests/unit/services/test_event.py::TestEventServiceCalendar


class TestEventDataMusicianFiltering:
    """TDD tests for performer (musician/auxiliar_musician/helper) role-based filtering"""

    @patch('data.event.SessionLocal')
    def test_get_paginated_musician_returns_only_assigned_events(self, mock_session_local):
        """Musician should only see events they are assigned to via event_musician"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Mock query chain for join + filter
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [MagicMock(id=10)]

        # Act
        events, total = event_data.get_paginated(
            page=1, limit=20,
            current_user_role="musician",
            current_user_id=5
        )

        # Assert - verify join on event_musicians was used
        mock_query.join.assert_called_once()
        assert total == 1
        assert len(events) == 1

    @patch('data.event.SessionLocal')
    def test_get_paginated_admin_returns_all_events(self, mock_session_local):
        """Admin role must bypass musician filtering and see all events"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.count.return_value = 42
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        events, total = event_data.get_paginated(
            page=1, limit=20,
            current_user_role="admin",
            current_user_id=99
        )

        # No join should be performed for admin
        assert not hasattr(mock_query, 'join') or mock_query.join.call_count == 0
        assert total == 42

    @patch('data.event.SessionLocal')
    def test_get_by_month_musician_filters_by_assignment(self, mock_session_local):
        """Calendar view for performer (helper) must also respect assignment filter"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        events = event_data.get_events_by_month(
            year=2026, month=5,
            current_user_role="helper",
            current_user_id=7
        )

        mock_query.join.assert_called_once()
        assert len(events) == 0
