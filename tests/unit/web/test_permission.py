import pytest
from fastapi import HTTPException
from schemas.permission import PermissionResponse, PermissionCreate, PermissionUpdate, RolePermissionCreate
from web.permission import (
    get_all,
    get_one,
    create,
    update,
    delete,
    get_role_permissions,
    get_permission_roles,
    assign_permission_to_role,
    remove_permission_from_role,
)
from exceptions import NotFoundError, ConflictError, DatabaseError


# ============================================
# Role-Permission Endpoint Tests
# ============================================


def test_get_role_permissions_empty_list(mocker):
    """Test get_role_permissions() returns empty list when role has no permissions"""
    # Arrange - Mock data.user_role.get_one to return a role
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = mocker.MagicMock(id=1, name="admin")
    
    # Mock service to return empty list
    mock_service = mocker.patch('web.permission.service.get_role_permissions')
    mock_service.return_value = []

    # Act - Call function directly
    result = get_role_permissions(role_name="admin")

    # Assert - Check result is empty list
    assert result == []
    mock_get_role.assert_called_once_with("admin")
    mock_service.assert_called_once_with(1)


def test_get_role_permissions_with_data(mocker):
    """Test get_role_permissions() returns permissions when they exist"""
    # Arrange - Mock data.user_role.get_one to return a role
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = mocker.MagicMock(id=1, name="admin")
    
    # Mock service to return specific permissions
    expected_permissions = [
        PermissionResponse(id=1, name="users:read", description="Read users"),
        PermissionResponse(id=2, name="users:write", description="Write users"),
    ]
    mock_service = mocker.patch('web.permission.service.get_role_permissions')
    mock_service.return_value = expected_permissions

    # Act - Call function directly
    result = get_role_permissions(role_name="admin")

    # Assert - Check result contains the mocked data
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "users:read"
    assert result[1].id == 2
    assert result[1].name == "users:write"
    mock_get_role.assert_called_once_with("admin")
    mock_service.assert_called_once_with(1)


def test_get_role_permissions_role_not_found(mocker):
    """Test get_role_permissions() returns 404 when role doesn't exist"""
    # Arrange - Mock data.user_role.get_one to return None
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = None

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_role_permissions(role_name="nonexistent")

    assert exc_info.value.status_code == 404
    assert "Role 'nonexistent' not found" in exc_info.value.detail


def test_get_role_permissions_database_error(mocker):
    """Test get_role_permissions() handles database errors"""
    # Arrange - Mock data.user_role.get_one to return a role
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = mocker.MagicMock(id=1, name="admin")
    
    # Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.get_role_permissions')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_role_permissions(role_name="admin")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_get_role.assert_called_once_with("admin")
    mock_service.assert_called_once_with(1)


def test_get_permission_roles_empty_list(mocker):
    """Test get_permission_roles() returns empty list when permission has no roles"""
    # Arrange - Mock service.get_by_name to return a permission
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = mocker.MagicMock(id=1, name="users:read")
    
    # Mock service to return empty list
    mock_service = mocker.patch('web.permission.service.get_permission_roles')
    mock_service.return_value = []

    # Act - Call function directly
    result = get_permission_roles(permission_name="users:read")

    # Assert - Check result is empty list
    assert result == []
    mock_get_permission.assert_called_once_with("users:read")
    mock_service.assert_called_once_with(1)


def test_get_permission_roles_with_data(mocker):
    """Test get_permission_roles() returns roles when they exist"""
    # Arrange - Mock service.get_by_name to return a permission
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = mocker.MagicMock(id=1, name="users:read")
    
    # Mock service to return specific roles
    from models.user_role import UserRole
    expected_roles = [
        UserRole(id=1, name="admin", description="Administrator"),
        UserRole(id=2, name="moderator", description="Moderator"),
    ]
    mock_service = mocker.patch('web.permission.service.get_permission_roles')
    mock_service.return_value = expected_roles

    # Act - Call function directly
    result = get_permission_roles(permission_name="users:read")

    # Assert - Check result contains the mocked data
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "admin"
    assert result[1].id == 2
    assert result[1].name == "moderator"
    mock_get_permission.assert_called_once_with("users:read")
    mock_service.assert_called_once_with(1)


def test_get_permission_roles_permission_not_found(mocker):
    """Test get_permission_roles() returns 404 when permission doesn't exist"""
    # Arrange - Mock service.get_by_name to return None
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = None

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_permission_roles(permission_name="nonexistent:permission")

    assert exc_info.value.status_code == 404
    assert "Permission 'nonexistent:permission' not found" in exc_info.value.detail


def test_get_permission_roles_database_error(mocker):
    """Test get_permission_roles() handles database errors"""
    # Arrange - Mock service.get_by_name to return a permission
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = mocker.MagicMock(id=1, name="users:read")
    
    # Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.get_permission_roles')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_permission_roles(permission_name="users:read")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_get_permission.assert_called_once_with("users:read")
    mock_service.assert_called_once_with(1)


def test_assign_permission_to_role_success(mocker):
    """Test assign_permission_to_role() success"""
    # Arrange - Mock service.get_by_name to return a permission
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = mocker.MagicMock(id=1, name="users:read")
    
    # Mock data.user_role.get_one to return a role
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = mocker.MagicMock(id=1, name="admin")
    
    # Mock service to return True
    mock_service = mocker.patch('web.permission.service.assign_permission_to_role')
    mock_service.return_value = True

    # Act - Call function directly
    result = assign_permission_to_role(permission_name="users:read", role_name="admin")

    # Assert - Check result contains success and message
    assert result["success"] is True
    assert result["message"] == "Permission 'users:read' assigned to role 'admin'"
    mock_get_permission.assert_called_once_with("users:read")
    mock_get_role.assert_called_once_with("admin")
    mock_service.assert_called_once_with(1, 1)


def test_assign_permission_to_role_permission_not_found(mocker):
    """Test assign_permission_to_role() returns 404 when permission doesn't exist"""
    # Arrange - Mock service.get_by_name to return None
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = None

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        assign_permission_to_role(permission_name="nonexistent:perm", role_name="admin")

    assert exc_info.value.status_code == 404
    assert "Permission 'nonexistent:perm' not found" in exc_info.value.detail


def test_assign_permission_to_role_role_not_found(mocker):
    """Test assign_permission_to_role() returns 404 when role doesn't exist"""
    # Arrange - Mock service.get_by_name to return a permission
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = mocker.MagicMock(id=1, name="users:read")
    
    # Mock data.user_role.get_one to return None
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = None

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        assign_permission_to_role(permission_name="users:read", role_name="nonexistent")

    assert exc_info.value.status_code == 404
    assert "Role 'nonexistent' not found" in exc_info.value.detail


def test_assign_permission_to_role_database_error(mocker):
    """Test assign_permission_to_role() handles database errors"""
    # Arrange - Mock service.get_by_name to return a permission
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = mocker.MagicMock(id=1, name="users:read")
    
    # Mock data.user_role.get_one to return a role
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = mocker.MagicMock(id=1, name="admin")
    
    # Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.assign_permission_to_role')
    mock_service.side_effect = DatabaseError("Failed to assign permission")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        assign_permission_to_role(permission_name="users:read", role_name="admin")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"


def test_remove_permission_from_role_success(mocker):
    """Test remove_permission_from_role() success"""
    # Arrange - Mock service.get_by_name to return a permission
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = mocker.MagicMock(id=1, name="users:read")
    
    # Mock data.user_role.get_one to return a role
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = mocker.MagicMock(id=1, name="admin")
    
    # Mock service to return True
    mock_service = mocker.patch('web.permission.service.remove_permission_from_role')
    mock_service.return_value = True

    # Act - Call function directly
    result = remove_permission_from_role(permission_name="users:read", role_name="admin")

    # Assert - Check result contains success and message
    assert result["success"] is True
    assert result["message"] == "Permission 'users:read' removed from role 'admin'"
    mock_get_permission.assert_called_once_with("users:read")
    mock_get_role.assert_called_once_with("admin")
    mock_service.assert_called_once_with(1, 1)


