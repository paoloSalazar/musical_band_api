import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from models.event import Event, EventStatus
import services.event as event_service
from exceptions import NotFoundError, DatabaseError, ConflictError


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
    
    @patch('services.event.data.get_one_with_user')
    def test_get_one_found(self, mock_data_get_one_with_user):
        """Test getting event by ID when it exists"""
        # Arrange
        from models.user import User
        mock_user = User(
            id=1,
            name="John",
            lastname="Doe",
            email="john@example.com",
            password="hashed",
            role_id=1
        )
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
        mock_event.user = mock_user  # Set the relationship
        mock_data_get_one_with_user.return_value = mock_event
        
        # Act
        result = event_service.get_one(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert result.created_by is not None
        assert result.created_by.name == "John"

    @patch('services.event.data.get_one_with_user')
    def test_get_one_not_found(self, mock_data_get_one_with_user):
        """Test getting event by ID when it doesn't exist"""
        # Arrange
        mock_data_get_one_with_user.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            event_service.get_one(999)

    @patch('services.event.data.get_all_with_users')
    def test_get_all(self, mock_data_get_all_with_users):
        """Test getting all events"""
        # Arrange
        from models.user import User
        mock_user = User(
            id=1,
            name="John",
            lastname="Doe",
            email="john@example.com",
            password="hashed",
            role_id=1
        )
        mock_events = [
            Event(id=1, name="Event 1", place="Place 1", start_datetime=datetime(2026, 3, 15, 20, 0), end_datetime=datetime(2026, 3, 15, 23, 0), user_id=1, status=EventStatus.PENDING, created_at=datetime(2026, 1, 1, 10, 0), updated_at=datetime(2026, 1, 1, 10, 0)),
            Event(id=2, name="Event 2", place="Place 2", start_datetime=datetime(2026, 3, 16, 20, 0), end_datetime=datetime(2026, 3, 16, 23, 0), user_id=1, status=EventStatus.PENDING, created_at=datetime(2026, 1, 1, 10, 0), updated_at=datetime(2026, 1, 1, 10, 0)),
        ]
        # Set the user relationship for both events
        mock_events[0].user = mock_user
        mock_events[1].user = mock_user
        mock_data_get_all_with_users.return_value = mock_events
        
        # Act
        result = event_service.get_all()
        
        # Assert
        assert len(result) == 2
        assert result[0].created_by is not None
        assert result[1].created_by is not None


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


class TestEventConflictValidation:
    """Tests for event conflict validation"""
    
    @patch('services.event.data.get_events_in_date_range')
    def test_create_event_conflict_all_day_with_all_day(self, mock_get_events):
        """Test creating an all-day event conflicts with existing all-day event on same date"""
        # Arrange
        from schemas.event import EventCreate
        
        # Existing all-day event on the same date
        existing_event = Event(
            id=1,
            name="Existing Event",
            place="Place",
            start_datetime=datetime(2026, 3, 22, 0, 0),
            end_datetime=datetime(2026, 3, 22, 23, 59),
            is_all_day=True,
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 1, 10, 0)
        )
        mock_get_events.return_value = [existing_event]
        
        event_data = EventCreate(
            name="New All-Day Event",
            place="New Place",
            start_datetime=datetime(2026, 3, 22, 0, 0),
            end_datetime=datetime(2026, 3, 22, 23, 59),
            is_all_day=True,
            user_id=1
        )
        
        # Act & Assert
        with pytest.raises(ConflictError) as exc_info:
            event_service.create(event_data)
        assert "conflicts with existing event" in str(exc_info.value)
    
    @patch('services.event.data.get_events_in_date_range')
    def test_create_event_conflict_all_day_with_partial(self, mock_get_events):
        """Test creating an all-day event conflicts with existing partial day event on same date"""
        # Arrange
        from schemas.event import EventCreate
        
        existing_event = Event(
            id=1,
            name="Existing Partial Event",
            place="Place",
            start_datetime=datetime(2026, 3, 22, 14, 0),
            end_datetime=datetime(2026, 3, 22, 18, 0),
            is_all_day=False,
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 1, 10, 0)
        )
        mock_get_events.return_value = [existing_event]
        
        event_data = EventCreate(
            name="New All-Day Event",
            place="New Place",
            start_datetime=datetime(2026, 3, 22, 0, 0),
            end_datetime=datetime(2026, 3, 22, 23, 59),
            is_all_day=True,
            user_id=1
        )
        
        # Act & Assert
        with pytest.raises(ConflictError) as exc_info:
            event_service.create(event_data)
        assert "conflicts with existing event" in str(exc_info.value)
    
    @patch('services.event.data.get_events_in_date_range')
    def test_create_event_conflict_partial_with_partial_overlap(self, mock_get_events):
        """Test creating a partial day event that overlaps with existing partial day event"""
        # Arrange
        from schemas.event import EventCreate
        
        existing_event = Event(
            id=1,
            name="Existing Event",
            place="Place",
            start_datetime=datetime(2026, 3, 22, 19, 0),
            end_datetime=datetime(2026, 3, 22, 23, 0),
            is_all_day=False,
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 1, 10, 0)
        )
        mock_get_events.return_value = [existing_event]
        
        # New event that overlaps: 18:00-22:00 overlaps with 19:00-23:00
        event_data = EventCreate(
            name="Overlapping Event",
            place="New Place",
            start_datetime=datetime(2026, 3, 22, 18, 0),
            end_datetime=datetime(2026, 3, 22, 22, 0),
            is_all_day=False,
            user_id=1
        )
        
        # Act & Assert
        with pytest.raises(ConflictError) as exc_info:
            event_service.create(event_data)
        assert "conflicts with existing event" in str(exc_info.value)
    
    @patch('services.event.data.get_events_in_date_range')
    def test_create_event_no_conflict_different_dates(self, mock_get_events):
        """Test creating event on different date doesn't conflict"""
        # Arrange
        from schemas.event import EventCreate
        
        # Existing event on a different date
        existing_event = Event(
            id=1,
            name="Existing Event",
            place="Place",
            start_datetime=datetime(2026, 3, 20, 19, 0),
            end_datetime=datetime(2026, 3, 20, 23, 0),
            is_all_day=False,
            user_id=1,
            status=EventStatus.PENDING,
            created_at=datetime(2026, 1, 1, 10, 0),
            updated_at=datetime(2026, 1, 1, 10, 0)
        )
        mock_get_events.return_value = [existing_event]
        
        event_data = EventCreate(
            name="New Event",
            place="New Place",
            start_datetime=datetime(2026, 3, 22, 19, 0),
            end_datetime=datetime(2026, 3, 22, 23, 0),
            is_all_day=False,
            user_id=1
        )
        
        # Mock the create function
        with patch('services.event.data.create') as mock_create:
            mock_event = Event(
                id=2,
                name="New Event",
                place="New Place",
                start_datetime=datetime(2026, 3, 22, 19, 0),
                end_datetime=datetime(2026, 3, 22, 23, 0),
                is_all_day=False,
                user_id=1,
                status=EventStatus.PENDING,
                created_at=datetime(2026, 1, 1, 10, 0),
                updated_at=datetime(2026, 1, 1, 10, 0)
            )
            mock_create.return_value = mock_event
            
            # Act & Assert - should not raise
            result = event_service.create(event_data)
            assert result is not None
    
    def test_create_event_end_before_start(self):
        """Test creating event with end datetime before start datetime raises error"""
        # Arrange
        from schemas.event import EventCreate
        
        event_data = EventCreate(
            name="Invalid Event",
            place="Place",
            start_datetime=datetime(2026, 3, 22, 23, 0),
            end_datetime=datetime(2026, 3, 22, 19, 0),  # End before start!
            is_all_day=False,
            user_id=1
        )
        
        # Act & Assert
        with pytest.raises(ConflictError) as exc_info:
            event_service.create(event_data)
        assert "End datetime must be after start datetime" in str(exc_info.value)
