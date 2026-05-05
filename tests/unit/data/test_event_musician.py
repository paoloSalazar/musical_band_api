import pytest
from decimal import Decimal
from models.event_musician import EventMusician, PaymentStatus
import data.event_musician as data
from sqlalchemy.exc import SQLAlchemyError
from exceptions import DatabaseError


def test_get_by_event_found(mocker):
    """Test get_by_event() when musicians are assigned"""
    # Arrange
    event_id = 1
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query

    expected_musicians = [
        EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING"),
        EventMusician(id=2, event_id=1, musician_id=3, role="Drummer", salary=Decimal("1200.00"), payment_status="COMPLETED")
    ]
    mock_query.all.return_value = expected_musicians

    # Mock selectinload
    mocker.patch('data.event_musician.selectinload', return_value=mock_options)

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_by_event(event_id)

    # Assert
    assert result == expected_musicians
    mock_query.options.assert_called_once()
    mock_query.filter.assert_called_once()
    mock_query.all.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_by_event_not_found(mocker):
    """Test get_by_event() when no musicians are assigned"""
    # Arrange
    event_id = 1
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = []

    # Mock selectinload
    mocker.patch('data.event_musician.selectinload', return_value=mock_options)

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_by_event(event_id)

    # Assert
    assert result == []
    mock_session.close.assert_called_once()


def test_get_by_event_database_error(mocker):
    """Test get_by_event() raises DatabaseError on SQLAlchemyError"""
    # Arrange
    event_id = 1
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.side_effect = SQLAlchemyError("Test error")

    # Mock selectinload
    mocker.patch('data.event_musician.selectinload', return_value=mock_options)

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        data.get_by_event(event_id)

    assert str(exc_info.value) == "Failed to get event musicians"
    mock_session.close.assert_called_once()


def test_get_by_musician_found(mocker):
    """Test get_by_musician() when assignments exist"""
    # Arrange
    musician_id = 2
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query

    expected_assignments = [
        EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING"),
        EventMusician(id=3, event_id=2, musician_id=2, role="Bassist", salary=Decimal("1300.00"), payment_status="COMPLETED")
    ]
    mock_query.all.return_value = expected_assignments

    # Mock selectinload
    mocker.patch('data.event_musician.selectinload', return_value=mock_options)

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_by_musician(musician_id)

    # Assert
    assert result == expected_assignments
    mock_session.close.assert_called_once()


def test_get_by_event_and_musician_found(mocker):
    """Test get_by_event_and_musician() when assignment exists"""
    # Arrange
    event_id = 1
    musician_id = 2
    expected_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = expected_assignment

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_by_event_and_musician(event_id, musician_id)

    # Assert
    assert result == expected_assignment
    mock_session.close.assert_called_once()


def test_get_by_event_and_musician_not_found(mocker):
    """Test get_by_event_and_musician() when assignment does not exist"""
    # Arrange
    event_id = 1
    musician_id = 2

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_by_event_and_musician(event_id, musician_id)

    # Assert
    assert result is None
    mock_session.close.assert_called_once()


def test_is_assigned_to_event_true(mocker):
    """Test is_assigned_to_event() when musician is assigned"""
    # Arrange
    event_id = 1
    musician_id = 2
    assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = assignment

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.is_assigned_to_event(event_id, musician_id)

    # Assert
    assert result is True
    mock_session.close.assert_called_once()


def test_is_assigned_to_event_false(mocker):
    """Test is_assigned_to_event() when musician is not assigned"""
    # Arrange
    event_id = 1
    musician_id = 2

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.is_assigned_to_event(event_id, musician_id)

    # Assert
    assert result is False
    mock_session.close.assert_called_once()


def test_create_event_musician(mocker):
    """Test create() event musician"""
    # Arrange
    musician = EventMusician(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status="PENDING"
    )
    mock_session = mocker.Mock()
    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.create(musician)

    # Assert
    assert result == musician
    mock_session.add.assert_called_once_with(musician)
    mock_session.commit.assert_called_once()
    assert mock_session.refresh.call_count == 2
    mock_session.refresh.assert_any_call(musician)
    mock_session.refresh.assert_any_call(musician, ['musician', 'event'])
    mock_session.close.assert_called_once()


def test_create_event_musician_database_error(mocker):
    """Test create() raises DatabaseError on SQLAlchemyError"""
    # Arrange
    musician = EventMusician(
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status="PENDING"
    )
    mock_session = mocker.Mock()
    mock_session.commit.side_effect = SQLAlchemyError("Test error")

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        data.create(musician)

    assert str(exc_info.value) == "Failed to create event musician"
    mock_session.add.assert_called_once_with(musician)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()


def test_create_bulk_event_musicians(mocker):
    """Test create_bulk() event musicians"""
    # Arrange
    musicians = [
        EventMusician(event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING"),
        EventMusician(event_id=1, musician_id=3, role="Drummer", salary=Decimal("1200.00"), payment_status="PENDING")
    ]
    mock_session = mocker.Mock()
    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.create_bulk(musicians)

    # Assert
    assert result == musicians
    mock_session.add_all.assert_called_once_with(musicians)
    mock_session.commit.assert_called_once()
    assert mock_session.refresh.call_count == 2  # Called for each musician
    mock_session.close.assert_called_once()


def test_update_event_musician_found(mocker):
    """Test update() when musician assignment exists"""
    # Arrange
    musician = EventMusician(
        id=1,
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status="PENDING"
    )
    updates = {"role": "Solo Guitarist", "salary": Decimal("1600.00"), "payment_status": "COMPLETED"}
    expected_updated = EventMusician(
        id=1,
        event_id=1,
        musician_id=2,
        role="Solo Guitarist",
        salary=Decimal("1600.00"),
        payment_status="COMPLETED"
    )

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = expected_updated

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.update(musician, updates)

    # Assert
    assert result == expected_updated
    assert result.role == "Solo Guitarist"
    assert result.salary == Decimal("1600.00")
    assert result.payment_status == "COMPLETED"
    mock_session.commit.assert_called_once()
    assert mock_session.refresh.call_count == 2
    mock_session.refresh.assert_any_call(expected_updated)
    mock_session.refresh.assert_any_call(expected_updated, ['musician'])
    mock_session.close.assert_called_once()


def test_update_event_musician_not_found(mocker):
    """Test update() when musician assignment does not exist"""
    # Arrange
    musician = EventMusician(
        id=999,
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status="PENDING"
    )
    updates = {"role": "Solo Guitarist"}

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.update(musician, updates)

    # Assert
    assert result is None
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()
    mock_session.close.assert_called_once()


def test_delete_event_musician_found(mocker):
    """Test delete() when musician assignment exists"""
    # Arrange
    assignment_id = 1
    existing_musician = EventMusician(
        id=1,
        event_id=1,
        musician_id=2,
        role="Lead Guitarist",
        salary=Decimal("1500.00"),
        payment_status="PENDING"
    )

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_musician

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_integrity_check = mocker.patch('data.event_musician.check_integrity_before_deletion')
    mock_session_local.return_value = mock_session
    mock_integrity_check.return_value = None  # No integrity violations

    # Act
    result = data.delete(assignment_id)

    # Assert
    assert result is True
    mock_integrity_check.assert_called_once_with('event_musician', assignment_id)
    mock_session.delete.assert_called_once_with(existing_musician)
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()


def test_delete_event_musician_not_found(mocker):
    """Test delete() when musician assignment does not exist"""
    # Arrange
    musician_id = 999

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.event_musician.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.delete(musician_id)

    # Assert
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.close.assert_called_once()