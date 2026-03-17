import pytest
from models.user_detail import UserDetail
import data.user_detail as data
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError


def test_get_one_user_detail_found(mocker):
    """Test get_one() when user detail exists"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = UserDetail(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one(1)

    # Assert - Check result and session calls
    assert result is not None
    assert result.id == 1
    assert result.user_id == 1
    assert result.detail_type == "phone"
    assert result.detail_value == "+1234567890"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.query.assert_called_once_with(UserDetail)
    mock_query.filter.assert_called_once()
    mock_query.first.assert_called_once()


def test_get_one_user_detail_not_found(mocker):
    """Test get_one() when user detail does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one(999)

    # Assert - Check result is None
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_one_user_detail_database_error(mocker):
    """Test get_one() handles database errors"""
    # Arrange - Mock SessionLocal to raise database error
    mock_session = mocker.Mock()
    mock_session.query.side_effect = SQLAlchemyError("Database error")

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError):
        data.get_one(1)


def test_get_by_user_id_found(mocker):
    """Test get_by_user_id() when user details exist"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [
        UserDetail(id=1, user_id=1, detail_type="phone", detail_value="+1234567890"),
        UserDetail(id=2, user_id=1, detail_type="address", detail_value="123 Main St")
    ]

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_by_user_id(1)

    # Assert - Check result
    assert result is not None
    assert len(result) == 2
    assert result[0].detail_type == "phone"
    assert result[1].detail_type == "address"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_by_user_id_not_found(mocker):
    """Test get_by_user_id() when user has no details"""
    # Arrange - Mock SessionLocal and query to return empty list
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = []

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_by_user_id(999)

    # Assert - Check result is empty list
    assert result == []
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_all_user_details_empty(mocker):
    """Test get_all() when no user details exist"""
    # Arrange - Mock SessionLocal and query to return empty list
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = []

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_all()

    # Assert - Check result is empty list
    assert result == []
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_all_user_details_with_data(mocker):
    """Test get_all() when user details exist"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = [
        UserDetail(id=1, user_id=1, detail_type="phone", detail_value="+1234567890"),
        UserDetail(id=2, user_id=2, detail_type="email", detail_value="test@example.com")
    ]

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_all()

    # Assert - Check result
    assert result is not None
    assert len(result) == 2
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_all_user_details_database_error(mocker):
    """Test get_all() handles database errors"""
    # Arrange - Mock SessionLocal to raise database error
    mock_session = mocker.Mock()
    mock_session.query.side_effect = SQLAlchemyError("Database error")

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError):
        data.get_all()


def test_create_user_detail(mocker):
    """Test create() creates and returns new user detail"""
    # Arrange - Mock SessionLocal and add
    mock_session = mocker.Mock()
    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session
    
    mock_session.add = mocker.Mock()
    mock_session.commit = mocker.Mock()
    mock_session.refresh = mocker.Mock()
    
    # Create input data
    detail_data = {
        "user_id": 1,
        "detail_type": "phone",
        "detail_value": "+1234567890"
    }

    # Act - Call data function
    result = data.create(detail_data)

    # Assert - Check result
    assert result is not None
    assert result.user_id == 1
    assert result.detail_type == "phone"
    assert result.detail_value == "+1234567890"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_create_user_detail_database_error(mocker):
    """Test create() handles database errors"""
    # Arrange - Mock SessionLocal to raise database error
    mock_session = mocker.Mock()
    mock_session.add.side_effect = SQLAlchemyError("Database error")

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    detail_data = {
        "user_id": 1,
        "detail_type": "phone",
        "detail_value": "+1234567890"
    }

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError):
        data.create(detail_data)


def test_update_user_detail_found(mocker):
    """Test update() updates and returns user detail"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = UserDetail(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    update_data = {
        "detail_value": "+0987654321"
    }

    # Act - Call data function
    result = data.update(1, update_data)

    # Assert - Check result
    assert result is not None
    assert result.detail_value == "+0987654321"
    mock_session.commit.assert_called_once()


def test_update_user_detail_not_found(mocker):
    """Test update() when user detail does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    update_data = {
        "detail_value": "+0987654321"
    }

    # Act - Call data function
    result = data.update(999, update_data)

    # Assert - Check result is None
    assert result is None
    mock_session.commit.assert_not_called()


def test_delete_user_detail_found(mocker):
    """Test delete() deletes user detail"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = UserDetail(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.delete(1)

    # Assert - Check result
    assert result is True
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_delete_user_detail_not_found(mocker):
    """Test delete() when user detail does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.delete(999)

    # Assert - Check result is False
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


def test_delete_by_user_id_found(mocker):
    """Test delete_by_user_id() deletes all user details"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [
        UserDetail(id=1, user_id=1, detail_type="phone", detail_value="+1234567890"),
        UserDetail(id=2, user_id=1, detail_type="address", detail_value="123 Main St")
    ]

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.delete_by_user_id(1)

    # Assert - Check result
    assert result is True
    assert mock_session.delete.call_count == 2
    mock_session.commit.assert_called_once()


def test_delete_by_user_id_not_found(mocker):
    """Test delete_by_user_id() when user has no details"""
    # Arrange - Mock SessionLocal and query to return empty list
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = []

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.delete_by_user_id(999)

    # Assert - Check result is False
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


def test_create_user_detail_duplicate_constraint(mocker):
    """Test create() raises ConflictError when duplicate detail type exists"""
    # Arrange - Mock SessionLocal to raise IntegrityError (unique constraint violation)
    mock_session = mocker.Mock()
    mock_session.add.side_effect = IntegrityError(
        "duplicate key value violates unique constraint \"uq_user_detail_type\"",
        orig=None,
        params=None
    )

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    detail_data = {
        "user_id": 1,
        "detail_type": "phone",
        "detail_value": "+1234567890"
    }

    # Act & Assert - Call data function and expect ConflictError
    with pytest.raises(ConflictError) as exc_info:
        data.create(detail_data)
    
    assert "phone" in str(exc_info.value)
    mock_session.rollback.assert_called_once()


def test_update_user_detail_duplicate_constraint(mocker):
    """Test update() raises ConflictError when duplicate detail type exists"""
    # Arrange - Mock SessionLocal and query to return existing detail
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = UserDetail(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )
    # Make commit raise IntegrityError
    mock_session.commit.side_effect = IntegrityError(
        "duplicate key value violates unique constraint \"uq_user_detail_type\"",
        orig=None,
        params=None
    )

    mock_session_local = mocker.patch('data.user_detail.SessionLocal')
    mock_session_local.return_value = mock_session

    update_data = {
        "detail_type": "address"
    }

    # Act & Assert - Call data function and expect ConflictError
    with pytest.raises(ConflictError) as exc_info:
        data.update(1, update_data)
    
    assert "address" in str(exc_info.value)
    mock_session.rollback.assert_called_once()
