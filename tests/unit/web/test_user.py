import pytest
from fastapi import HTTPException
from schemas.user import UserResponse, UserCreate, UserUpdate, UserPasswordUpdate, UserResponseWithRole, UserPaginationResponse, UserProfileUpdate
from web.user import get_all, get_one, create, modify, modify_password, get_current_user_info, get_one_by_id, modify_by_id, delete, modify_me
from exceptions import NotFoundError, ConflictError, DatabaseError
from auth.roles import RoleAndPermissionChecker


def test_get_users_empty_list(mocker):
    """Test get_all() returns empty list when no users"""
    # Arrange - Mock service to return empty paginated response
    mock_service = mocker.patch('web.user.service.get_all_paginated')
    mock_service.return_value = UserPaginationResponse(data=[], total=0, skip=0, limit=20)
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = get_all(current_user=mock_current_user)

    # Assert - Check result is empty pagination response
    assert result.data == []
    assert result.total == 0
    mock_service.assert_called_once()


def test_get_users_with_order_by(mocker):
    """Test get_all() passes order_by parameter to service"""
    # Arrange - Mock service to return paginated users
    expected_users = [
        UserResponseWithRole(id=1, name="John", lastname="Doe", email="john.doe@example.com", role_id=1, role="admin"),
        UserResponseWithRole(id=2, name="Jane", lastname="Smith", email="jane.smith@example.com", role_id=2, role="client")
    ]
    mock_service = mocker.patch('web.user.service.get_all_paginated')
    mock_service.return_value = UserPaginationResponse(data=expected_users, total=2, skip=0, limit=20)
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function with order_by parameter
    result = get_all(current_user=mock_current_user, skip=0, limit=20, order_by='name')

    # Assert
    assert len(result.data) == 2
    assert result.total == 2
    mock_service.assert_called_once_with(skip=0, limit=20, order_by='name')


def test_get_users_without_order_by(mocker):
    """Test get_all() works without order_by parameter (backwards compatibility)"""
    # Arrange - Mock service to return paginated users
    expected_users = [
        UserResponseWithRole(id=1, name="John", lastname="Doe", email="john.doe@example.com", phone_number=None, role_id=1, role="admin")
    ]
    mock_service = mocker.patch('web.user.service.get_all_paginated')
    mock_service.return_value = UserPaginationResponse(data=expected_users, total=1, skip=0, limit=20)
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function without order_by parameter
    result = get_all(current_user=mock_current_user, skip=0, limit=20)

    # Assert
    assert len(result.data) == 1
    mock_service.assert_called_once_with(skip=0, limit=20, order_by=None)


def test_delete_user_success(mocker):
    """Test delete() successfully deletes a user"""
    # Arrange - Mock service.delete
    mock_service = mocker.patch('web.user.service.delete')
    mock_service.return_value = True
    mock_current_user = {"sub": "admin@example.com", "role": "admin", "id": 1}

    # Act - Call function
    result = delete(current_user=mock_current_user, user_id=2)

    # Assert
    assert result == {"message": "User deleted successfully"}
    mock_service.assert_called_once_with(2)


def test_delete_user_self_deletion_forbidden(mocker):
    """Test delete() prevents user from deleting themselves"""
    # Arrange
    mock_current_user = {"sub": "admin@example.com", "role": "admin", "user_id": 1}

    # Act & Assert - Should raise 403 error
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete(current_user=mock_current_user, user_id=1)
    
    assert exc_info.value.status_code == 403
    assert "Cannot delete your own account" in exc_info.value.detail


def test_delete_user_not_found(mocker):
    """Test delete() returns 404 when user not found"""
    # Arrange - Mock service.delete to raise NotFoundError
    mock_service = mocker.patch('web.user.service.delete')
    from exceptions import NotFoundError
    mock_service.side_effect = NotFoundError("User not found")
    mock_current_user = {"sub": "admin@example.com", "role": "admin", "id": 1}

    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete(current_user=mock_current_user, user_id=999)
    
    assert exc_info.value.status_code == 404


