import pytest
from datetime import date, timedelta
from models.musician_availability import MusicianAvailability
import data.musician_availability as data
from sqlalchemy.exc import SQLAlchemyError
from exceptions import DatabaseError


def test_get_by_musician_found(mocker):
    """Test get_by_musician() when availabilities exist"""
    # Arrange
    musician_id = 1
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query

    expected_availabilities = [
        MusicianAvailability(id=1, musician_id=1, unavailable_date=date.today() + timedelta(days=1), reason="Holiday"),
        MusicianAvailability(id=2, musician_id=1, unavailable_date=date.today() + timedelta(days=2), reason="Sick")
    ]
    mock_query.all.return_value = expected_availabilities

    # Mock selectinload
    mocker.patch('data.musician_availability.selectinload', return_value=mock_options)

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_by_musician(musician_id)

    # Assert
    assert result == expected_availabilities
    mock_query.options.assert_called_once()
    mock_query.filter.assert_called_once()
    mock_query.all.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_by_musician_not_found(mocker):
    """Test get_by_musician() when no availabilities exist"""
    # Arrange
    musician_id = 1
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = []

    # Mock selectinload
    mocker.patch('data.musician_availability.selectinload', return_value=mock_options)

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_by_musician(musician_id)

    # Assert
    assert result == []
    mock_session.close.assert_called_once()


def test_get_by_musician_database_error(mocker):
    """Test get_by_musician() raises DatabaseError on SQLAlchemyError"""
    # Arrange
    musician_id = 1
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.side_effect = SQLAlchemyError("Test error")

    # Mock selectinload
    mocker.patch('data.musician_availability.selectinload', return_value=mock_options)

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        data.get_by_musician(musician_id)

    assert str(exc_info.value) == "Failed to get musician availability"
    mock_session.close.assert_called_once()


def test_get_by_musician_and_date_found(mocker):
    """Test get_by_musician_and_date() when availability exists"""
    # Arrange
    musician_id = 1
    test_date = date.today() + timedelta(days=1)
    expected_availability = MusicianAvailability(id=1, musician_id=1, unavailable_date=test_date, reason="Holiday")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = expected_availability

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_by_musician_and_date(musician_id, test_date)

    # Assert
    assert result == expected_availability
    mock_session.close.assert_called_once()


def test_get_by_musician_and_date_not_found(mocker):
    """Test get_by_musician_and_date() when availability does not exist"""
    # Arrange
    musician_id = 1
    test_date = date.today() + timedelta(days=1)

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_by_musician_and_date(musician_id, test_date)

    # Assert
    assert result is None
    mock_session.close.assert_called_once()


def test_get_all_by_date_found(mocker):
    """Test get_all_by_date() when availabilities exist"""
    # Arrange
    test_date = date.today() + timedelta(days=1)
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query

    expected_availabilities = [
        MusicianAvailability(id=1, musician_id=1, unavailable_date=test_date, reason="Holiday"),
        MusicianAvailability(id=2, musician_id=2, unavailable_date=test_date, reason="Sick")
    ]
    mock_query.all.return_value = expected_availabilities

    # Mock selectinload
    mocker.patch('data.musician_availability.selectinload', return_value=mock_options)

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_all_by_date(test_date)

    # Assert
    assert result == expected_availabilities
    mock_session.close.assert_called_once()


def test_check_availability_available(mocker):
    """Test check_availability() when musician is available"""
    # Arrange
    musician_id = 1
    check_date = date.today() + timedelta(days=1)

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None  # No availability entry means available

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.check_availability(musician_id, check_date)

    # Assert
    assert result is True
    mock_session.close.assert_called_once()


def test_check_availability_unavailable(mocker):
    """Test check_availability() when musician is unavailable"""
    # Arrange
    musician_id = 1
    check_date = date.today() + timedelta(days=1)
    availability = MusicianAvailability(id=1, musician_id=1, unavailable_date=check_date, reason="Holiday")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = availability  # Availability entry means unavailable

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.check_availability(musician_id, check_date)

    # Assert
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.close.assert_called_once()


