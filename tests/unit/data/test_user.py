import pytest
from models.user import User
import data.user as data
from sqlalchemy.exc import SQLAlchemyError
from exceptions import DatabaseError


def test_get_all_paginated_without_order_by(mocker):
    """Test get_all_paginated() without order_by parameter"""
    # Arrange - Mock SessionLocal
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    
    # Mock count() and query chain
    mock_query.count.return_value = 2
    mock_query.options.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [
        User(id=1, name="John", lastname="Doe", email="john@example.com", password="pass", role_id=1),
        User(id=2, name="Jane", lastname="Smith", email="jane@example.com", password="pass", role_id=1)
    ]

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_all_paginated(skip=0, limit=20)

    # Assert
    assert result[0] is not None
    assert result[1] == 2  # total count as integer
    mock_query.order_by.assert_not_called()
    mock_session.close.assert_called_once()


def test_get_all_paginated_with_order_by(mocker):
    """Test get_all_paginated() with order_by parameter"""
    # Arrange - Mock SessionLocal
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    
    # Mock count() and query chain
    mock_query.count.return_value = 2
    mock_query.options.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [
        User(id=1, name="John", lastname="Doe", email="john@example.com", password="pass", role_id=1),
        User(id=2, name="Jane", lastname="Smith", email="jane@example.com", password="pass", role_id=1)
    ]

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.get_all_paginated(skip=0, limit=20, order_by='name')

    # Assert
    assert result[0] is not None
    assert result[1] == 2  # total count as integer
    mock_query.order_by.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_all_paginated_with_invalid_order_by(mocker):
    """Test get_all_paginated() with invalid order_by field (should be ignored)"""
    # Arrange - Mock SessionLocal
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    
    # Mock count() and query chain
    mock_query.count.return_value = 2
    mock_query.options.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [
        User(id=1, name="John", lastname="Doe", email="john@example.com", password="pass", role_id=1),
        User(id=2, name="Jane", lastname="Smith", email="jane@example.com", password="pass", role_id=1)
    ]

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - with invalid field name
    result = data.get_all_paginated(skip=0, limit=20, order_by='invalid_field')

    # Assert
    assert result[0] is not None
    assert result[1] == 2  # total count as integer
    # order_by should NOT be called with invalid field
    mock_query.order_by.assert_not_called()
    mock_session.close.assert_called_once()


def test_delete_user_found(mocker):
    """Test delete() when user exists"""
    # Arrange - Mock SessionLocal
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = User(
        id=1,
        name="John",
        lastname="Doe",
        email="john.doe@example.com",
        password="hashedpass",
        role_id=1
    )

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.delete(1)

    # Assert
    assert result is True
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()


def test_delete_user_not_found(mocker):
    """Test delete() when user does not exist"""
    # Arrange - Mock SessionLocal
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.delete(999)

    # Assert
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.close.assert_called_once()

def test_get_one_user_found(mocker):
    """Test get_one() when user exists"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = User(
        id=1,
        name="John",
        lastname="Doe",
        email="john.doe@example.com",
        password="hashedpass",
        role_id=1
    )

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one("john.doe@example.com")

    # Assert - Check result and session calls
    assert result is not None
    assert result.id == 1
    assert result.name == "John"
    assert result.email == "john.doe@example.com"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.query.assert_called_once_with(User)
    mock_query.filter.assert_called_once()
    mock_query.first.assert_called_once()

def test_get_one_user_not_found(mocker):
    """Test get_one() when user does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one("nonexistent@example.com")

    # Assert - Check result is None and session calls
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()