def test_get_users_with_data(mocker):
    """Test get_all() returns users when they exist"""
    # Arrange - Mock service to return paginated users
    from schemas.user import UserPaginationResponse, UserResponseWithRole
    expected_users = [
        UserResponseWithRole(id=1, name="John", lastname="Doe", email="john.doe@example.com", role_id=1, role="admin"),
        UserResponseWithRole(id=2, name="Jane", lastname="Smith", email="jane.smith@example.com", role_id=2, role="client")
    ]
    mock_service = mocker.patch('web.user.service.get_all_paginated')
    mock_service.return_value = UserPaginationResponse(data=expected_users, total=2, skip=0, limit=20)
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = get_all(current_user=mock_current_user)

    # Assert - Check result contains the mocked data
    assert len(result.data) == 2
    assert result.data[0].id == 1
    assert result.data[0].name == "John"
    assert result.data[1].id == 2
    assert result.data[1].name == "Jane"
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


@pytest.mark.asyncio
async def test_create_user(mocker):
    """Test create() creates and returns new user"""
    # Arrange - Mock service to return created user
    input_data = UserCreate(name="Jane", lastname="Smith", email="jane.smith@example.com", password="hashedpass", role_id=2, phone_number="+1234567890")
    expected_created_user = UserResponse(id=3, name="Jane", lastname="Smith", email="jane.smith@example.com", role_id=2, phone_number="+1234567890")
    mock_service = mocker.patch('web.user.service.create')
    mock_service.return_value = expected_created_user

    # Act - Call function directly
    result = await create(input_data)

    # Assert - Check result contains created user
    assert result.id == 3
    assert result.name == "Jane"
    assert result.email == "jane.smith@example.com"
    assert result.phone_number == "+1234567890"
    mock_service.assert_called_once()
    # Verify service was called with UserCreate object
    call_args = mock_service.call_args[0][0]
    assert isinstance(call_args, UserCreate)
    assert call_args.name == "Jane"
    assert call_args.email == "jane.smith@example.com"
    assert call_args.phone_number == "+1234567890"


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


@pytest.mark.asyncio
async def test_create_user_conflict(mocker):
    """Test create() handles conflict when user already exists"""
    # Arrange - Mock service to raise ConflictError for duplicate user
    input_data = UserCreate(name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1)
    mock_service = mocker.patch('web.user.service.create')
    mock_service.side_effect = ConflictError("User with email john.doe@example.com already exists")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await create(input_data)

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
    mock_service = mocker.patch('web.user.service.get_all_paginated')
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
    
    # Mock service.get_one to return user info for email
    mock_get_one = mocker.patch('web.user.service.get_one')
    mock_get_one.return_value = mocker.MagicMock(
        email="john.doe@example.com",
        name="John",
        lastname="Doe"
    )
    
    # Mock send_password_change_confirmation to be an async function
    mock_email = mocker.patch('web.user.send_password_change_confirmation')
    mock_email.return_value = True
    
    mock_current_user = {"sub": "test@example.com", "role": "admin"}
    password_update = UserPasswordUpdate(current_password="oldpassword", new_password="newpassword")

    # Act - Call function directly and await since it's async
    import asyncio
    result = asyncio.run(modify_password(current_user=mock_current_user, email="john.doe@example.com", password_update=password_update))

    # Assert - Check result contains success message
    assert result == {"message": "Password updated successfully"}
    mock_service.assert_called_once_with("john.doe@example.com", "oldpassword", "newpassword")


