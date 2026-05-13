import pytest
from datetime import date, datetime, timedelta
from fastapi import HTTPException
from schemas.musician_availability import (
    MusicianAvailabilityCreate,
    MusicianAvailabilityUpdate,
    MusicianAvailabilityResponse,
    MusicianAvailabilityMonthlyResponse
)
from web.musician_availability import (
    get_by_musician,
    get_musician_availability_by_month,
    check_availability,
    create_availability,
    create_bulk_availability,
    update_availability,
    delete_availability,
    delete_by_musician_and_date,
    get_all_by_date
)
from exceptions import NotFoundError, DatabaseError, ConflictError, UnauthorizedError, ValidationError


def test_get_by_musician_success(mocker):
    """Test get_by_musician() returns availability list for authorized user"""
    # Arrange
    musician_id = 1
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    mock_availabilities = [
        MusicianAvailabilityResponse(
            id=1, musician_id=1, unavailable_date=date.today() + timedelta(days=1),
            reason="Holiday", created_at=datetime.now(), updated_at=datetime.now()
        )
    ]
    mock_service = mocker.patch('web.musician_availability.service.get_by_musician')
    mock_service.return_value = mock_availabilities

    # Act
    result = get_by_musician(current_user=current_user, musician_id=musician_id)

    # Assert
    assert len(result) == 1
    assert result[0].musician_id == 1
    mock_service.assert_called_once_with(musician_id, current_user)


def test_get_by_musician_unauthorized(mocker):
    """Test get_by_musician() raises HTTPException for unauthorized access"""
    # Arrange
    musician_id = 2
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    mock_service = mocker.patch('web.musician_availability.service.get_by_musician')
    mock_service.side_effect = UnauthorizedError("You can only view your own availability")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_by_musician(current_user=current_user, musician_id=musician_id)

    assert exc_info.value.status_code == 403
    assert "You can only view your own availability" in exc_info.value.detail


def test_get_by_musician_database_error(mocker):
    """Test get_by_musician() handles database errors"""
    # Arrange
    musician_id = 1
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    mock_service = mocker.patch('web.musician_availability.service.get_by_musician')
    mock_service.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_by_musician(current_user=current_user, musician_id=musician_id)

    assert exc_info.value.status_code == 500
    assert "Internal server error" in exc_info.value.detail


def test_check_availability_success(mocker):
    """Test check_availability() returns boolean result"""
    # Arrange
    musician_id = 1
    check_date = date.today() + timedelta(days=1)
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    mock_service = mocker.patch('web.musician_availability.service.check_availability')
    mock_service.return_value = True

    # Act
    result = check_availability(current_user=current_user, musician_id=musician_id, check_date=check_date)

    # Assert
    assert result is True
    mock_service.assert_called_once_with(musician_id, check_date, current_user)


def test_check_availability_database_error(mocker):
    """Test check_availability() handles database errors"""
    # Arrange
    musician_id = 1
    check_date = date.today() + timedelta(days=1)
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    mock_service = mocker.patch('web.musician_availability.service.check_availability')
    mock_service.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        check_availability(current_user=current_user, musician_id=musician_id, check_date=check_date)

    assert exc_info.value.status_code == 500


def test_create_availability_success(mocker):
    """Test create_availability() creates and returns availability"""
    # Arrange
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )
    mock_response = MusicianAvailabilityResponse(
        id=1, musician_id=1, unavailable_date=availability_data.unavailable_date,
        reason="Holiday", created_at=datetime.now(), updated_at=datetime.now()
    )
    mock_service = mocker.patch('web.musician_availability.service.create')
    mock_service.return_value = mock_response

    # Act
    result = create_availability(current_user=current_user, availability_data=availability_data)

    # Assert
    assert result.id == 1
    assert result.musician_id == 1
    mock_service.assert_called_once_with(availability_data, current_user)


def test_create_availability_unauthorized(mocker):
    """Test create_availability() raises HTTPException for unauthorized access"""
    # Arrange
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    availability_data = MusicianAvailabilityCreate(
        musician_id=2,
        unavailable_date=date.today() + timedelta(days=1)
    )
    mock_service = mocker.patch('web.musician_availability.service.create')
    mock_service.side_effect = UnauthorizedError("You can only manage your own availability")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_availability(current_user=current_user, availability_data=availability_data)

    assert exc_info.value.status_code == 403