def test_get_musician_availability_by_month_found(mocker):
    """Test get_musician_availability_by_month() when availabilities exist"""
    # Arrange
    musician_id = 1
    year = 2024
    month = 5
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query

    expected_availabilities = [
        MusicianAvailability(id=1, musician_id=1, unavailable_date=date(2026, 5, 15), reason="Holiday"),
        MusicianAvailability(id=2, musician_id=1, unavailable_date=date(2026, 5, 20), reason="Sick")
    ]
    mock_query.all.return_value = expected_availabilities

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_musician_availability_by_month(musician_id, year, month)

    # Assert
    assert result == expected_availabilities
    mock_query.filter.assert_called_once()
    mock_query.all.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_musician_availability_by_month_no_availabilities(mocker):
    """Test get_musician_availability_by_month() when no availabilities exist"""
    # Arrange
    musician_id = 1
    year = 2024
    month = 5
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query

    mock_query.all.return_value = []

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_musician_availability_by_month(musician_id, year, month)

    # Assert
    assert result == []
    mock_query.filter.assert_called_once()
    mock_query.all.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_musician_availability_by_month_database_error(mocker):
    """Test get_musician_availability_by_month() with database error"""
    # Arrange
    musician_id = 1
    year = 2024
    month = 5
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query

    mock_query.all.side_effect = SQLAlchemyError("Database error")

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert
    with pytest.raises(DatabaseError):
        data.get_musician_availability_by_month(musician_id, year, month)

    mock_session.close.assert_called_once()


def test_create_availability(mocker):
    """Test create() availability"""
    # Arrange
    availability = MusicianAvailability(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )
    mock_session = mocker.Mock()
    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.create(availability)

    # Assert
    assert result == availability
    mock_session.add.assert_called_once_with(availability)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(availability)
    mock_session.close.assert_called_once()


def test_create_availability_database_error(mocker):
    """Test create() raises DatabaseError on SQLAlchemyError"""
    # Arrange
    availability = MusicianAvailability(
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )
    mock_session = mocker.Mock()
    mock_session.commit.side_effect = SQLAlchemyError("Test error")

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        data.create(availability)

    assert str(exc_info.value) == "Failed to create musician availability"
    mock_session.add.assert_called_once_with(availability)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()


def test_create_bulk_availability(mocker):
    """Test create_bulk() availability"""
    # Arrange
    availabilities = [
        MusicianAvailability(musician_id=1, unavailable_date=date.today() + timedelta(days=1), reason="Holiday"),
        MusicianAvailability(musician_id=1, unavailable_date=date.today() + timedelta(days=2), reason="Sick")
    ]
    mock_session = mocker.Mock()
    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.create_bulk(availabilities)

    # Assert
    assert result == availabilities
    mock_session.add_all.assert_called_once_with(availabilities)
    mock_session.commit.assert_called_once()
    assert mock_session.refresh.call_count == 2  # Called for each availability
    mock_session.close.assert_called_once()


def test_update_availability_found(mocker):
    """Test update() when availability exists"""
    # Arrange
    availability = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )
    updates = {"unavailable_date": date.today() + timedelta(days=2), "reason": "Updated reason"}
    expected_updated = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=2),
        reason="Updated reason"
    )

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = expected_updated

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.update(availability, updates)

    # Assert
    assert result == expected_updated
    assert result.unavailable_date == date.today() + timedelta(days=2)
    assert result.reason == "Updated reason"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(expected_updated)
    mock_session.close.assert_called_once()


def test_update_availability_not_found(mocker):
    """Test update() when availability does not exist"""
    # Arrange
    availability = MusicianAvailability(
        id=999,
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )
    updates = {"reason": "Updated reason"}

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.update(availability, updates)

    # Assert
    assert result is None
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()
    mock_session.close.assert_called_once()


def test_delete_availability_found(mocker):
    """Test delete() when availability exists"""
    # Arrange
    availability_id = 1
    existing_availability = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=date.today() + timedelta(days=1),
        reason="Holiday"
    )

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_availability

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.delete(availability_id)

    # Assert
    assert result is True
    mock_session.delete.assert_called_once_with(existing_availability)
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()


def test_delete_availability_not_found(mocker):
    """Test delete() when availability does not exist"""
    # Arrange
    availability_id = 999

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.delete(availability_id)

    # Assert
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.close.assert_called_once()


def test_delete_by_musician_and_date_found(mocker):
    """Test delete_by_musician_and_date() when availability exists"""
    # Arrange
    musician_id = 1
    test_date = date.today() + timedelta(days=1)
    existing_availability = MusicianAvailability(
        id=1,
        musician_id=1,
        unavailable_date=test_date,
        reason="Holiday"
    )

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_availability

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.delete_by_musician_and_date(musician_id, test_date)

    # Assert
    assert result is True
    mock_session.delete.assert_called_once_with(existing_availability)
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()


def test_delete_by_musician_and_date_not_found(mocker):
    """Test delete_by_musician_and_date() when availability does not exist"""
    # Arrange
    musician_id = 1
    test_date = date.today() + timedelta(days=1)

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.musician_availability.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.delete_by_musician_and_date(musician_id, test_date)

    # Assert
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.close.assert_called_once()