def test_remove_permission_from_role_permission_not_found(mocker):
    """Test remove_permission_from_role() returns 404 when permission doesn't exist"""
    # Arrange - Mock service.get_by_name to return None
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = None

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        remove_permission_from_role(permission_name="nonexistent:perm", role_name="admin")

    assert exc_info.value.status_code == 404
    assert "Permission 'nonexistent:perm' not found" in exc_info.value.detail


def test_remove_permission_from_role_role_not_found(mocker):
    """Test remove_permission_from_role() returns 404 when role doesn't exist"""
    # Arrange - Mock service.get_by_name to return a permission
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = mocker.MagicMock(id=1, name="users:read")
    
    # Mock data.user_role.get_one to return None
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = None

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        remove_permission_from_role(permission_name="users:read", role_name="nonexistent")

    assert exc_info.value.status_code == 404
    assert "Role 'nonexistent' not found" in exc_info.value.detail


def test_remove_permission_from_role_database_error(mocker):
    """Test remove_permission_from_role() handles database errors"""
    # Arrange - Mock service.get_by_name to return a permission
    mock_get_permission = mocker.patch('web.permission.service.get_by_name')
    mock_get_permission.return_value = mocker.MagicMock(id=1, name="users:read")
    
    # Mock data.user_role.get_one to return a role
    mock_get_role = mocker.patch('web.permission.get_role_by_name')
    mock_get_role.return_value = mocker.MagicMock(id=1, name="admin")
    
    # Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.remove_permission_from_role')
    mock_service.side_effect = DatabaseError("Failed to remove permission")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        remove_permission_from_role(permission_name="users:read", role_name="admin")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"


# ============================================
# Permission CRUD Endpoint Tests
# ============================================


def test_get_all_permissions_empty_list(mocker):
    """Test get_all() returns empty list when no permissions"""
    # Arrange - Mock service to return empty list
    mock_service = mocker.patch('web.permission.service.get_all')
    mock_service.return_value = []

    # Act - Call function directly
    result = get_all()

    # Assert - Check result is empty list
    assert result == []
    mock_service.assert_called_once()


def test_get_all_permissions_with_data(mocker):
    """Test get_all() returns permissions when they exist"""
    # Arrange - Mock service to return specific permissions
    expected_permissions = [
        PermissionResponse(id=1, name="read:users", description="Read users"),
        PermissionResponse(id=2, name="write:users", description="Write users"),
    ]
    mock_service = mocker.patch('web.permission.service.get_all')
    mock_service.return_value = expected_permissions

    # Act - Call function directly
    result = get_all()

    # Assert - Check result contains the mocked data
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "read:users"
    assert result[1].id == 2
    assert result[1].name == "write:users"
    mock_service.assert_called_once()


def test_get_all_permissions_database_error(mocker):
    """Test get_all() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.get_all')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_all()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once()


def test_get_one_permission_found(mocker):
    """Test get_one() when permission exists"""
    # Arrange - Mock service to return a specific permission
    expected_permission = PermissionResponse(id=1, name="read:users", description="Read users")
    mock_service = mocker.patch('web.permission.service.get_one')
    mock_service.return_value = expected_permission

    # Act - Call function directly
    result = get_one(permission_id=1)

    # Assert - Check result contains the mocked permission
    assert result.id == 1
    assert result.name == "read:users"
    assert result.description == "Read users"
    mock_service.assert_called_once_with(1)


def test_get_one_permission_not_found(mocker):
    """Test get_one() when permission doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    mock_service = mocker.patch('web.permission.service.get_one')
    mock_service.side_effect = NotFoundError("Permission with ID 99 not found")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_one(permission_id=99)

    assert exc_info.value.status_code == 404
    assert "Permission with ID 99 not found" in exc_info.value.detail
    mock_service.assert_called_once_with(99)


