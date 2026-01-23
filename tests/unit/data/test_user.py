import pytest
from models.user import User
import data.user as data

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