def test_get_one_user_database_error(mocker):
    """Test get_one() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and query to raise SQLAlchemyError
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = SQLAlchemyError("Test error")

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_one("john.doe@example.com")

    assert str(exc_info.value) == "Failed to get user"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_one_by_id_user_found(mocker):
    """Test get_one_by_id() when user exists"""
    # Arrange - Mock SessionLocal, query and selectinload
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    
    # Create a mock user with a mock role
    mock_role = mocker.MagicMock()
    mock_role.name = "admin"
    mock_user = User(
        id=1,
        name="John",
        lastname="Doe",
        email="john.doe@example.com",
        password="hashedpass",
        role_id=1
    )
    mock_user.role = mock_role
    mock_query.first.return_value = mock_user

    # Mock selectinload
    mocker.patch('data.user.selectinload', return_value=mock_options)
    
    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one_by_id(1)

    # Assert - Check result and session calls
    assert result is not None
    assert result.id == 1
    assert result.name == "John"
    assert result.email == "john.doe@example.com"
    assert result.role.name == "admin"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_one_by_id_user_not_found(mocker):
    """Test get_one_by_id() when user does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    # Mock selectinload
    mocker.patch('data.user.selectinload', return_value=mock_options)
    
    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one_by_id(999)

    # Assert - Check result is None and session calls
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_one_by_id_database_error(mocker):
    """Test get_one_by_id() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and query to raise SQLAlchemyError
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_options = mocker.Mock()
    
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = SQLAlchemyError("Test error")

    # Mock selectinload
    mocker.patch('data.user.selectinload', return_value=mock_options)
    
    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_one_by_id(1)

    assert str(exc_info.value) == "Failed to get user"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()

def test_get_all_users(mocker):
    """Test get_all() returns list of users"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    expected_users = [
        User(
            id=1,
            name="John",
            lastname="Doe",
            email="john.doe@example.com",
            password="hashedpass",
            role_id=1
        ),
        User(
            id=2,
            name="Jane",
            lastname="Smith",
            email="jane.smith@example.com",
            password="hashedpass",
            role_id=2
        )
    ]
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = expected_users

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_all()

    # Assert - Check result and session calls
    assert result == expected_users
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.query.assert_called_once_with(User)
    mock_query.all.assert_called_once()

def test_get_all_users_database_error(mocker):
    """Test get_all() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and query to raise SQLAlchemyError
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.side_effect = SQLAlchemyError("Test error")

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_all()

    assert str(exc_info.value) == "Failed to get all users"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()

def test_create_user(mocker):
    """Test create() user"""
    # Arrange
    user = User(
        name="Jane",
        lastname="Smith",
        email="jane.smith@example.com",
        password="hashedpass",
        role_id=2
    )
    mock_session = mocker.Mock()
    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.create(user)

    # Assert
    assert result == user
    mock_session.add.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(user)
    mock_session.close.assert_called_once()

def test_create_user_database_error(mocker):
    """Test create() raises DatabaseError on SQLAlchemyError"""
    # Arrange
    user = User(
        name="Jane",
        lastname="Smith",
        email="jane.smith@example.com",
        password="hashedpass",
        role_id=2
    )
    mock_session = mocker.Mock()
    mock_session.commit.side_effect = SQLAlchemyError("Test error")

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.create(user)

    assert str(exc_info.value) == "Failed to create user"
    mock_session.add.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()

def test_modify_user_found(mocker):
    """Test modify() when user exists"""
    # Arrange
    user = User(id=1, name="Updated John", lastname="Doe", email="john.doe@example.com", password="newpass", role_id=1)
    existing_user = User(id=1, name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1)

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_user

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.modify(user)

    # Assert
    assert result == existing_user
    assert existing_user.name == "Updated John"
    assert existing_user.password == "newpass"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_user)


def test_modify_user_not_found(mocker):
    """Test modify() when user does not exist"""
    # Arrange
    user = User(id=99, name="Nonexistent", lastname="User", email="nonexistent@example.com", password="newpass", role_id=1)
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act
    result = data.modify(user)

    # Assert
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()

def test_modify_user_database_error(mocker):
    """Test modify() raises DatabaseError on SQLAlchemyError"""
    # Arrange
    user = User(id=1, name="Updated John", lastname="Doe", email="john.doe@example.com", password="newpass", role_id=1)
    existing_user = User(id=1, name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1)

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_user
    mock_session.commit.side_effect = SQLAlchemyError("Test error")

    mock_session_local = mocker.patch('data.user.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.modify(user)

    assert str(exc_info.value) == "Failed to modify user"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    mock_session.refresh.assert_not_called()