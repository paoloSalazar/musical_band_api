import pytest
from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException
from schemas.event_musician import (
    EventMusicianCreate,
    EventMusicianUpdate,
    EventMusicianResponse,
    MusicianSummaryResponse,
    PaymentStatus,
)
from web.event_musician import (
    get_event_musicians,
    assign_musician_to_event,
    update_event_musician,
    get_musician_assignments,
    remove_musician_from_event,
    get_event_musicians_summary,
)
from exceptions import NotFoundError, DatabaseError, ConflictError, UnauthorizedError, ValidationError


def test_get_event_musicians_success(mocker):
    """Test get_event_musicians() returns musicians for event"""
    # Arrange
    event_id = 1
    current_user = {"id": 1, "role": "user"}
    mock_musicians = [
        EventMusicianResponse(
            id=1, event_id=1, musician_id=2, role="Lead Guitarist",
            salary=Decimal("1500.00"), payment_status=PaymentStatus.PENDING,
            musician_name="John", musician_lastname="Doe",
            created_at=datetime.now(), updated_at=datetime.now()
        )
    ]
    mock_service = mocker.patch('web.event_musician.service.get_by_event')
    mock_service.return_value = mock_musicians

    # Act
    result = get_event_musicians(current_user=current_user, event_id=event_id)

    # Assert
    assert len(result) == 1
    assert result[0].event_id == 1
    mock_service.assert_called_once_with(event_id, current_user)


def test_get_event_musicians_unauthorized(mocker):
    """Test get_event_musicians() raises HTTPException for unauthorized access"""
    # Arrange
    event_id = 1
    current_user = {"id": 2, "role": "user"}
    mock_service = mocker.patch('web.event_musician.service.get_by_event')
    mock_service.side_effect = UnauthorizedError("You can only manage musicians for your own events")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_event_musicians(current_user=current_user, event_id=event_id)

    assert exc_info.value.status_code == 403
    assert "You can only manage musicians for your own events" in exc_info.value.detail


def test_get_event_musicians_not_found(mocker):
    """Test get_event_musicians() raises HTTPException when event not found"""
    # Arrange
    event_id = 999
    current_user = {"id": 1, "role": "user"}
    mock_service = mocker.patch('web.event_musician.service.get_by_event')
    mock_service.side_effect = NotFoundError("Event with id 999 not found")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_event_musicians(current_user=current_user, event_id=event_id)

    assert exc_info.value.status_code == 404
    assert "Event with id 999 not found" in exc_info.value.detail


def test_get_musician_assignments_success(mocker):
    """Test get_musician_assignments() returns assignments for musician"""
    # Arrange
    musician_id = 2
    current_user = {"id": 2, "role": "musician"}
    mock_assignments = [
        EventMusicianResponse(
            id=1, event_id=1, musician_id=2, role="Lead Guitarist",
            salary=Decimal("1500.00"), payment_status=PaymentStatus.PENDING,
            musician_name="Jane", musician_lastname="Smith",
            created_at=datetime.now(), updated_at=datetime.now()
        )
    ]
    mock_service = mocker.patch('web.event_musician.service.get_by_musician')
    mock_service.return_value = mock_assignments

    # Act
    result = get_musician_assignments(current_user=current_user, musician_id=musician_id)

    # Assert
    assert len(result) == 1
    assert result[0].musician_id == 2
    mock_service.assert_called_once_with(musician_id, current_user)


def test_assign_musician_to_event_success(mocker):
    """Test assign_musician_to_event() creates assignment"""
    # Arrange
    event_id = 1
    current_user = {"id": 1, "role": "user"}
    assignment_data = EventMusicianCreate(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status=PaymentStatus.PENDING
    )
    mock_response = EventMusicianResponse(
        id=1, event_id=1, musician_id=2, role="Lead Guitarist",
        salary=Decimal("1500.00"), payment_status=PaymentStatus.PENDING,
        musician_name="John", musician_lastname="Doe",
        created_at=datetime.now(), updated_at=datetime.now()
    )
    mock_service = mocker.patch('web.event_musician.service.assign_musician')
    mock_service.return_value = mock_response

    # Act
    result = assign_musician_to_event(
        current_user=current_user,
        event_id=event_id,
        musician_data=assignment_data
    )

    # Assert
    assert result.id == 1
    assert result.event_id == 1
    mock_service.assert_called_once_with(assignment_data, current_user)


