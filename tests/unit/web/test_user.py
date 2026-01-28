import pytest
from fastapi import HTTPException
from schemas.user import User, UserCreate
from web.user import get_all, get_one, create, modify
from exceptions import NotFoundError, ConflictError, DatabaseError

def test_get_users_empty_list(mocker):
    """Test get_all() returns empty list when no users"""
    # Arrange - Mock service to return empty list
    mock_service = mocker.patch('web.user.service.get_all')
    mock_service.return_value = []

    # Act - Call function directly
    result = get_all()

    # Assert - Check result is empty list
    assert result == []
    mock_service.assert_called_once()

def test_get_users_with_data(mocker):
    """Test get_all() returns users when they exist"""
    # Arrange - Mock service to return specific users
    expected_users = [
        User(id=1, name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1),
        User(id=2, name="Jane", lastname="Smith", email="jane.smith@example.com", password="hashedpass", role_id=2)
    ]
    mock_service = mocker.patch('web.user.service.get_all')
    mock_service.return_value = expected_users

    # Act - Call function directly
    result = get_all()

    # Assert - Check result contains the mocked data
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "John"
    assert result[0].email == "john.doe@example.com"
    assert result[1].id == 2
    assert result[1].name == "Jane"
    mock_service.assert_called_once()

def test_get_user_found(mocker):
    """Test get_one() when user exists"""
    # Arrange - Mock service to return a specific user
    expected_user = User(id=1, name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1)
    mock_service = mocker.patch('web.user.service.get_one')
    mock_service.return_value = expected_user

    # Act - Call function directly
    result = get_one("john.doe@example.com")

    # Assert - Check result contains the mocked user
    assert result.id == 1
    assert result.name == "John"
    assert result.email == "john.doe@example.com"
    mock_service.assert_called_once_with("john.doe@example.com")

def test_get_user_not_found(mocker):
    """Test get_one() when user doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    mock_service = mocker.patch('web.user.service.get_one')
    mock_service.side_effect = NotFoundError("User with email nonexistent@example.com not found")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_one("nonexistent@example.com")

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
    mock_service.assert_called_once_with("nonexistent@example.com")

def test_create_user(mocker):
    """Test create() creates and returns new user"""
    # Arrange - Mock service to return created user
    input_data = UserCreate(name="Jane", lastname="Smith", email="jane.smith@example.com", password="hashedpass", role_id=2)
    expected_created_user = User(id=3, name="Jane", lastname="Smith", email="jane.smith@example.com", password="hashedpass", role_id=2)
    mock_service = mocker.patch('web.user.service.create')
    mock_service.return_value = expected_created_user

    # Act - Call function directly
    result = create(input_data)

    # Assert - Check result contains created user
    assert result.id == 3
    assert result.name == "Jane"
    assert result.email == "jane.smith@example.com"
    mock_service.assert_called_once()
    # Verify service was called with UserCreate object
    call_args = mock_service.call_args[0][0]
    assert isinstance(call_args, UserCreate)
    assert call_args.name == "Jane"
    assert call_args.email == "jane.smith@example.com"

def test_modify_user(mocker):
    """Test modify() updates and returns modified user"""
    # Arrange - Mock service to return modified user
    input_data = User(id=1, name="Updated John", lastname="Doe", email="john.doe@example.com", password="newpass", role_id=1)
    expected_modified_user = User(id=1, name="Updated John", lastname="Doe", email="john.doe@example.com", password="newpass", role_id=1)
    mock_service = mocker.patch('web.user.service.modify')
    mock_service.return_value = expected_modified_user

    # Act - Call function directly
    result = modify(input_data)

    # Assert - Check result contains modified user
    assert result.id == 1
    assert result.name == "Updated John"
    assert result.password == "newpass"
    mock_service.assert_called_once()
    # Verify service was called with User object
    call_args = mock_service.call_args[0][0]
    assert isinstance(call_args, User)
    assert call_args.id == 1
    assert call_args.name == "Updated John"

def test_create_user_conflict(mocker):
    """Test create() handles conflict when user already exists"""
    # Arrange - Mock service to raise ConflictError for duplicate user
    input_data = UserCreate(name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1)
    mock_service = mocker.patch('web.user.service.create')
    mock_service.side_effect = ConflictError("User with email john.doe@example.com already exists")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        create(input_data)

    assert exc_info.value.status_code == 409
    assert "User already exists" in exc_info.value.detail
    mock_service.assert_called_once()
    # Verify service was called with UserCreate object
    call_args = mock_service.call_args[0][0]
    assert isinstance(call_args, UserCreate)
    assert call_args.email == "john.doe@example.com"

def test_modify_user_not_found(mocker):
    """Test modify() when user doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    input_data = User(id=1, name="Nonexistent", lastname="User", email="nonexistent@example.com", password="pass", role_id=1)
    mock_service = mocker.patch('web.user.service.modify')
    mock_service.side_effect = NotFoundError("User with email nonexistent@example.com not found")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        modify(input_data)

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
    mock_service.assert_called_once()

def test_get_all_database_error(mocker):
    """Test get_all() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.user.service.get_all')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_all()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once()