def test_modify_password_user_not_found(mocker):
    """Test modify_password() when user doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    mock_service = mocker.patch('web.user.service.modify_password')
    mock_service.side_effect = NotFoundError("User with email nonexistent@example.com not found")
    
    # Mock send_password_change_confirmation to avoid issues
    mock_email = mocker.patch('web.user.send_password_change_confirmation')
    mock_email.return_value = True
    
    mock_current_user = {"sub": "test@example.com", "role": "admin"}
    password_update = UserPasswordUpdate(current_password="oldpassword", new_password="newpassword")

    # Act & Assert - Call function and expect HTTPException (need to run async)
    import asyncio
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(modify_password(current_user=mock_current_user, email="nonexistent@example.com", password_update=password_update))

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
    mock_service.assert_called_once()


def test_modify_password_invalid_current(mocker):
    """Test modify_password() when current password is incorrect"""
    # Arrange - Mock service to raise UnauthorizedError
    from exceptions import UnauthorizedError
    mock_service = mocker.patch('web.user.service.modify_password')
    mock_service.side_effect = UnauthorizedError("Current password is incorrect")
    
    # Mock send_password_change_confirmation to avoid issues
    mock_email = mocker.patch('web.user.send_password_change_confirmation')
    mock_email.return_value = True
    
    mock_current_user = {"sub": "test@example.com", "role": "admin"}
    password_update = UserPasswordUpdate(current_password="wrongpassword", new_password="newpassword")

    # Act & Assert - Call function and expect HTTPException (need to run async)
    import asyncio
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(modify_password(current_user=mock_current_user, email="john.doe@example.com", password_update=password_update))

    assert exc_info.value.status_code == 401
    assert "Current password is incorrect" in exc_info.value.detail
    mock_service.assert_called_once()


# ============================================
# Tests for GET /api/users/me endpoint
# ============================================


def test_get_current_user_info_success(mocker):
    """Test get_current_user_info() returns user info with roles and permissions"""
    # Arrange - Mock current_user from JWT token (format returned by auth.auth.get_current_user)
    mock_current_user = {
        "email": "john.doe@example.com",
        "id": 1,
        "role": "admin",
        "role_id": 1,
        "permissions": ["users:read", "users:write", "users:delete"]
    }
    # Mock the user service to return full user profile
    mock_user = mocker.MagicMock()
    mock_user.id = 1
    mock_user.name = "John"
    mock_user.lastname = "Doe"
    mock_user.second_lastname = "Smith"
    mock_user.email = "john.doe@example.com"
    mock_user.phone_number = "+1234567890"
    mock_service = mocker.patch('web.user.service.get_one')
    mock_service.return_value = mock_user

    # Act - Call function directly
    result = get_current_user_info(current_user=mock_current_user)

    # Assert - Check result contains user info
    assert result["email"] == "john.doe@example.com"
    assert result["id"] == 1
    assert result["name"] == "John"
    assert result["lastname"] == "Doe"
    assert result["second_lastname"] == "Smith"
    assert result["phone_number"] == "+1234567890"
    assert result["role"] == "admin"
    assert result["role_id"] == 1
    assert result["permissions"] == ["users:read", "users:write", "users:delete"]


def test_get_current_user_info_with_empty_permissions(mocker):
    """Test get_current_user_info() returns user with empty permissions list"""
    # Arrange - Mock current_user with no permissions (format returned by auth.auth.get_current_user)
    mock_current_user = {
        "email": "jane.smith@example.com",
        "id": 2,
        "role": "user",
        "role_id": 2,
        "permissions": []
    }
    # Mock the user service to return full user profile
    mock_user = mocker.MagicMock()
    mock_user.id = 2
    mock_user.name = "Jane"
    mock_user.lastname = "Smith"
    mock_user.second_lastname = None
    mock_user.email = "jane.smith@example.com"
    mock_service = mocker.patch('web.user.service.get_one')
    mock_service.return_value = mock_user

    # Act - Call function directly
    result = get_current_user_info(current_user=mock_current_user)

    # Assert - Check result contains user info with empty permissions
    assert result["email"] == "jane.smith@example.com"
    assert result["id"] == 2
    assert result["name"] == "Jane"
    assert result["lastname"] == "Smith"
    assert result["second_lastname"] is None
    assert result["role"] == "user"
    assert result["permissions"] == []


# ============================================
# Tests for POST /api/users/ RBAC (Admin + write:users)
# ============================================


@pytest.mark.asyncio
async def test_create_user_rbac_allows_admin_with_permission(mocker):
    """Test create() allows admin user with write:users permission"""
    # Arrange - Create RBAC checker requiring admin role AND write:users permission
    checker = RoleAndPermissionChecker(
        required_roles=["admin"],
        required_permissions=["write:users"]
    )
    
    # Simulate authenticated admin with write:users permission
    mock_admin_user = {
        "id": 1,
        "email": "admin@example.com",
        "role": "admin",
        "role_id": 1,
        "permissions": ["write:users"]
    }
    
    # Mock service to return created user
    input_data = UserCreate(name="NewUser", lastname="Test", email="newuser@example.com", password="hashedpass", role_id=2)
    expected_created_user = UserResponse(id=3, name="NewUser", lastname="Test", email="newuser@example.com", role_id=2)
    mock_service = mocker.patch('web.user.service.create')
    mock_service.return_value = expected_created_user
    
    # Act - First verify RBAC passes, then call create
    result_check = checker._check_role_and_permission(mock_admin_user)
    assert result_check == mock_admin_user
    
    result = await create(input_data)
    
    # Assert - Check result contains created user
    assert result.id == 3
    assert result.name == "NewUser"
    mock_service.assert_called_once()


def test_create_user_rbac_denies_non_admin(mocker):
    """Test create() denies non-admin user even with write:users permission"""
    # Arrange - Create RBAC checker requiring admin role AND write:users permission
    checker = RoleAndPermissionChecker(
        required_roles=["admin"],
        required_permissions=["write:users"]
    )
    
    # Simulate regular user with write:users permission (but not admin)
    mock_regular_user = {
        "id": 2,
        "email": "user@example.com",
        "role": "user",
        "role_id": 2,
        "permissions": ["write:users"]
    }
    
    # Act & Assert - Should raise HTTPException for lacking admin role
    with pytest.raises(HTTPException) as exc_info:
        checker._check_role_and_permission(mock_regular_user)
    
    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail


# ============================================
# Tests for GET /api/users/{id} endpoint
# ============================================


def test_get_one_by_id_success(mocker):
    """Test get_one_by_id() when user exists"""
    # Arrange - Mock service to return a user with role
    expected_user = UserResponseWithRole(
        id=1,
        name="John",
        lastname="Doe",
        email="john.doe@example.com",
        role_id=1,
        role="admin"
    )
    mock_service = mocker.patch('web.user.service.get_one_by_id')
    mock_service.return_value = expected_user
    mock_current_user = {"sub": "admin@example.com", "role": "admin"}

    # Act - Call function directly
    result = get_one_by_id(current_user=mock_current_user, user_id=1)

    # Assert - Check result contains the mocked user
    assert result.id == 1
    assert result.name == "John"
    assert result.email == "john.doe@example.com"
    assert result.role_id == 1
    assert result.role == "admin"  # role_name should be included
    mock_service.assert_called_once_with(1)


def test_get_one_by_id_not_found(mocker):
    """Test get_one_by_id() when user doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    mock_service = mocker.patch('web.user.service.get_one_by_id')
    mock_service.side_effect = NotFoundError("User with id 999 not found")
    mock_current_user = {"sub": "admin@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_one_by_id(current_user=mock_current_user, user_id=999)

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
    mock_service.assert_called_once_with(999)


def test_get_one_by_id_database_error(mocker):
    """Test get_one_by_id() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.user.service.get_one_by_id')
    mock_service.side_effect = DatabaseError("Database connection failed")
    mock_current_user = {"sub": "admin@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_one_by_id(current_user=mock_current_user, user_id=1)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once_with(1)


def test_modify_by_id_success(mocker):
    """Test modify_by_id() when user is updated successfully"""
    # Arrange - Mock service to return updated user
    from schemas.user import UserUpdate, UserResponseWithRole
    expected_user = UserResponseWithRole(
        id=1,
        name="John Updated",
        lastname="Doe",
        email="john.doe@example.com",
        role_id=2,
        role="admin"
    )
    mock_service = mocker.patch('web.user.service.modify_by_id')
    mock_service.return_value = expected_user
    mock_current_user = {"sub": "admin@example.com", "role": "admin"}
    user_update = UserUpdate(name="John Updated", role_id=2)

    # Act - Call function directly
    result = modify_by_id(current_user=mock_current_user, user_id=1, user_update=user_update)

    # Assert - Check result contains the mocked user
    assert result.id == 1
    assert result.name == "John Updated"
    assert result.role_id == 2
    assert result.role == "admin"
    mock_service.assert_called_once_with(1, user_update)


def test_modify_by_id_not_found(mocker):
    """Test modify_by_id() when user doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    from schemas.user import UserUpdate
    mock_service = mocker.patch('web.user.service.modify_by_id')
    mock_service.side_effect = NotFoundError("User with id 999 not found")
    mock_current_user = {"sub": "admin@example.com", "role": "admin"}
    user_update = UserUpdate(name="John Updated")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        modify_by_id(current_user=mock_current_user, user_id=999, user_update=user_update)

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
    mock_service.assert_called_once_with(999, user_update)


def test_modify_by_id_database_error(mocker):
    """Test modify_by_id() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    from schemas.user import UserUpdate
    mock_service = mocker.patch('web.user.service.modify_by_id')
    mock_service.side_effect = DatabaseError("Database connection failed")
    mock_current_user = {"sub": "admin@example.com", "role": "admin"}
    user_update = UserUpdate(name="John Updated")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        modify_by_id(current_user=mock_current_user, user_id=1, user_update=user_update)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once_with(1, user_update)


def test_modify_me_success(mocker):
    """Test modify_me() successfully updates current user's profile"""
    # Arrange - Mock service to return modified user
    input_data = UserProfileUpdate(name="Updated John", lastname="Doe", second_lastname="Smith", phone_number="+1234567890")
    expected_modified_user = UserResponse(id=1, name="Updated John", lastname="Doe", second_lastname="Smith", email="john.doe@example.com", phone_number="+1234567890", role_id=2)
    mock_service = mocker.patch('web.user.service.modify_by_id')
    mock_service.return_value = UserResponseWithRole(id=1, name="Updated John", lastname="Doe", second_lastname="Smith", email="john.doe@example.com", phone_number="+1234567890", role_id=2, role="user")
    mock_current_user = {"sub": "john.doe@example.com", "role": "user", "user_id": 1, "role_id": 2}

    # Act - Call function directly
    result = modify_me(current_user=mock_current_user, user_update=input_data)

    # Assert - Check result contains modified user
    assert result.id == 1
    assert result.name == "Updated John"
    mock_service.assert_called_once()
    # Verify service was called with the correct user_id from current_user
    call_args = mock_service.call_args[0]
    assert call_args[0] == 1  # user_id
    assert isinstance(call_args[1], UserUpdate)
    assert call_args[1].name == "Updated John"
    assert call_args[1].lastname == "Doe"


def test_modify_me_not_found(mocker):
    """Test modify_me() when current user doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    from exceptions import NotFoundError
    input_data = UserProfileUpdate(name="John", lastname="Doe")
    mock_service = mocker.patch('web.user.service.modify_by_id')
    mock_service.side_effect = NotFoundError("User with id 1 not found")
    mock_current_user = {"sub": "john.doe@example.com", "role": "user", "user_id": 1, "role_id": 2}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        modify_me(current_user=mock_current_user, user_update=input_data)

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
    mock_service.assert_called_once()


def test_modify_me_database_error(mocker):
    """Test modify_me() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    from exceptions import DatabaseError
    input_data = UserProfileUpdate(name="John", lastname="Doe")
    mock_service = mocker.patch('web.user.service.modify_by_id')
    mock_service.side_effect = DatabaseError("Database connection failed")
    mock_current_user = {"sub": "john.doe@example.com", "role": "user", "user_id": 1, "role_id": 2}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        modify_me(current_user=mock_current_user, user_update=input_data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once()


def test_modify_me_partial_update(mocker):
    """Test modify_me() allows partial updates (only name)"""
    # Arrange - Mock service to return modified user with partial update
    input_data = UserProfileUpdate(name="NewName")
    mock_service = mocker.patch('web.user.service.modify_by_id')
    mock_service.return_value = UserResponseWithRole(id=1, name="NewName", lastname="Doe", second_lastname=None, email="john.doe@example.com", phone_number=None, role_id=2, role="user")
    mock_current_user = {"sub": "john.doe@example.com", "role": "user", "user_id": 1, "role_id": 2}

    # Act - Call function with partial data
    result = modify_me(current_user=mock_current_user, user_update=input_data)

    # Assert - Check result
    assert result.name == "NewName"
    mock_service.assert_called_once()


def test_create_user_rbac_denies_admin_without_permission(mocker):
    """Test create() denies admin user without write:users permission"""
    # Arrange - Create RBAC checker requiring admin role AND write:users permission
    checker = RoleAndPermissionChecker(
        required_roles=["admin"],
        required_permissions=["write:users"]
    )
    
    # Simulate admin without write:users permission
    mock_admin_without_perm = {
        "id": 1,
        "email": "admin@example.com",
        "role": "admin",
        "role_id": 1,
        "permissions": ["users:read"]  # Has admin role but missing write:users
    }
    
    # Act & Assert - Should raise HTTPException for lacking permission
    with pytest.raises(HTTPException) as exc_info:
        checker._check_role_and_permission(mock_admin_without_perm)
    
    assert exc_info.value.status_code == 403
    assert "Missing required permission" in exc_info.value.detail
    assert "write:users" in exc_info.value.detail


def test_create_user_rbac_denies_non_admin_without_permission(mocker):
    """Test create() denies non-admin user without write:users permission"""
    # Arrange - Create RBAC checker requiring admin role AND write:users permission
    checker = RoleAndPermissionChecker(
        required_roles=["admin"],
        required_permissions=["write:users"]
    )
    
    # Simulate regular user without admin role or write:users permission
    mock_regular_user = {
        "id": 3,
        "email": "regular@example.com",
        "role": "user",
        "role_id": 2,
        "permissions": []
    }
    
    # Act & Assert - Should raise HTTPException for lacking admin role
    with pytest.raises(HTTPException) as exc_info:
        checker._check_role_and_permission(mock_regular_user)
    
    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail