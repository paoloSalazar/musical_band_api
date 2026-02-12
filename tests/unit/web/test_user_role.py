import pytest
from fastapi import HTTPException
from schemas.user_role import UserRole, UserRoleCreate
from web.user_role import get_all, get_one, create, modify, replace, delete
from exceptions import NotFoundError, ConflictError, DatabaseError
from auth.roles import require_admin


# ============================================
# RBAC Tests for User Roles
# ============================================


def test_require_admin_allows_admin(mocker):
    """Test require_admin allows admin user"""
    # Simulate authenticated admin user
    mock_user = {"id": 1, "email": "admin@example.com", "role": "admin"}
    
    # Act - Call require_admin with admin user
    result = require_admin._check_role(mock_user)
    
    # Assert
    assert result == mock_user


def test_require_admin_denies_user(mocker):
    """Test require_admin denies regular user"""
    # Simulate authenticated regular user
    mock_user = {"id": 2, "email": "user@example.com", "role": "user"}
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        require_admin._check_role(mock_user)
    
    assert exc_info.value.status_code == 403


def test_require_admin_denies_moderator(mocker):
    """Test require_admin denies moderator"""
    # Simulate authenticated moderator
    mock_user = {"id": 3, "email": "moderator@example.com", "role": "moderator"}
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        require_admin._check_role(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "Required role(s): admin" in exc_info.value.detail


def test_require_admin_denies_no_role(mocker):
    """Test require_admin denies user without role"""
    # Simulate authenticated user without role
    mock_user = {"id": 4, "email": "no-role@example.com"}
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        require_admin._check_role(mock_user)
    
    assert exc_info.value.status_code == 403


# ============================================
# Service-Level Tests for User Roles
# (These test the business logic without RBAC)
# ============================================


def test_get_all_roles_empty_list(mocker):
    """Test get_all() returns empty list when no roles"""
    # Arrange - Mock service to return empty list
    mock_service = mocker.patch('web.user_role.service.get_all')
    mock_service.return_value = []

    # Act - Call function directly (RBAC handled at router level)
    result = get_all()

    # Assert - Check result is empty list
    assert result == []
    mock_service.assert_called_once()


def test_get_all_roles_with_data(mocker):
    """Test get_all() returns roles when they exist"""
    # Arrange - Mock service to return specific roles
    expected_roles = [
        UserRole(id=1, name="admin", description="Administrator"),
        UserRole(id=2, name="user", description="Regular user")
    ]
    mock_service = mocker.patch('web.user_role.service.get_all')
    mock_service.return_value = expected_roles

    # Act - Call function directly
    result = get_all()

    # Assert - Check result contains the mocked data
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "admin"
    assert result[1].id == 2
    assert result[1].name == "user"
    mock_service.assert_called_once()


def test_get_one_role_found(mocker):
    """Test get_one() when role exists"""
    # Arrange - Mock service to return a specific role
    expected_role = UserRole(id=1, name="admin", description="Administrator")
    mock_service = mocker.patch('web.user_role.service.get_one')
    mock_service.return_value = expected_role

    # Act - Call function directly
    result = get_one("admin")

    # Assert - Check result contains the mocked role
    assert result.id == 1
    assert result.name == "admin"
    assert result.description == "Administrator"
    mock_service.assert_called_once_with("admin")


def test_get_one_role_not_found(mocker):
    """Test get_one() when role doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    mock_service = mocker.patch('web.user_role.service.get_one')
    mock_service.side_effect = NotFoundError("User role 'nonexistent' not found")

    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_one("nonexistent")

    assert exc_info.value.status_code == 404
    assert "User role 'nonexistent' not found" in exc_info.value.detail
    mock_service.assert_called_once_with("nonexistent")


def test_create_role_success(mocker):
    """Test create() creates and returns new role"""
    # Arrange - Mock service to return created role
    input_data = UserRoleCreate(name="moderator", description="Content moderator")
    expected_created_role = UserRole(id=3, name="moderator", description="Content moderator")
    mock_service = mocker.patch('web.user_role.service.create')
    mock_service.return_value = expected_created_role

    # Act - Call function directly
    result = create(input_data)

    # Assert - Check result contains created role
    assert result.id == 3
    assert result.name == "moderator"
    assert result.description == "Content moderator"
    mock_service.assert_called_once()


def test_create_role_conflict(mocker):
    """Test create() handles conflict when role already exists"""
    # Arrange - Mock service to raise ConflictError for duplicate role
    input_data = UserRoleCreate(name="admin", description="Duplicate admin role")
    mock_service = mocker.patch('web.user_role.service.create')
    mock_service.side_effect = ConflictError("User role 'admin' already exists")

    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        create(input_data)

    assert exc_info.value.status_code == 409
    assert "User role 'admin' already exists" in exc_info.value.detail
    mock_service.assert_called_once()


def test_modify_role_success(mocker):
    """Test modify() updates and returns modified role"""
    # Arrange - Mock service to return modified role
    input_data = UserRole(id=3, name="moderator", description="Updated moderator")
    expected_modified_role = UserRole(id=3, name="moderator", description="Updated moderator")
    mock_service = mocker.patch('web.user_role.service.modify')
    mock_service.return_value = expected_modified_role

    # Act - Call function directly
    result = modify(input_data)

    # Assert - Check result contains modified role
    assert result.id == 3
    assert result.name == "moderator"
    assert result.description == "Updated moderator"
    mock_service.assert_called_once()


def test_modify_role_not_found(mocker):
    """Test modify() when role doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    input_data = UserRole(id=1, name="nonexistent", description="Updated role")
    mock_service = mocker.patch('web.user_role.service.modify')
    mock_service.side_effect = NotFoundError("User role 'nonexistent' not found")

    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        modify(input_data)

    assert exc_info.value.status_code == 404
    assert "User role 'nonexistent' not found" in exc_info.value.detail
    mock_service.assert_called_once()


def test_replace_role_success(mocker):
    """Test replace() updates and returns replaced role"""
    # Arrange - Mock service to return replaced role
    input_data = UserRole(id=3, name="moderator", description="Replaced moderator")
    expected_replaced_role = UserRole(id=3, name="moderator", description="Replaced moderator")
    mock_service = mocker.patch('web.user_role.service.replace')
    mock_service.return_value = expected_replaced_role

    # Act - Call function directly
    result = replace(input_data)

    # Assert - Check result contains replaced role
    assert result.id == 3
    assert result.name == "moderator"
    assert result.description == "Replaced moderator"
    mock_service.assert_called_once()


def test_replace_role_not_found(mocker):
    """Test replace() when role doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    input_data = UserRole(id=1, name="nonexistent", description="Replaced role")
    mock_service = mocker.patch('web.user_role.service.replace')
    mock_service.side_effect = NotFoundError("User role with id 1 not found")

    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        replace(input_data)

    assert exc_info.value.status_code == 404
    assert "User role with id 1 not found" in exc_info.value.detail
    mock_service.assert_called_once()


def test_delete_role_success(mocker):
    """Test delete() deletes the role"""
    # Arrange - Mock service delete method
    mock_service = mocker.patch('web.user_role.service.delete')
    mock_service.return_value = None

    # Act - Call function directly
    result = delete("moderator")

    # Assert - Check result is None
    assert result is None
    mock_service.assert_called_once_with("moderator")


def test_delete_role_not_found(mocker):
    """Test delete() when role doesn't exist"""
    # Arrange - Mock service to raise NotFoundError
    mock_service = mocker.patch('web.user_role.service.delete')
    mock_service.side_effect = NotFoundError("User role 'nonexistent' not found")

    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete("nonexistent")

    assert exc_info.value.status_code == 404
    assert "User role 'nonexistent' not found" in exc_info.value.detail
    mock_service.assert_called_once_with("nonexistent")


def test_get_all_database_error(mocker):
    """Test get_all() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.user_role.service.get_all')
    mock_service.side_effect = DatabaseError("Database connection failed")

    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_all()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error"
    mock_service.assert_called_once()