def test_create_availability_conflict(mocker):
    """Test create_availability() raises HTTPException for conflicts"""
    # Arrange
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1)
    )
    mock_service = mocker.patch('web.musician_availability.service.create')
    mock_service.side_effect = ConflictError("Availability already exists")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_availability(current_user=current_user, availability_data=availability_data)

    assert exc_info.value.status_code == 409


def test_create_availability_validation_error(mocker):
    """Test create_availability() raises HTTPException for service validation errors"""
    # Arrange
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1)
    )
    mock_service = mocker.patch('web.musician_availability.service.create')
    mock_service.side_effect = ValidationError("Invalid availability data")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_availability(current_user=current_user, availability_data=availability_data)

    assert exc_info.value.status_code == 400


def test_create_bulk_availability_success(mocker):
    """Test create_bulk_availability() creates multiple availabilities"""
    # Arrange
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    availabilities_data = [
        MusicianAvailabilityCreate(
            musician_id=1,
            unavailable_date=date.today() + timedelta(days=1),
            reason="Holiday"
        ),
        MusicianAvailabilityCreate(
            musician_id=1,
            unavailable_date=date.today() + timedelta(days=2),
            reason="Sick"
        )
    ]
    mock_responses = [
        MusicianAvailabilityResponse(
            id=i+1, musician_id=1, unavailable_date=av.unavailable_date,
            reason=av.reason, created_at=datetime.now(), updated_at=datetime.now()
        ) for i, av in enumerate(availabilities_data)
    ]
    mock_service = mocker.patch('web.musician_availability.service.create_bulk')
    mock_service.return_value = mock_responses

    # Act
    result = create_bulk_availability(current_user=current_user, availabilities_data=availabilities_data)

    # Assert
    assert len(result) == 2
    mock_service.assert_called_once_with(availabilities_data, current_user)


def test_update_availability_success(mocker):
    """Test update_availability() updates and returns availability"""
    # Arrange
    availability_id = 1
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    update_data = MusicianAvailabilityUpdate(reason="Updated reason")
    mock_response = MusicianAvailabilityResponse(
        id=1, musician_id=1, unavailable_date=date.today() + timedelta(days=1),
        reason="Updated reason", created_at=datetime.now(), updated_at=datetime.now()
    )
    mock_service = mocker.patch('web.musician_availability.service.update')
    mock_service.return_value = mock_response

    # Act
    result = update_availability(
        current_user=current_user,
        availability_id=availability_id,
        availability_data=update_data
    )

    # Assert
    assert result.reason == "Updated reason"
    mock_service.assert_called_once_with(availability_id, update_data, current_user)


def test_update_availability_not_found(mocker):
    """Test update_availability() raises HTTPException when not found"""
    # Arrange
    availability_id = 999
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    update_data = MusicianAvailabilityUpdate(reason="Updated reason")
    mock_service = mocker.patch('web.musician_availability.service.update')
    mock_service.side_effect = NotFoundError("Availability entry not found")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        update_availability(
            current_user=current_user,
            availability_id=availability_id,
            availability_data=update_data
        )

    assert exc_info.value.status_code == 404


def test_delete_availability_success(mocker):
    """Test delete_availability() returns success message"""
    # Arrange
    availability_id = 1
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    mock_service = mocker.patch('web.musician_availability.service.delete')
    mock_service.return_value = True

    # Act
    result = delete_availability(current_user=current_user, availability_id=availability_id)

    # Assert
    assert result == {"message": "Availability deleted successfully"}
    mock_service.assert_called_once_with(availability_id, current_user)


def test_delete_availability_not_found(mocker):
    """Test delete_availability() raises HTTPException when not found"""
    # Arrange
    availability_id = 999
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    mock_service = mocker.patch('web.musician_availability.service.delete')
    mock_service.return_value = False

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        delete_availability(current_user=current_user, availability_id=availability_id)

    assert exc_info.value.status_code == 404


