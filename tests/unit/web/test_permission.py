import pytest
from fastapi import HTTPException
from schemas.permission import PermissionResponse, RolePermissionCreate
from web.permission import (
    get_role_permissions,
    get_permission_roles,
    assign_permission_to_role,
    remove_permission_from_role,
)
from exceptions import NotFoundError, DatabaseError


def test_get_role_permissions_empty_list(mocker):
    """Test get_role_permissions() returns empty list when role has no permissions"""
    # Arrange - Mock service to return empty list
    mock_service = mocker.patch('web.permission.service.get_role_permissions')
    mock_service.return_value = []

    # Act - Call function directly
    result = get_role_permissions(role_id=1)

    # Assert - Check result is empty list
    assert result == []
    mock_service.assert_called_once_with(1)


def test_get_role_permissions_with_data(mocker):
    """Test get_role_permissions() returns permissions when they exist"""
    # Arrange - Mock service to return specific permissions
    expected_permissions = [
        PermissionResponse(id=1, name="read:users", description="Read users"),
        PermissionResponse(id=2, name="write:users", description="Write users"),
    ]
    mock_service = mocker.patch('web.permission.service.get_role_permissions')
    mock_service.return_value = expected_permissions

    # Act - Call function directly
    result = get_role_permissions(role_id=1)

    # Assert - Check result contains the mocked data
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "read:users"
    assert result[1].id == 2
    assert result[1].name == "write:users"
    mock_service.assert_called_once_with(1)


def test_get_role_permissions_database_error(mocker):
    """Test get_role_permissions() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.get_role_permissions')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_role_permissions(role_id=1)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once_with(1)


def test_get_permission_roles_empty_list(mocker):
    """Test get_permission_roles() returns empty list when permission has no roles"""
    # Arrange - Mock service to return empty list
    mock_service = mocker.patch('web.permission.service.get_permission_roles')
    mock_service.return_value = []

    # Act - Call function directly
    result = get_permission_roles(permission_id=1)

    # Assert - Check result is empty list
    assert result == []
    mock_service.assert_called_once_with(1)


def test_get_permission_roles_with_data(mocker):
    """Test get_permission_roles() returns roles when they exist"""
    # Arrange - Mock service to return specific roles
    from models.user_role import UserRole
    expected_roles = [
        UserRole(id=1, name="admin", description="Administrator"),
        UserRole(id=2, name="moderator", description="Moderator"),
    ]
    mock_service = mocker.patch('web.permission.service.get_permission_roles')
    mock_service.return_value = expected_roles

    # Act - Call function directly
    result = get_permission_roles(permission_id=1)

    # Assert - Check result contains the mocked data
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "admin"
    assert result[1].id == 2
    assert result[1].name == "moderator"
    mock_service.assert_called_once_with(1)


def test_get_permission_roles_database_error(mocker):
    """Test get_permission_roles() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.get_permission_roles')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_permission_roles(permission_id=1)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once_with(1)


def test_assign_permission_to_role_success(mocker):
    """Test assign_permission_to_role() success"""
    # Arrange - Mock service to return True
    mock_service = mocker.patch('web.permission.service.assign_permission_to_role')
    mock_service.return_value = True

    # Act - Call function directly
    result = assign_permission_to_role(permission_id=1, role_id=2)

    # Assert - Check result contains success and message
    assert result["success"] is True
    assert result["message"] == "Permission 1 assigned to role 2"
    mock_service.assert_called_once_with(1, 2)


def test_assign_permission_to_role_database_error(mocker):
    """Test assign_permission_to_role() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.assign_permission_to_role')
    mock_service.side_effect = DatabaseError("Failed to assign permission")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        assign_permission_to_role(permission_id=1, role_id=2)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once_with(1, 2)


def test_remove_permission_from_role_success(mocker):
    """Test remove_permission_from_role() success"""
    # Arrange - Mock service to return True
    mock_service = mocker.patch('web.permission.service.remove_permission_from_role')
    mock_service.return_value = True

    # Act - Call function directly
    result = remove_permission_from_role(permission_id=1, role_id=2)

    # Assert - Check result contains success and message
    assert result["success"] is True
    assert result["message"] == "Permission 1 removed from role 2"
    mock_service.assert_called_once_with(1, 2)


def test_remove_permission_from_role_database_error(mocker):
    """Test remove_permission_from_role() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.permission.service.remove_permission_from_role')
    mock_service.side_effect = DatabaseError("Failed to remove permission")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        remove_permission_from_role(permission_id=1, role_id=2)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once_with(1, 2)