def test_get_one_permission_database_error(mocker):
    """Test get_one() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.get_one')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_one(permission_id=1)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once_with(1)


def test_create_permission_success(mocker):
    """Test create() creates and returns new permission"""
    # Arrange - Mock service to return created permission
    input_data = PermissionCreate(name="delete:users", description="Delete users")
    expected_created_permission = PermissionResponse(id=3, name="delete:users", description="Delete users")
    mock_service = mocker.patch('web.permission.service.create')
    mock_service.return_value = expected_created_permission

    # Act - Call function directly
    result = create(permission=input_data)

    # Assert - Check result contains created permission
    assert result.id == 3
    assert result.name == "delete:users"
    assert result.description == "Delete users"
    mock_service.assert_called_once()


def test_create_permission_conflict(mocker):
    """Test create() handles conflict when permission already exists"""
    # Arrange - Mock service to raise ConflictError
    input_data = PermissionCreate(name="read:users", description="Duplicate permission")
    mock_service = mocker.patch('web.permission.service.create')
    mock_service.side_effect = ConflictError("Permission with name 'read:users' already exists")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        create(permission=input_data)

    assert exc_info.value.status_code == 409
    assert "Permission with name 'read:users' already exists" in exc_info.value.detail
    mock_service.assert_called_once()


def test_create_permission_database_error(mocker):
    """Test create() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    input_data = PermissionCreate(name="new:permission", description="New permission")
    mock_service = mocker.patch('web.permission.service.create')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        create(permission=input_data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once()


def test_update_permission_success(mocker):
    """Test update() updates and returns modified permission"""
    # Arrange - Mock service to return updated permission
    input_data = PermissionUpdate(description="Updated description")
    expected_updated_permission = PermissionResponse(id=1, name="read:users", description="Updated description")
    mock_service = mocker.patch('web.permission.service.update')
    mock_service.return_value = expected_updated_permission

    # Act - Call function directly
    result = update(permission_id=1, permission_update=input_data)

    # Assert - Check result contains updated permission
    assert result.id == 1
    assert result.name == "read:users"
    assert result.description == "Updated description"
    mock_service.assert_called_once_with(1, input_data)


def test_update_permission_not_found(mocker):
    """Test update() when permission doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    input_data = PermissionUpdate(description="Updated description")
    mock_service = mocker.patch('web.permission.service.update')
    mock_service.side_effect = NotFoundError("Permission with ID 99 not found")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        update(permission_id=99, permission_update=input_data)

    assert exc_info.value.status_code == 404
    assert "Permission with ID 99 not found" in exc_info.value.detail
    mock_service.assert_called_once()


def test_update_permission_database_error(mocker):
    """Test update() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    input_data = PermissionUpdate(description="Updated description")
    mock_service = mocker.patch('web.permission.service.update')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        update(permission_id=1, permission_update=input_data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once()


def test_delete_permission_success(mocker):
    """Test delete() deletes the permission"""
    # Arrange - Mock service delete method
    mock_service = mocker.patch('web.permission.service.delete')
    mock_service.return_value = True

    # Act - Call function directly
    result = delete(permission_id=1)

    # Assert - Check result is True
    assert result is True
    mock_service.assert_called_once_with(1)


def test_delete_permission_not_found(mocker):
    """Test delete() when permission doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    mock_service = mocker.patch('web.permission.service.delete')
    mock_service.side_effect = NotFoundError("Permission with ID 99 not found")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete(permission_id=99)

    assert exc_info.value.status_code == 404
    assert "Permission with ID 99 not found" in exc_info.value.detail
    mock_service.assert_called_once_with(99)


def test_delete_permission_database_error(mocker):
    """Test delete() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.delete')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete(permission_id=1)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once_with(1)