def test_delete_by_musician_and_date_success(mocker):
    """Test delete_by_musician_and_date() returns success message"""
    # Arrange
    musician_id = 1
    delete_date = date.today() + timedelta(days=1)
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    mock_service = mocker.patch('web.musician_availability.service.delete_by_musician_and_date')
    mock_service.return_value = True

    # Act
    result = delete_by_musician_and_date(
        current_user=current_user,
        musician_id=musician_id,
        delete_date=delete_date
    )

    # Assert
    assert result == {"message": "Availability deleted successfully"}
    mock_service.assert_called_once_with(musician_id, delete_date, current_user)


def test_get_all_by_date_admin_success(mocker):
    """Test get_all_by_date() returns availability list for admin"""
    # Arrange
    check_date = date.today() + timedelta(days=1)
    current_user = {"id": 1, "role": "admin", "permissions": ["read:musician_availability", "write:musician_availability", "delete:musician_availability"]}
    mock_availabilities = [
        MusicianAvailabilityResponse(
            id=1, musician_id=1, unavailable_date=check_date,
            reason="Holiday", created_at=datetime.now(), updated_at=datetime.now()
        )
    ]
    mock_service = mocker.patch('web.musician_availability.service.get_all_by_date')
    mock_service.return_value = mock_availabilities

    # Act
    result = get_all_by_date(current_user=current_user, check_date=check_date)

    # Assert
    assert len(result) == 1
    mock_service.assert_called_once_with(check_date, current_user)


def test_get_all_by_date_admin_database_error(mocker):
    """Test get_all_by_date() handles database errors for admin"""
    # Arrange
    check_date = date.today() + timedelta(days=1)
    current_user = {"id": 1, "role": "admin", "permissions": ["read:musician_availability", "write:musician_availability", "delete:musician_availability"]}
    mock_service = mocker.patch('web.musician_availability.service.get_all_by_date')
    mock_service.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_all_by_date(current_user=current_user, check_date=check_date)

    assert exc_info.value.status_code == 500


def test_get_by_musician_all_roles_authorized_with_permission(mocker):
    """Test get_by_musician() allows all valid roles with proper permissions"""
    # Arrange
    musician_id = 1
    mock_availabilities = [
        MusicianAvailabilityResponse(
            id=1, musician_id=1, unavailable_date=date.today() + timedelta(days=1),
            reason="Holiday", created_at=datetime.now(), updated_at=datetime.now()
        )
    ]
    mock_service = mocker.patch('web.musician_availability.service.get_by_musician')
    mock_service.return_value = mock_availabilities

    # Test admin access
    admin_user = {"id": 1, "role": "admin", "permissions": ["read:musician_availability"]}
    result = get_by_musician(current_user=admin_user, musician_id=musician_id)
    assert len(result) == 1

    # Test musician access
    musician_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}
    result = get_by_musician(current_user=musician_user, musician_id=musician_id)
    assert len(result) == 1

    # Test auxiliar_musician access
    aux_musician_user = {"id": 1, "role": "auxiliar_musician", "permissions": ["read:musician_availability"]}
    result = get_by_musician(current_user=aux_musician_user, musician_id=musician_id)
    assert len(result) == 1


def test_create_availability_all_roles_can_write_with_permission(mocker):
    """Test create_availability() allows all valid roles to create with proper permissions"""
    # Arrange
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    mock_response = MusicianAvailabilityResponse(
        id=1, musician_id=1, unavailable_date=availability_data.unavailable_date,
        reason="Holiday", created_at=datetime.now(), updated_at=datetime.now()
    )

    mock_service = mocker.patch('web.musician_availability.service.create')
    mock_service.return_value = mock_response

    # Test admin can create
    admin_user = {"id": 1, "role": "admin", "permissions": ["write:musician_availability"]}
    result = create_availability(current_user=admin_user, availability_data=availability_data)
    assert result.id == 1

    # Test musician can create
    musician_user = {"id": 1, "role": "musician", "permissions": ["write:musician_availability"]}
    result = create_availability(current_user=musician_user, availability_data=availability_data)
    assert result.id == 1

    # Test auxiliar_musician can create
    aux_musician_user = {"id": 1, "role": "auxiliar_musician", "permissions": ["write:musician_availability"]}
    result = create_availability(current_user=aux_musician_user, availability_data=availability_data)
    assert result.id == 1


