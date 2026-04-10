import pytest
from decimal import Decimal
from unittest.mock import Mock
from services.event_musician import (
    get_by_event,
    get_by_musician,
    assign_musician,
    update_assignment,
    remove_musician,
    get_musicians_summary,
)
from schemas.event_musician import (
    EventMusicianCreate,
    EventMusicianUpdate,
)
from models.event_musician import EventMusician, PaymentStatus
from models.event import Event
from exceptions import (
    NotFoundError,
    DatabaseError,
    ConflictError,
    UnauthorizedError,
    ValidationError,
)


def test_get_by_event_success(mocker):
    """Test get_by_event() returns musicians for event owner"""
    # Arrange
    event_id = 1
    current_user = {'id': 1, 'role': 'user'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musicians = [
        EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING"),
        EventMusician(id=2, event_id=1, musician_id=3, role="Drummer", salary=Decimal("1200.00"), payment_status="COMPLETED")
    ]
    mock_data_get = mocker.patch('services.event_musician.data.get_by_event')
    mock_data_get.return_value = mock_musicians

    # Act
    result = get_by_event(event_id, current_user)

    # Assert
    assert len(result) == 2
    mock_event_data_get.assert_called_once_with(event_id)
    mock_data_get.assert_called_once_with(event_id)


def test_get_by_event_admin_access(mocker):
    """Test get_by_event() allows admin to view any event's musicians"""
    # Arrange
    event_id = 1
    current_user = {'id': 2, 'role': 'admin'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1  # Different user
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musicians = [EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING")]
    mock_data_get = mocker.patch('services.event_musician.data.get_by_event')
    mock_data_get.return_value = mock_musicians

    # Act
    result = get_by_event(event_id, current_user)

    # Assert
    assert len(result) == 1
    mock_data_get.assert_called_once_with(event_id)


def test_get_by_event_unauthorized(mocker):
    """Test get_by_event() raises UnauthorizedError for non-owner user"""
    # Arrange
    event_id = 1
    current_user = {'id': 2, 'role': 'user'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1  # Different user
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_by_event(event_id, current_user)

    assert "You can only manage musicians for your own events" in str(exc_info.value)


def test_get_by_event_not_found(mocker):
    """Test get_by_event() raises NotFoundError when event doesn't exist"""
    # Arrange
    event_id = 999
    current_user = {'id': 1, 'role': 'user'}

    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        get_by_event(event_id, current_user)

    assert "Event with id 999 not found" in str(exc_info.value)


def test_get_by_musician_success(mocker):
    """Test get_by_musician() returns events for musician"""
    # Arrange
    musician_id = 2
    current_user = {'id': 2, 'role': 'musician'}

    mock_assignments = [
        EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING"),
        EventMusician(id=3, event_id=2, musician_id=2, role="Bassist", salary=Decimal("1300.00"), payment_status="COMPLETED")
    ]
    mock_data_get = mocker.patch('services.event_musician.data.get_by_musician')
    mock_data_get.return_value = mock_assignments

    # Act
    result = get_by_musician(musician_id, current_user)

    # Assert
    assert len(result) == 2
    mock_data_get.assert_called_once_with(musician_id)


def test_get_by_musician_admin_access(mocker):
    """Test get_by_musician() allows admin to view any musician's assignments"""
    # Arrange
    musician_id = 2
    current_user = {'id': 1, 'role': 'admin'}

    mock_assignments = [EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING")]
    mock_data_get = mocker.patch('services.event_musician.data.get_by_musician')
    mock_data_get.return_value = mock_assignments

    # Act
    result = get_by_musician(musician_id, current_user)

    # Assert
    assert len(result) == 1
    mock_data_get.assert_called_once_with(musician_id)


def test_get_by_musician_unauthorized(mocker):
    """Test get_by_musician() raises UnauthorizedError for non-owner musician"""
    # Arrange
    musician_id = 2
    current_user = {'id': 1, 'role': 'musician'}

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_by_musician(musician_id, current_user)

    assert "You can only view your own event assignments" in str(exc_info.value)


def test_assign_musician_success(mocker):
    """Test assign_musician() creates assignment with availability check"""
    # Arrange
    current_user = {'id': 1, 'role': 'user'}
    assignment_data = EventMusicianCreate(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status=PaymentStatus.PENDING
    )

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = Mock()  # Mock datetime
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.event_musician.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_data_is_assigned = mocker.patch('services.event_musician.data.is_assigned_to_event')
    mock_data_is_assigned.return_value = False

    mock_availability_check = mocker.patch('services.event_musician.musician_availability_data.check_availability')
    mock_availability_check.return_value = True

    mock_assignment = EventMusician(
        id=1,
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status="PENDING"
    )
    mock_data_create = mocker.patch('services.event_musician.data.create')
    mock_data_create.return_value = mock_assignment

    # Act
    result = assign_musician(assignment_data, current_user)

    # Assert
    assert result.id == 1
    mock_event_data_get.assert_called_once_with(1)
    mock_user_data_get.assert_called_once_with(2)
    mock_data_is_assigned.assert_called_once_with(1, 2)
    mock_availability_check.assert_called_once()
    mock_data_create.assert_called_once()


def test_assign_musician_unauthorized_event(mocker):
    """Test assign_musician() raises UnauthorizedError for non-owner event"""
    # Arrange
    current_user = {'id': 2, 'role': 'user'}
    assignment_data = EventMusicianCreate(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00")
    )

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1  # Different user
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        assign_musician(assignment_data, current_user)

    assert "You can only manage musicians for your own events" in str(exc_info.value)


def test_assign_musician_event_not_found(mocker):
    """Test assign_musician() raises NotFoundError when event doesn't exist"""
    # Arrange
    current_user = {'id': 1, 'role': 'user'}
    assignment_data = EventMusicianCreate(
        event_id=999,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00")
    )

    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        assign_musician(assignment_data, current_user)

    assert "Event with id 999 not found" in str(exc_info.value)


def test_assign_musician_musician_not_found(mocker):
    """Test assign_musician() raises NotFoundError when musician doesn't exist"""
    # Arrange
    current_user = {'id': 1, 'role': 'user'}
    assignment_data = EventMusicianCreate(
        event_id=1,
        musician_id=999,
        role="Lead Guitarist",
        salary=Decimal("1500.00")
    )

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_user_data_get = mocker.patch('services.event_musician.user_data.get_one_by_id')
    mock_user_data_get.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        assign_musician(assignment_data, current_user)

    assert "Musician with id 999 not found" in str(exc_info.value)


def test_assign_musician_already_assigned(mocker):
    """Test assign_musician() raises ConflictError when musician already assigned"""
    # Arrange
    current_user = {'id': 1, 'role': 'user'}
    assignment_data = EventMusicianCreate(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00")
    )

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.event_musician.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_data_is_assigned = mocker.patch('services.event_musician.data.is_assigned_to_event')
    mock_data_is_assigned.return_value = True

    # Act & Assert
    with pytest.raises(ConflictError) as exc_info:
        assign_musician(assignment_data, current_user)

    assert "Musician is already assigned to this event" in str(exc_info.value)


def test_assign_musician_unavailable(mocker):
    """Test assign_musician() raises ConflictError when musician is unavailable"""
    # Arrange
    current_user = {'id': 1, 'role': 'user'}
    assignment_data = EventMusicianCreate(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00")
    )

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = Mock()
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.event_musician.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_data_is_assigned = mocker.patch('services.event_musician.data.is_assigned_to_event')
    mock_data_is_assigned.return_value = False

    mock_availability_check = mocker.patch('services.event_musician.musician_availability_data.check_availability')
    mock_availability_check.return_value = False

    # Act & Assert
    with pytest.raises(ConflictError) as exc_info:
        assign_musician(assignment_data, current_user)

    assert "Musician is not available on the event date" in str(exc_info.value)


def test_update_assignment_success(mocker):
    """Test update_assignment() updates assignment"""
    # Arrange
    assignment_id = 1
    current_user = {'id': 1, 'role': 'user'}
    update_data = EventMusicianUpdate(role="Solo Guitarist", salary=Decimal("1600.00"))

    mock_assignment = EventMusician(
        id=1,
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status="PENDING"
    )
    mock_data_get = mocker.patch('services.event_musician.data.get_by_id')
    mock_data_get.return_value = mock_assignment

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    updated_assignment = EventMusician(
        id=1,
        event_id=1,
        musician_id=2,
        role="Solo Guitarist",
        salary=Decimal("1600.00"),
        payment_status="PENDING"
    )
    mock_data_update = mocker.patch('services.event_musician.data.update')
    mock_data_update.return_value = updated_assignment

    # Act
    result = update_assignment(assignment_id, update_data, current_user)

    # Assert
    assert result.role == "Solo Guitarist"
    assert result.salary == Decimal("1600.00")
    mock_data_update.assert_called_once()


def test_remove_musician_success(mocker):
    """Test remove_musician() deletes assignment"""
    # Arrange
    assignment_id = 1
    current_user = {'id': 1, 'role': 'user'}

    mock_assignment = EventMusician(
        id=1,
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status="PENDING"
    )
    mock_data_get = mocker.patch('services.event_musician.data.get_by_id')
    mock_data_get.return_value = mock_assignment

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_data_delete = mocker.patch('services.event_musician.data.delete')
    mock_data_delete.return_value = True

    # Act
    result = remove_musician(assignment_id, current_user)

    # Assert
    assert result is True
    mock_data_delete.assert_called_once_with(assignment_id)


def test_get_musicians_summary_success(mocker):
    """Test get_musicians_summary() returns summary for event"""
    # Arrange
    event_id = 1
    current_user = {'id': 1, 'role': 'user'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.event_musician.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musicians = [
        EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING"),
        EventMusician(id=2, event_id=1, musician_id=3, role="Drummer", salary=Decimal("1200.00"), payment_status="COMPLETED")
    ]
    mock_data_get = mocker.patch('services.event_musician.data.get_by_event')
    mock_data_get.return_value = mock_musicians

    # Act
    result = get_musicians_summary(event_id, current_user)

    # Assert
    assert result['total_musicians'] == 2
    assert result['total_salary'] == Decimal("2700.00")
    mock_data_get.assert_called_once_with(event_id)