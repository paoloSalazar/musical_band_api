import pytest
from fastapi import HTTPException
from auth.roles import RoleChecker


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