def test_create_availability_denies_wrong_role(mocker):
    """Test create_availability() denies access for invalid roles"""
    # Arrange
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    # Test user role denied
    user_with_permission = {"id": 1, "role": "user", "permissions": ["write:musician_availability"]}

    # Mock the service to simulate authorization failure
    mock_service = mocker.patch('web.musician_availability.service.create')
    mock_service.side_effect = UnauthorizedError("Access denied. Required role")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_availability(current_user=user_with_permission, availability_data=availability_data)

    assert exc_info.value.status_code == 403
    assert "Access denied. Required role" in exc_info.value.detail


def test_create_availability_denies_missing_permission(mocker):
    """Test create_availability() denies access when permission is missing"""
    # Arrange
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    # Test admin without permission
    admin_without_permission = {"id": 1, "role": "admin", "permissions": []}

    # Mock the service to simulate permission failure
    mock_service = mocker.patch('web.musician_availability.service.create')
    mock_service.side_effect = UnauthorizedError("Missing required permission")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_availability(current_user=admin_without_permission, availability_data=availability_data)

    assert exc_info.value.status_code == 403
    assert "Missing required permission" in exc_info.value.detail


def test_get_musician_availability_by_month_success(mocker):
    """Test get_musician_availability_by_month() returns monthly availability"""
    # Arrange
    musician_id = 1
    year = 2024
    month = 5
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}

    from schemas.musician_availability import MusicianAvailabilityMonthlyItem

    mock_response = MusicianAvailabilityMonthlyResponse(
        musician_id=musician_id,
        year=year,
        month=month,
        unavailable_dates=[
            MusicianAvailabilityMonthlyItem(id=1, unavailable_date=date(2026, 5, 15), reason="Holiday"),
            MusicianAvailabilityMonthlyItem(id=2, unavailable_date=date(2026, 5, 20), reason="Sick")
        ]
    )
    mock_service = mocker.patch('web.musician_availability.service.get_musician_availability_by_month')
    mock_service.return_value = mock_response

    # Act
    result = get_musician_availability_by_month(
        current_user=current_user,
        musician_id=musician_id,
        year=year,
        month=month
    )

    # Assert
    assert result.musician_id == musician_id
    assert result.year == year
    assert result.month == month
    assert len(result.unavailable_dates) == 2
    mock_service.assert_called_once_with(musician_id, year, month, current_user)


def test_get_musician_availability_by_month_unauthorized(mocker):
    """Test get_musician_availability_by_month() raises HTTPException for unauthorized access"""
    # Arrange
    musician_id = 2  # Different musician
    year = 2024
    month = 5
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}

    mock_service = mocker.patch('web.musician_availability.service.get_musician_availability_by_month')
    mock_service.side_effect = UnauthorizedError("You can only view your own availability")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_musician_availability_by_month(
            current_user=current_user,
            musician_id=musician_id,
            year=year,
            month=month
        )

    assert exc_info.value.status_code == 403
    assert "You can only view your own availability" in exc_info.value.detail


def test_get_musician_availability_by_month_validation_error(mocker):
    """Test get_musician_availability_by_month() raises HTTPException for validation errors"""
    # Arrange
    musician_id = 1
    year = 2024
    month = 13  # Invalid month
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}

    mock_service = mocker.patch('web.musician_availability.service.get_musician_availability_by_month')
    mock_service.side_effect = ValidationError("Month must be between 1 and 12")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_musician_availability_by_month(
            current_user=current_user,
            musician_id=musician_id,
            year=year,
            month=month
        )

    assert exc_info.value.status_code == 400
    assert "Month must be between 1 and 12" in exc_info.value.detail


def test_get_musician_availability_by_month_database_error(mocker):
    """Test get_musician_availability_by_month() raises HTTPException for database errors"""
    # Arrange
    musician_id = 1
    year = 2024
    month = 5
    current_user = {"id": 1, "role": "musician", "permissions": ["read:musician_availability"]}

    mock_service = mocker.patch('web.musician_availability.service.get_musician_availability_by_month')
    mock_service.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_musician_availability_by_month(
            current_user=current_user,
            musician_id=musician_id,
            year=year,
            month=month
        )

    assert exc_info.value.status_code == 500