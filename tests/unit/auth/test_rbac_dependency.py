import pytest
from fastapi import HTTPException
from auth.roles import RoleChecker, PermissionChecker, RoleOrPermissionChecker


def test_role_checker_allows_admin():
    """Test RoleChecker allows admin user"""
    # Arrange - Create role checker for admin
    checker = RoleChecker(allowed_roles=["admin"])
    
    # Simulate authenticated user
    mock_user = {"id": 1, "email": "admin@example.com", "role": "admin"}
    
    # Act - Call the checker directly with mock user
    # Since get_current_user is a dependency, we test the logic by calling with mock
    result = checker._check_role(mock_user)
    
    # Assert - Should return the user
    assert result == mock_user


def test_role_checker_denies_wrong_role():
    """Test RoleChecker denies non-admin user"""
    # Arrange - Create role checker for admin
    checker = RoleChecker(allowed_roles=["admin"])
    
    # Simulate authenticated user
    mock_user = {"id": 2, "email": "user@example.com", "role": "user"}
    
    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        checker._check_role(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail


def test_role_checker_denies_no_role():
    """Test RoleChecker denies user without role"""
    # Arrange - Create role checker for admin
    checker = RoleChecker(allowed_roles=["admin"])
    
    # Simulate authenticated user without role
    mock_user = {"id": 3, "email": "no-role@example.com"}
    
    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        checker._check_role(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "User role not found" in exc_info.value.detail


def test_role_checker_allows_multiple_roles():
    """Test RoleChecker allows user with one of multiple allowed roles"""
    # Arrange - Create role checker for admin or moderator
    checker = RoleChecker(allowed_roles=["admin", "moderator"])
    
    # Simulate authenticated moderator
    mock_user = {"id": 4, "email": "moderator@example.com", "role": "moderator"}
    
    # Act - Call the checker
    result = checker._check_role(mock_user)
    
    # Assert - Should return the user
    assert result == mock_user


def test_role_checker_denies_not_in_allowed_roles():
    """Test RoleChecker denies user with role not in allowed list"""
    # Arrange - Create role checker for admin or moderator
    checker = RoleChecker(allowed_roles=["admin", "moderator"])
    
    # Simulate authenticated guest
    mock_user = {"id": 5, "email": "guest@example.com", "role": "guest"}
    
    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        checker._check_role(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "Required role(s): admin, moderator" in exc_info.value.detail


def test_role_checker_superadmin_denied():
    """Test RoleChecker denies superadmin when only admin is allowed"""
    # Arrange - Create role checker for admin only
    checker = RoleChecker(allowed_roles=["admin"])
    
    # Simulate authenticated superadmin
    mock_user = {"id": 6, "email": "superadmin@example.com", "role": "superadmin"}
    
    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        checker._check_role(mock_user)
    
    assert exc_info.value.status_code == 403


def test_require_admin_allows_admin():
    """Test require_admin allows admin user"""
    # Import and use require_admin
    from auth.roles import require_admin
    
    # Simulate authenticated admin user
    mock_user = {"id": 1, "email": "admin@example.com", "role": "admin"}
    
    # Act - Call require_admin with mock user
    result = require_admin._check_role(mock_user)
    
    # Assert
    assert result == mock_user


def test_require_admin_denies_user():
    """Test require_admin denies regular user"""
    from auth.roles import require_admin
    
    # Simulate authenticated regular user
    mock_user = {"id": 2, "email": "user@example.com", "role": "user"}
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        require_admin._check_role(mock_user)
    
    assert exc_info.value.status_code == 403


def test_require_admin_denies_moderator():
    """Test require_admin denies moderator"""
    from auth.roles import require_admin
    
    # Simulate authenticated moderator
    mock_user = {"id": 3, "email": "moderator@example.com", "role": "moderator"}
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        require_admin._check_role(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "Required role(s): admin" in exc_info.value.detail


# ============================================
# PermissionChecker Tests
# ============================================


def test_permission_checker_allows_user_with_permission():
    """Test PermissionChecker allows user with required permission"""
    # Arrange - Create permission checker for users:read
    checker = PermissionChecker(required_permissions=["users:read"])
    
    # Simulate authenticated user with users:read permission
    mock_user = {
        "id": 1, 
        "email": "user@example.com", 
        "role": "user",
        "permissions": ["users:read"]
    }
    
    # Act - Call the checker directly with mock user
    result = checker._check_permission(mock_user)
    
    # Assert - Should return the user
    assert result == mock_user


def test_permission_checker_denies_user_without_permission():
    """Test PermissionChecker denies user without required permission"""
    # Arrange - Create permission checker for users:write
    checker = PermissionChecker(required_permissions=["users:write"])
    
    # Simulate authenticated user without users:write permission
    mock_user = {
        "id": 2, 
        "email": "user@example.com", 
        "role": "user",
        "permissions": ["users:read"]
    }
    
    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        checker._check_permission(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "Missing required permission(s): users:write" in exc_info.value.detail


def test_permission_checker_denies_user_with_no_permissions():
    """Test PermissionChecker denies user with no permissions list"""
    # Arrange - Create permission checker for users:read
    checker = PermissionChecker(required_permissions=["users:read"])
    
    # Simulate authenticated user without permissions
    mock_user = {"id": 3, "email": "user@example.com", "role": "user"}
    
    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        checker._check_permission(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "Missing required permission(s): users:read" in exc_info.value.detail


def test_permission_checker_allows_multiple_permissions():
    """Test PermissionChecker allows user with all required permissions"""
    # Arrange - Create permission checker requiring multiple permissions
    checker = PermissionChecker(required_permissions=["users:read", "users:write"])
    
    # Simulate authenticated user with both permissions
    mock_user = {
        "id": 4, 
        "email": "admin@example.com", 
        "role": "admin",
        "permissions": ["users:read", "users:write", "users:delete"]
    }
    
    # Act - Call the checker
    result = checker._check_permission(mock_user)
    
    # Assert - Should return the user
    assert result == mock_user


def test_permission_checker_denies_missing_one_permission():
    """Test PermissionChecker denies user missing one of multiple required permissions"""
    # Arrange - Create permission checker requiring multiple permissions
    checker = PermissionChecker(required_permissions=["users:read", "users:write", "users:delete"])
    
    # Simulate authenticated user missing one permission
    mock_user = {
        "id": 5, 
        "email": "user@example.com", 
        "role": "user",
        "permissions": ["users:read", "users:write"]
    }
    
    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        checker._check_permission(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "users:delete" in exc_info.value.detail


def test_require_users_read_allows_user_with_permission():
    """Test require_users_read allows user with users:read permission"""
    from auth.roles import require_users_read
    
    # Simulate authenticated user with users:read permission
    mock_user = {
        "id": 1, 
        "email": "user@example.com", 
        "role": "user",
        "permissions": ["users:read"]
    }
    
    # Act - Call require_users_read with mock user
    result = require_users_read._check_permission(mock_user)
    
    # Assert
    assert result == mock_user


def test_require_users_read_denies_user_without_permission():
    """Test require_users_read denies user without users:read permission"""
    from auth.roles import require_users_read
    
    # Simulate authenticated user without users:read permission
    mock_user = {
        "id": 2, 
        "email": "user@example.com", 
        "role": "user",
        "permissions": []
    }
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        require_users_read._check_permission(mock_user)
    
    assert exc_info.value.status_code == 403


# ============================================
# RoleOrPermissionChecker Tests
# ============================================


def test_role_or_permission_checker_allows_with_role():
    """Test RoleOrPermissionChecker allows user with required role"""
    # Arrange - Create checker requiring admin role OR users:delete permission
    checker = RoleOrPermissionChecker(
        allowed_roles=["admin"], 
        required_permissions=["users:delete"]
    )
    
    # Simulate authenticated admin (has role, no permission needed)
    mock_user = {
        "id": 1, 
        "email": "admin@example.com", 
        "role": "admin",
        "permissions": []
    }
    
    # Act - Call the checker directly with mock user
    result = checker._check_role_or_permission(mock_user)
    
    # Assert - Should return the user
    assert result == mock_user


def test_role_or_permission_checker_allows_with_permission():
    """Test RoleOrPermissionChecker allows user with required permission"""
    # Arrange - Create checker requiring admin role OR users:delete permission
    checker = RoleOrPermissionChecker(
        allowed_roles=["admin"], 
        required_permissions=["users:delete"]
    )
    
    # Simulate authenticated user (no admin role but has permission)
    mock_user = {
        "id": 2, 
        "email": "moderator@example.com", 
        "role": "moderator",
        "permissions": ["users:delete"]
    }
    
    # Act - Call the checker directly with mock user
    result = checker._check_role_or_permission(mock_user)
    
    # Assert - Should return the user
    assert result == mock_user


def test_role_or_permission_checker_denies_without_role_or_permission():
    """Test RoleOrPermissionChecker denies user without role or permission"""
    # Arrange - Create checker requiring admin role OR users:delete permission
    checker = RoleOrPermissionChecker(
        allowed_roles=["admin"], 
        required_permissions=["users:delete"]
    )
    
    # Simulate authenticated regular user (no admin role, no users:delete)
    mock_user = {
        "id": 3, 
        "email": "user@example.com", 
        "role": "user",
        "permissions": ["users:read"]
    }
    
    # Act & Assert - Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        checker._check_role_or_permission(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "admin" in exc_info.value.detail
    assert "users:delete" in exc_info.value.detail


def test_role_or_permission_checker_allows_with_multiple_roles():
    """Test RoleOrPermissionChecker allows user with one of multiple allowed roles"""
    # Arrange - Create checker requiring admin OR moderator role
    checker = RoleOrPermissionChecker(
        allowed_roles=["admin", "moderator"], 
        required_permissions=[]
    )
    
    # Simulate authenticated moderator
    mock_user = {
        "id": 4, 
        "email": "moderator@example.com", 
        "role": "moderator",
        "permissions": []
    }
    
    # Act - Call the checker
    result = checker._check_role_or_permission(mock_user)
    
    # Assert - Should return the user
    assert result == mock_user


def test_role_or_permission_checker_allows_with_multiple_permissions():
    """Test RoleOrPermissionChecker allows user with any of multiple required permissions"""
    # Arrange - Create checker requiring any of multiple permissions
    checker = RoleOrPermissionChecker(
        allowed_roles=[], 
        required_permissions=["users:read", "users:write", "users:delete"]
    )
    
    # Simulate authenticated user with only users:write
    mock_user = {
        "id": 5, 
        "email": "user@example.com", 
        "role": "user",
        "permissions": ["users:write"]
    }
    
    # Act - Call the checker
    result = checker._check_role_or_permission(mock_user)
    
    # Assert - Should return the user
    assert result == mock_user
