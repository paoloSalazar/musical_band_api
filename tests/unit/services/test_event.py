import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from models.event import Event, EventStatus
import services.event as event_service
from exceptions import NotFoundError, DatabaseError


class TestEventServiceCreate:
    """Tests for event creation in service layer"""
    
    @patch('services.event.data.create')
    def test_create_event_success(self, mock_data_create):
        """Test successful event creation"""
        # Arrange
        from schemas.event import EventCreate
        mock_event = Event(
            name="Rock Concert",
            place="Madison Square Garden",
            description="An amazing rock concert",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            is_all_day=False,
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 1, 10, 0)
        )
        mock_event.id = 1
        mock_data_create.return_value = mock_event
        
        event_data = EventCreate(
            name="Rock Concert",
            place="Madison Square Garden",
            description="An amazing rock concert",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            is_all_day=False,
            user_id=1
        )
        
        # Act
        result = event_service.create(event_data)
        
        # Assert
        assert result is not None
        assert result.name == "Rock Concert"
        mock_data_create.assert_called_once()


class TestEventServiceGet:
    """Tests for retrieving events in service layer"""
    
    @patch('services.event.data.get_one')
    def test_get_one_found(self, mock_data_get_one):
        """Test getting event by ID when it exists"""
        # Arrange
        mock_event = Event(
            id=1,
            name="Rock Concert",
            place="Madison Square Garden",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 1, 10, 0)
        )
        mock_data_get_one.return_value = mock_event
        
        # Act
        result = event_service.get_one(1)
        
        # Assert
        assert result is not None
        assert result.id == 1

    @patch('services.event.data.get_one')
    def test_get_one_not_found(self, mock_data_get_one):
        """Test getting event by ID when it doesn't exist"""
        # Arrange
        mock_data_get_one.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            event_service.get_one(999)

    @patch('services.event.data.get_all')
    def test_get_all(self, mock_data_get_all):
        """Test getting all events"""
        # Arrange
        mock_events = [
            Event(id=1, name="Event 1", place="Place 1", start_datetime=datetime(2026, 3, 15, 20, 0), end_datetime=datetime(2026, 3, 15, 23, 0), user_id=1, status=EventStatus.PENDING, created_at=datetime(2026, 1, 1, 10, 0), updated_at=datetime(2026, 1, 1, 10, 0)),
            Event(id=2, name="Event 2", place="Place 2", start_datetime=datetime(2026, 3, 16, 20, 0), end_datetime=datetime(2026, 3, 16, 23, 0), user_id=1, status=EventStatus.PENDING, created_at=datetime(2026, 1, 1, 10, 0), updated_at=datetime(2026, 1, 1, 10, 0)),
        ]
        mock_data_get_all.return_value = mock_events
        
        # Act
        result = event_service.get_all()
        
        # Assert
        assert len(result) == 2


class TestEventServiceModify:
    """Tests for modifying events in service layer"""
    
    @patch('services.event.data.get_one')
    @patch('services.event.data.modify')
    def test_modify_success(self, mock_data_modify, mock_data_get_one):
        """Test successful event modification"""
        # Arrange
        from schemas.event import EventUpdate
        
        existing_event = Event(
            id=1,
            name="Old Name",
            place="Old Place",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 1, 10, 0)
        )
        mock_data_get_one.return_value = existing_event
        
        updated_event = Event(
            id=1,
            name="New Name",
            place="New Place",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 2, 10, 0)
        )
        mock_data_modify.return_value = updated_event
        
        event_update = EventUpdate(
            name="New Name",
            place="New Place"
        )
        
        # Act
        result = event_service.modify(1, event_update)
        
        # Assert
        assert result is not None
        assert result.name == "New Name"

    @patch('services.event.data.get_one')
    def test_modify_not_found(self, mock_data_get_one):
        """Test modifying non-existent event"""
        # Arrange
        from schemas.event import EventUpdate
        mock_data_get_one.return_value = None
        
        event_update = EventUpdate(name="New Name")
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            event_service.modify(999, event_update)


class TestEventServiceDelete:
    """Tests for deleting events in service layer"""
    
    @patch('services.event.data.get_one')
    @patch('services.event.data.delete')
    def test_delete_success(self, mock_data_delete, mock_data_get_one):
        """Test successful event deletion"""
        # Arrange
        existing_event = Event(
            id=1,
            name="Event to Delete",
            place="Place",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 1, 10, 0)
        )
        mock_data_get_one.return_value = existing_event
        mock_data_delete.return_value = True
        
        # Act
        result = event_service.delete(1)
        
        # Assert
        assert result is True

    @patch('services.event.data.get_one')
    def test_delete_not_found(self, mock_data_get_one):
        """Test deleting non-existent event"""
        # Arrange
        mock_data_get_one.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            event_service.delete(999)


class TestEventServiceModifyStatus:
    """Tests for modifying event status"""
    
    @patch('services.event.data.get_one')
    @patch('services.event.data.modify')
    def test_change_status_success(self, mock_data_modify, mock_data_get_one):
        """Test successful status change"""
        from schemas.event import EventStatusEnum
        
        existing_event = Event(
            id=1,
            name="Event",
            place="Place",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 1, 10, 0)
        )
        mock_data_get_one.return_value = existing_event
        
        updated_event = Event(
            id=1,
            name="Event",
            place="Place",
            start_datetime=datetime(2026, 3, 15, 20, 0),
            end_datetime=datetime(2026, 3, 15, 23, 0),
            user_id=1,
            status=EventStatus.CONFIRMED,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 2, 10, 0)
        )
        mock_data_modify.return_value = updated_event
        
        # Act
        result = event_service.change_status(1, EventStatusEnum.CONFIRMED)
        
        # Assert
        assert result is not None
        assert result.status == EventStatusEnum.CONFIRMED
