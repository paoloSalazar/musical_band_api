import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock
from services.musician_availability import (
    get_by_musician,
    get_musician_availability_by_month,
    get_all_by_date,
    check_availability,
    create,
    create_bulk,
    update,
    delete,
    delete_by_musician_and_date,
)
from schemas.musician_availability import (
    MusicianAvailabilityCreate,
    MusicianAvailabilityUpdate,
)
from models.musician_availability import MusicianAvailability
from exceptions import (
    NotFoundError,
    DatabaseError,
    ConflictError,
    UnauthorizedError,
    ValidationError,
)


def test_get_by_musician_success(mocker):
    """Test get_by_musician() returns availability list for authorized user (covers musician, auxiliar_musician, helper roles via generic non-admin check)"""
    # Arrange
    musician_id = 1
    current_user = {'id': 1, 'role': 'musician'}

    mock_availabilities = [
        MusicianAvailability(id=1, musician_id=1, unavailable_date=date.today() + timedelta(days=1), reason="Holiday", created_at=datetime.now(), updated_at=datetime.now()),
        MusicianAvailability(id=2, musician_id=1, unavailable_date=date.today() + timedelta(days=2), reason="Sick", created_at=datetime.now(), updated_at=datetime.now())
    ]
    mock_data_get = mocker.patch('services.musician_availability.data.get_by_musician')
    mock_data_get.return_value = mock_availabilities

    # Act
    result = get_by_musician(musician_id, current_user)

    # Assert
    assert len(result) == 2
    assert result[0].musician_id == 1
    mock_data_get.assert_called_once_with(musician_id)


def test_get_by_musician_admin_access(mocker):
    """Test get_by_musician() allows admin to view any musician's availability"""
    # Arrange
    musician_id = 2
    current_user = {'id': 1, 'role': 'admin'}

    mock_availabilities = [
        MusicianAvailability(id=1, musician_id=2, unavailable_date=date.today() + timedelta(days=1), reason="Holiday", created_at=datetime.now(), updated_at=datetime.now())
    ]
    mock_data_get = mocker.patch('services.musician_availability.data.get_by_musician')
    mock_data_get.return_value = mock_availabilities

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

    assert "You can only view your own availability" in str(exc_info.value)


def test_get_all_by_date_admin_success(mocker):
    """Test get_all_by_date() returns availability list for admin"""
    # Arrange
    check_date = date.today() + timedelta(days=1)
    current_user = {'id': 1, 'role': 'admin'}

    mock_availabilities = [
        MusicianAvailability(id=1, musician_id=1, unavailable_date=check_date, reason="Holiday", created_at=datetime.now(), updated_at=datetime.now()),
        MusicianAvailability(id=2, musician_id=2, unavailable_date=check_date, reason="Sick", created_at=datetime.now(), updated_at=datetime.now())
    ]
    mock_data_get = mocker.patch('services.musician_availability.data.get_all_by_date')
    mock_data_get.return_value = mock_availabilities

    # Act
    result = get_all_by_date(check_date, current_user)

    # Assert
    assert len(result) == 2
    mock_data_get.assert_called_once_with(check_date)


def test_get_all_by_date_unauthorized(mocker):
    """Test get_all_by_date() raises UnauthorizedError for non-admin"""
    # Arrange
    check_date = date.today() + timedelta(days=1)
    current_user = {'id': 1, 'role': 'musician'}

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_all_by_date(check_date, current_user)

    assert "Only administrators can view all musicians' availability" in str(exc_info.value)


def test_check_availability_available(mocker):
    """Test check_availability() returns True when musician is available"""
    # Arrange
    musician_id = 1
    check_date = date.today() + timedelta(days=1)
    current_user = {'id': 1, 'role': 'musician'}

    mock_data_check = mocker.patch('services.musician_availability.data.check_availability')
    mock_data_check.return_value = True

    # Act
    result = check_availability(musician_id, check_date, current_user)

    # Assert
    assert result is True
    mock_data_check.assert_called_once_with(musician_id, check_date)


def test_check_availability_unavailable(mocker):
    """Test check_availability() returns False when musician is unavailable"""
    # Arrange
    musician_id = 1
    check_date = date.today() + timedelta(days=1)
    current_user = {'id': 1, 'role': 'musician'}

    mock_data_check = mocker.patch('services.musician_availability.data.check_availability')
    mock_data_check.return_value = False

    # Act
    result = check_availability(musician_id, check_date, current_user)

    # Assert
    assert result is False
    mock_data_check.assert_called_once_with(musician_id, check_date)