def test_assign_musician_to_event_conflict(mocker):
    """Test assign_musician_to_event() raises HTTPException for conflicts"""
    # Arrange
    event_id = 1
    current_user = {"id": 1, "role": "user"}
    assignment_data = EventMusicianCreate(
        event_id=1,
        musician_id=2,
        salary=Decimal("1500.00")
    )
    mock_service = mocker.patch('web.event_musician.service.assign_musician')
    mock_service.side_effect = ConflictError("Musician is already assigned to this event")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        assign_musician_to_event(
            current_user=current_user,
            event_id=event_id,
            musician_data=assignment_data
        )

    assert exc_info.value.status_code == 409
    assert "Musician is already assigned to this event" in exc_info.value.detail


def test_update_event_musician_success(mocker):
    """Test update_event_musician() updates assignment"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "user"}
    update_data = EventMusicianUpdate(role="Solo Guitarist", salary=Decimal("1600.00"))
    mock_response = EventMusicianResponse(
        id=1, event_id=1, musician_id=2, role="Solo Guitarist",
        salary=Decimal("1600.00"), payment_status=PaymentStatus.PENDING,
        musician_name="John", musician_lastname="Doe",
        created_at=datetime.now(), updated_at=datetime.now()
    )
    mock_service = mocker.patch('web.event_musician.service.update_assignment_by_event_musician')
    mock_service.return_value = mock_response

    # Act
    result = update_event_musician(
        current_user=current_user,
        event_id=event_id,
        musician_id=musician_id,
        musician_data=update_data
    )

    # Assert
    assert result.role == "Solo Guitarist"
    assert result.salary == Decimal("1600.00")
    mock_service.assert_called_once()


def test_update_event_musician_not_found(mocker):
    """Test update_event_musician() raises HTTPException when not found"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "user"}
    update_data = EventMusicianUpdate(role="Updated role")
    mock_service = mocker.patch('web.event_musician.service.update_assignment_by_event_musician')
    mock_service.side_effect = NotFoundError("Assignment not found")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        update_event_musician(
            current_user=current_user,
            event_id=event_id,
            musician_id=musician_id,
            musician_data=update_data
        )

    assert exc_info.value.status_code == 404


def test_remove_musician_from_event_success(mocker):
    """Test remove_musician_from_event() returns success message"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "user"}
    mock_service = mocker.patch('web.event_musician.service.remove_musician_by_event_musician')
    mock_service.return_value = True

    # Act
    result = remove_musician_from_event(
        current_user=current_user,
        event_id=event_id,
        musician_id=musician_id
    )

    # Assert
    assert result == {"message": "Musician removed from event successfully"}
    mock_service.assert_called_once()


def test_remove_musician_from_event_not_found(mocker):
    """Test remove_musician_from_event() raises HTTPException when not found"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "user"}
    mock_service = mocker.patch('web.event_musician.service.remove_musician_by_event_musician')
    mock_service.side_effect = NotFoundError("Assignment not found")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        remove_musician_from_event(
            current_user=current_user,
            event_id=event_id,
            musician_id=musician_id
        )

    assert exc_info.value.status_code == 404


def test_get_event_musicians_summary_success(mocker):
    """Test get_event_musicians_summary() returns summary"""
    # Arrange
    event_id = 1
    current_user = {"id": 1, "role": "user"}
    mock_summary = {
        "total_musicians": 2,
        "total_salary": Decimal("2700.00"),
        "musicians": []
    }
    mock_service = mocker.patch('web.event_musician.service.get_musicians_summary')
    mock_service.return_value = mock_summary

    # Act
    result = get_event_musicians_summary(current_user=current_user, event_id=event_id)

    # Assert
    assert result["total_musicians"] == 2
    assert result["total_salary"] == Decimal("2700.00")
    mock_service.assert_called_once_with(event_id, current_user)


def test_database_error_handling(mocker):
    """Test that database errors are properly handled"""
    # Arrange
    event_id = 1
    current_user = {"id": 1, "role": "user"}
    mock_service = mocker.patch('web.event_musician.service.get_by_event')
    mock_service.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_event_musicians(current_user=current_user, event_id=event_id)

    assert exc_info.value.status_code == 500
    assert "Internal server error" in exc_info.value.detail