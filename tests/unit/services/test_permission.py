import pytest
from unittest.mock import Mock, patch, MagicMock
from services.permission import (
    assign_permission_to_role,
    remove_permission_from_role,
    get_role_permissions,
    get_permission_roles,
)
from exceptions import NotFoundError, DatabaseError
from models.permission import Permission
from models.user_role import UserRole
from schemas.permission import PermissionResponse


def test_assign_permission_to_role_success(mocker):
    """Test assign_permission_to_role() success"""
    # Arrange
    mock_data_assign = mocker.patch('services.permission.data.assign_permission_to_role')
    mock_data_assign.return_value = True

    # Act
    result = assign_permission_to_role(permission_id=1, role_id=2)

    # Assert
    assert result is True
    mock_data_assign.assert_called_once_with(1, 2)


def test_assign_permission_to_role_database_error(mocker):
    """Test assign_permission_to_role() raises DatabaseError on failure"""
    # Arrange
    mock_data_assign = mocker.patch('services.permission.data.assign_permission_to_role')
    mock_data_assign.side_effect = DatabaseError("Failed to assign permission")

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        assign_permission_to_role(permission_id=1, role_id=2)

    assert "Failed to assign permission" in str(exc_info.value)


def test_remove_permission_from_role_success(mocker):
    """Test remove_permission_from_role() success"""
    # Arrange
    mock_data_remove = mocker.patch('services.permission.data.remove_permission_from_role')
    mock_data_remove.return_value = True

    # Act
    result = remove_permission_from_role(permission_id=1, role_id=2)

    # Assert
    assert result is True
    mock_data_remove.assert_called_once_with(1, 2)


def test_remove_permission_from_role_database_error(mocker):
    """Test remove_permission_from_role() raises DatabaseError on failure"""
    # Arrange
    mock_data_remove = mocker.patch('services.permission.data.remove_permission_from_role')
    mock_data_remove.side_effect = DatabaseError("Failed to remove permission")

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        remove_permission_from_role(permission_id=1, role_id=2)

    assert "Failed to remove permission" in str(exc_info.value)


def test_get_role_permissions_success(mocker):
    """Test get_role_permissions() returns list of PermissionResponse"""
    # Arrange
    mock_permissions = [
        Permission(id=1, name="read:users", description="Read users"),
        Permission(id=2, name="write:users", description="Write users"),
    ]
    mock_data_get = mocker.patch('services.permission.data.get_role_permissions')
    mock_data_get.return_value = mock_permissions

    # Act
    result = get_role_permissions(role_id=1)

    # Assert
    assert len(result) == 2
    assert isinstance(result[0], PermissionResponse)
    assert result[0].id == 1
    assert result[0].name == "read:users"
    assert result[1].id == 2
    assert result[1].name == "write:users"
    mock_data_get.assert_called_once_with(1)


def test_get_role_permissions_empty(mocker):
    """Test get_role_permissions() returns empty list"""
    # Arrange
    mock_data_get = mocker.patch('services.permission.data.get_role_permissions')
    mock_data_get.return_value = []

    # Act
    result = get_role_permissions(role_id=999)

    # Assert
    assert result == []
    mock_data_get.assert_called_once_with(999)


def test_get_role_permissions_database_error(mocker):
    """Test get_role_permissions() raises DatabaseError on failure"""
    # Arrange
    mock_data_get = mocker.patch('services.permission.data.get_role_permissions')
    mock_data_get.side_effect = DatabaseError("Failed to get role permissions")

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        get_role_permissions(role_id=1)

    assert "Failed to get role permissions" in str(exc_info.value)


def test_get_permission_roles_success(mocker):
    """Test get_permission_roles() returns list of UserRole objects"""
    # Arrange
    mock_roles = [
        UserRole(id=1, name="admin", description="Administrator"),
        UserRole(id=2, name="moderator", description="Moderator"),
    ]
    mock_data_get = mocker.patch('services.permission.data.get_permission_roles')
    mock_data_get.return_value = mock_roles

    # Act
    result = get_permission_roles(permission_id=1)

    # Assert
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "admin"
    assert result[1].id == 2
    assert result[1].name == "moderator"
    mock_data_get.assert_called_once_with(1)


def test_get_permission_roles_empty(mocker):
    """Test get_permission_roles() returns empty list"""
    # Arrange
    mock_data_get = mocker.patch('services.permission.data.get_permission_roles')
    mock_data_get.return_value = []

    # Act
    result = get_permission_roles(permission_id=999)

    # Assert
    assert result == []
    mock_data_get.assert_called_once_with(999)


def test_get_permission_roles_database_error(mocker):
    """Test get_permission_roles() raises DatabaseError on failure"""
    # Arrange
    mock_data_get = mocker.patch('services.permission.data.get_permission_roles')
    mock_data_get.side_effect = DatabaseError("Failed to get permission roles")

    # Act & Assert
    with pytest.raises(DatabaseError) as exc_info:
        get_permission_roles(permission_id=1)

    assert "Failed to get permission roles" in str(exc_info.value)
