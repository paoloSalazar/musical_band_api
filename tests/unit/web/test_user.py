import pytest
from fastapi import HTTPException
from schemas.user import UserResponse, UserCreate, UserUpdate, UserPasswordUpdate
from web.user import get_all, get_one, create, modify, modify_password
from exceptions import NotFoundError, ConflictError, DatabaseError

def test_get_users_empty_list(mocker):
    """Test get_all() returns empty list when no users"""
    # Arrange - Mock service to return empty list
    mock_service = mocker.patch('web.user.service.get_all')
    mock_service.return_value = []
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = get_all(current_user=mock_current_user)

    # Assert - Check result is empty list
    assert result == []
    mock_service.assert_called_once()

def test_get_users_with_data(mocker):
    """Test get_all() returns users when they exist"""
    # Arrange - Mock service to return specific users
    expected_users = [
        UserResponse(id=1, name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1),
        UserResponse(id=2, name="Jane", lastname="Smith", email="jane.smith@example.com", password="hashedpass", role_id=2)
    ]
    mock_service = mocker.patch('web.user.service.get_all')
    mock_service.return_value = expected_users
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = get_all(current_user=mock_current_user)

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
    expected_user = UserResponse(id=1, name="John", lastname="Doe", email="john.doe@example.com", role_id=1)
    mock_service = mocker.patch('web.user.service.get_one')
    mock_service.return_value = expected_user
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = get_one(current_user=mock_current_user, email="john.doe@example.com")

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
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_one(current_user=mock_current_user, email="nonexistent@example.com")

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
    mock_service.assert_called_once_with("nonexistent@example.com")

def test_create_user(mocker):
    """Test create() creates and returns new user"""
    # Arrange - Mock service to return created user
    input_data = UserCreate(name="Jane", lastname="Smith", email="jane.smith@example.com", password="hashedpass", role_id=2)
    expected_created_user = UserResponse(id=3, name="Jane", lastname="Smith", email="jane.smith@example.com", role_id=2)
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
    input_data = UserUpdate(name="Updated John", lastname="Doe", email="john.doe@example.com", role_id=1)
    expected_modified_user = UserResponse(id=1, name="Updated John", lastname="Doe", email="john.doe@example.com", role_id=1)
    mock_service = mocker.patch('web.user.service.modify')
    mock_service.return_value = expected_modified_user
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = modify(current_user=mock_current_user, user_update=input_data)

    # Assert - Check result contains modified user
    assert result.id == 1
    assert result.name == "Updated John"
    mock_service.assert_called_once()
    # Verify service was called with UserUpdate object
    call_args = mock_service.call_args[0][0]
    assert isinstance(call_args, UserUpdate)
    assert call_args.name == "Updated John"
    assert call_args.email == "john.doe@example.com"

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
    input_data = UserUpdate(name="Nonexistent", lastname="User", email="nonexistent@example.com", role_id=1)
    mock_service = mocker.patch('web.user.service.modify')
    mock_service.side_effect = NotFoundError("User with email nonexistent@example.com not found")
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        modify(current_user=mock_current_user, user_update=input_data)

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
    mock_service.assert_called_once()

def test_get_all_database_error(mocker):
    """Test get_all() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.user.service.get_all')
    mock_service.side_effect = DatabaseError("Database connection failed")
    mock_current_user = {"sub": "test@example.com", "role": "admin"}


    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_all(current_user=mock_current_user)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once()


def test_modify_password_success(mocker):
    """Test modify_password() successfully updates password"""
    # Arrange - Mock service to return True
    mock_service = mocker.patch('web.user.service.modify_password')
    mock_service.return_value = True
    mock_current_user = {"sub": "test@example.com", "role": "admin"}
    password_update = UserPasswordUpdate(current_password="oldpassword", new_password="newpassword")

    # Act - Call function directly
    result = modify_password(current_user=mock_current_user, email="john.doe@example.com", password_update=password_update)

    # Assert - Check result contains success message
    assert result == {"message": "Password updated successfully"}
    mock_service.assert_called_once_with("john.doe@example.com", "oldpassword", "newpassword")


def test_modify_password_user_not_found(mocker):
    """Test modify_password() when user doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    mock_service = mocker.patch('web.user.service.modify_password')
    mock_service.side_effect = NotFoundError("User with email nonexistent@example.com not found")
    mock_current_user = {"sub": "test@example.com", "role": "admin"}
    password_update = UserPasswordUpdate(current_password="oldpassword", new_password="newpassword")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        modify_password(current_user=mock_current_user, email="nonexistent@example.com", password_update=password_update)

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
    mock_service.assert_called_once()


def test_modify_password_invalid_current(mocker):
    """Test modify_password() when current password is incorrect"""
    # Arrange - Mock service to raise UnauthorizedError
    from exceptions import UnauthorizedError
    mock_service = mocker.patch('web.user.service.modify_password')
    mock_service.side_effect = UnauthorizedError("Current password is incorrect")
    mock_current_user = {"sub": "test@example.com", "role": "admin"}
    password_update = UserPasswordUpdate(current_password="wrongpassword", new_password="newpassword")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        modify_password(current_user=mock_current_user, email="john.doe@example.com", password_update=password_update)

    assert exc_info.value.status_code == 401
    assert "Current password is incorrect" in exc_info.value.detail
    mock_service.assert_called_once()