def test_create_success(mocker):
    """Test create() creates availability for authorized user"""
    # Arrange
    current_user = {'id': 1, 'role': 'musician'}
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    mock_musician = Mock()
    mock_musician.id = 1
    mock_user_data_get = mocker.patch('services.musician_availability.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_data_get_existing = mocker.patch('services.musician_availability.data.get_by_musician_and_date')
    mock_data_get_existing.return_value = None

    mock_availability = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=availability_data.unavailable_date,
        reason="Holiday",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_data_create = mocker.patch('services.musician_availability.data.create')
    mock_data_create.return_value = mock_availability

    # Act
    result = create(availability_data, current_user)

    # Assert
    assert result.id == 1
    assert result.musician_id == 1
    mock_user_data_get.assert_called_once_with(1)
    mock_data_get_existing.assert_called_once()
    mock_data_create.assert_called_once()


def test_create_admin_for_other(mocker):
    """Test create() allows admin to create availability for other musicians"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    availability_data = MusicianAvailabilityCreate(
        musician_id=2,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_availability.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_data_get_existing = mocker.patch('services.musician_availability.data.get_by_musician_and_date')
    mock_data_get_existing.return_value = None

    mock_availability = MusicianAvailability(
        id=1,
        musician_id=2,
        unavailable_date=availability_data.unavailable_date,
        reason="Holiday",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_data_create = mocker.patch('services.musician_availability.data.create')
    mock_data_create.return_value = mock_availability

    # Act
    result = create(availability_data, current_user)

    # Assert
    assert result.musician_id == 2
    mock_data_create.assert_called_once()


def test_create_unauthorized(mocker):
    """Test create() raises UnauthorizedError for non-owner musician"""
    # Arrange
    current_user = {'id': 1, 'role': 'musician'}
    availability_data = MusicianAvailabilityCreate(
        musician_id=2,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        create(availability_data, current_user)

    assert "You can only manage your own availability" in str(exc_info.value)


def test_create_musician_not_found(mocker):
    """Test create() raises NotFoundError when musician doesn't exist"""
    # Arrange
    current_user = {'id': 1, 'role': 'musician'}
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    mock_user_data_get = mocker.patch('services.musician_availability.user_data.get_one_by_id')
    mock_user_data_get.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        create(availability_data, current_user)

    assert "Musician with id 1 not found" in str(exc_info.value)


def test_create_conflict(mocker):
    """Test create() raises ConflictError when availability already exists"""
    # Arrange
    current_user = {'id': 1, 'role': 'musician'}
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    mock_musician = Mock()
    mock_musician.id = 1
    mock_user_data_get = mocker.patch('services.musician_availability.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_existing = MusicianAvailability(id=1, musician_id=1, unavailable_date=availability_data.unavailable_date)
    mock_data_get_existing = mocker.patch('services.musician_availability.data.get_by_musician_and_date')
    mock_data_get_existing.return_value = mock_existing

    # Act & Assert
    with pytest.raises(ConflictError) as exc_info:
        create(availability_data, current_user)

    assert "Availability already exists" in str(exc_info.value)


def test_create_event_assignment_conflict(mocker):
    """Test create() raises ConflictError when musician assigned to event on that date (includes event name)"""
    # Arrange
    current_user = {'id': 1, 'role': 'musician'}
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    mock_musician = Mock()
    mock_musician.id = 1
    mock_user_data_get = mocker.patch('services.musician_availability.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_data_get_existing = mocker.patch('services.musician_availability.data.get_by_musician_and_date')
    mock_data_get_existing.return_value = None

    mock_check_assignment = mocker.patch('services.musician_availability.data.check_musician_event_assignment')
    mock_check_assignment.return_value = "Wedding Gig"

    # Act & Assert
    with pytest.raises(ConflictError) as exc_info:
        create(availability_data, current_user)

    assert "assigned to event 'Wedding Gig'" in str(exc_info.value)


def test_create_bulk_success(mocker):
    """Test create_bulk() creates multiple availabilities"""
    # Arrange
    current_user = {'id': 1, 'role': 'musician'}
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

    mock_musician = Mock()
    mock_musician.id = 1
    mock_user_data_get = mocker.patch('services.musician_availability.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_data_get_existing = mocker.patch('services.musician_availability.data.get_by_musician_and_date')
    mock_data_get_existing.return_value = None

    mock_availabilities = [
        MusicianAvailability(id=i+1, musician_id=1, unavailable_date=av.unavailable_date, reason=av.reason, created_at=datetime.now(), updated_at=datetime.now())
        for i, av in enumerate(availabilities_data)
    ]
    mock_data_create_bulk = mocker.patch('services.musician_availability.data.create_bulk')
    mock_data_create_bulk.return_value = mock_availabilities

    # Act
    result = create_bulk(availabilities_data, current_user)

    # Assert
    assert len(result) == 2
    mock_data_create_bulk.assert_called_once()


def test_create_bulk_mixed_musicians(mocker):
    """Test create_bulk() raises ValidationError for mixed musicians"""
    # Arrange
    current_user = {'id': 1, 'role': 'musician'}
    availabilities_data = [
        MusicianAvailabilityCreate(musician_id=1, unavailable_date=date.today() + timedelta(days=1)),
        MusicianAvailabilityCreate(musician_id=2, unavailable_date=date.today() + timedelta(days=2))
    ]

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        create_bulk(availabilities_data, current_user)

    assert "All availability entries must be for the same musician" in str(exc_info.value)


def test_create_past_date_validation(mocker):
    """Test create() raises ValidationError for past unavailable_date"""
    # Arrange
    current_user = {'id': 1, 'role': 'musician'}
    availability_data = MusicianAvailabilityCreate(
        musician_id=1,
        unavailable_date=date.today() - timedelta(days=1),  # Past date
        reason="Holiday"
    )

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        create(availability_data, current_user)

    assert "Unavailable date cannot be in the past" in str(exc_info.value)


def test_create_bulk_past_date_validation(mocker):
    """Test create_bulk() raises ValidationError when any date is in the past"""
    # Arrange
    current_user = {'id': 1, 'role': 'musician'}
    availabilities_data = [
        MusicianAvailabilityCreate(
            musician_id=1,
            unavailable_date=date.today() + timedelta(days=1),  # Future date
            reason="Holiday"
        ),
        MusicianAvailabilityCreate(
            musician_id=1,
            unavailable_date=date.today() - timedelta(days=1),  # Past date
            reason="Sick"
        )
    ]

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        create_bulk(availabilities_data, current_user)

    assert "Unavailable date cannot be in the past" in str(exc_info.value)


def test_update_past_date_validation(mocker):
    """Test update() raises ValidationError when setting past unavailable_date"""
    # Arrange
    availability_id = 1
    current_user = {'id': 1, 'role': 'musician'}
    update_data = MusicianAvailabilityUpdate(
        unavailable_date=date.today() - timedelta(days=1)  # Past date
    )

    existing_availability = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_data_get = mocker.patch('services.musician_availability.data.get_by_id')
    mock_data_get.return_value = existing_availability

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        update(availability_id, update_data, current_user)

    assert "Unavailable date cannot be in the past" in str(exc_info.value)


def test_update_success(mocker):
    """Test update() updates availability for authorized user"""
    # Arrange
    availability_id = 1
    current_user = {'id': 1, 'role': 'musician'}
    update_data = MusicianAvailabilityUpdate(reason="Updated reason")

    existing_availability = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_data_get = mocker.patch('services.musician_availability.data.get_by_id')
    mock_data_get.return_value = existing_availability

    updated_availability = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Updated reason",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_data_update = mocker.patch('services.musician_availability.data.update')
    mock_data_update.return_value = updated_availability

    # Act
    result = update(availability_id, update_data, current_user)

    # Assert
    assert result.id == 1
    mock_data_update.assert_called_once()


def test_update_unauthorized(mocker):
    """Test update() raises UnauthorizedError for non-owner musician"""
    # Arrange
    availability_id = 1
    current_user = {'id': 1, 'role': 'musician'}
    update_data = MusicianAvailabilityUpdate(reason="Updated reason")

    existing_availability = MusicianAvailability(
        id=1,
        musician_id=2,  # Different musician
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_data_get = mocker.patch('services.musician_availability.data.get_by_id')
    mock_data_get.return_value = existing_availability

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        update(availability_id, update_data, current_user)

    assert "You can only manage your own availability" in str(exc_info.value)


def test_delete_success(mocker):
    """Test delete() deletes availability for authorized user"""
    # Arrange
    availability_id = 1
    current_user = {'id': 1, 'role': 'musician'}

    existing_availability = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_data_get = mocker.patch('services.musician_availability.data.get_by_id')
    mock_data_get.return_value = existing_availability

    mock_data_delete = mocker.patch('services.musician_availability.data.delete')
    mock_data_delete.return_value = True

    # Act
    result = delete(availability_id, current_user)

    # Assert
    assert result is True
    mock_data_delete.assert_called_once_with(availability_id)


def test_delete_by_musician_and_date_success(mocker):
    """Test delete_by_musician_and_date() deletes availability"""
    # Arrange
    musician_id = 1
    unavailable_date = date.today() + timedelta(days=1)
    current_user = {'id': 1, 'role': 'musician'}

    existing_availability = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_data_get = mocker.patch('services.musician_availability.data.get_by_musician_and_date')
    mock_data_get.return_value = existing_availability

    mock_data_delete = mocker.patch('services.musician_availability.data.delete_by_musician_and_date')
    mock_data_delete.return_value = True

    # Act
    result = delete_by_musician_and_date(musician_id, unavailable_date, current_user)

    # Assert
    assert result is True
    mock_data_delete.assert_called_once_with(musician_id, unavailable_date)


def test_database_error_handling(mocker):
    """Test that database errors are properly handled"""
    # Arrange
    musician_id = 1
    current_user = {'id': 1, 'role': 'musician'}

    mock_data_get = mocker.patch('services.musician_availability.data.get_by_musician')
    mock_data_get.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(DatabaseError):
        get_by_musician(musician_id, current_user)


def test_get_musician_availability_by_month_success(mocker):
    """Test get_musician_availability_by_month() returns monthly availability"""
    # Arrange
    musician_id = 1
    year = 2024
    month = 5
    current_user = {'id': 1, 'role': 'musician'}

    expected_availabilities = [
        MusicianAvailability(id=1, musician_id=1, unavailable_date=date.today() + timedelta(days=5), reason="Holiday"),
        MusicianAvailability(id=2, musician_id=1, unavailable_date=date.today() + timedelta(days=10), reason="Sick")
    ]
    mock_data_get = mocker.patch('services.musician_availability.data.get_musician_availability_by_month')
    mock_data_get.return_value = expected_availabilities

    # Act
    result = get_musician_availability_by_month(musician_id, year, month, current_user)

    # Assert
    assert result.musician_id == musician_id
    assert result.year == year
    assert result.month == month
    assert len(result.unavailable_dates) == 2
    assert result.unavailable_dates[0].id == 1
    assert result.unavailable_dates[0].unavailable_date == date.today() + timedelta(days=5)
    assert result.unavailable_dates[0].reason == "Holiday"
    mock_data_get.assert_called_once_with(musician_id, year, month)


def test_get_musician_availability_by_month_unauthorized(mocker):
    """Test get_musician_availability_by_month() raises UnauthorizedError for non-owner"""
    # Arrange
    musician_id = 2  # Different musician
    year = 2024
    month = 5
    current_user = {'id': 1, 'role': 'musician'}

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_musician_availability_by_month(musician_id, year, month, current_user)

    assert "You can only view your own availability" in str(exc_info.value)


def test_get_musician_availability_by_month_admin_access(mocker):
    """Test get_musician_availability_by_month() allows admin to view any musician's availability"""
    # Arrange
    musician_id = 2  # Different musician
    year = 2024
    month = 5
    current_user = {'id': 1, 'role': 'admin'}

    expected_availabilities = [
        MusicianAvailability(id=10, musician_id=2, unavailable_date=date(2026, 6, 10), reason="Meeting")
    ]
    mock_data_get = mocker.patch('services.musician_availability.data.get_musician_availability_by_month')
    mock_data_get.return_value = expected_availabilities

    # Act
    result = get_musician_availability_by_month(musician_id, year, month, current_user)

    # Assert
    assert result.musician_id == musician_id
    assert len(result.unavailable_dates) == 1
    assert result.unavailable_dates[0].id == 10
    assert result.unavailable_dates[0].reason == "Meeting"
    mock_data_get.assert_called_once_with(musician_id, year, month)


def test_get_musician_availability_by_month_invalid_month(mocker):
    """Test get_musician_availability_by_month() validates month parameter"""
    # Arrange
    musician_id = 1
    year = 2024
    month = 13  # Invalid month
    current_user = {'id': 1, 'role': 'musician'}

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        get_musician_availability_by_month(musician_id, year, month, current_user)

    assert "Month must be between 1 and 12" in str(exc_info.value)


def test_get_musician_availability_by_month_invalid_year(mocker):
    """Test get_musician_availability_by_month() validates year parameter"""
    # Arrange
    musician_id = 1
    year = 1999  # Invalid year (too low)
    month = 5
    current_user = {'id': 1, 'role': 'musician'}

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        get_musician_availability_by_month(musician_id, year, month, current_user)

    assert "Year must be between 2000 and 2100" in str(exc_info.value)


def test_get_musician_availability_by_month_database_error(mocker):
    """Test get_musician_availability_by_month() handles database errors"""
    # Arrange
    musician_id = 1
    year = 2024
    month = 5
    current_user = {'id': 1, 'role': 'musician'}

    mock_data_get = mocker.patch('services.musician_availability.data.get_musician_availability_by_month')
    mock_data_get.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(DatabaseError):
        get_musician_availability_by_month(musician_id, year, month, current_user)