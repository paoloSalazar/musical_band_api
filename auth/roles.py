"""Role-Based Access Control (RBAC) dependencies for FastAPI."""

from fastapi import Depends, HTTPException, status
from auth.auth import get_current_user


class RoleChecker:
    """Dependency class that checks if the user has the required role."""

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def _check_role(self, user: dict) -> dict:
        """Check if the user's role is in the allowed roles list (for testing)."""
        user_role = user.get("role")
        
        if user_role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not found"
            )
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(self.allowed_roles)}"
            )
        
        return user

    async def __call__(self, user: dict = Depends(get_current_user)):
        """Check if the user's role is in the allowed roles list."""
        return self._check_role(user)


# Pre-defined role checkers for common use cases
require_admin = RoleChecker(allowed_roles=["admin"])
require_admin_or_moderator = RoleChecker(allowed_roles=["admin", "moderator"])
require_any_role = RoleChecker(allowed_roles=["admin", "moderator", "user"])


# ============================================
# Permission Checker Classes
# ============================================


class PermissionChecker:
    """Dependency class that checks if user has required permission(s)."""

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def _check_permission(self, user: dict) -> dict:
        """Check if user has all required permissions (for testing)."""
        user_permissions = user.get("permissions", [])
        
        missing_permissions = [
            perm for perm in self.required_permissions 
            if perm not in user_permissions
        ]
        
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission(s): {', '.join(missing_permissions)}"
            )
        
        return user

    async def __call__(self, user: dict = Depends(get_current_user)) -> dict:
        """Check if user has all required permissions."""
        return self._check_permission(user)


class RoleOrPermissionChecker:
    """Dependency class that checks if user has required role OR permission."""

    def __init__(self, allowed_roles: list[str], required_permissions: list[str]):
        self.allowed_roles = allowed_roles
        self.required_permissions = required_permissions

    def _check_role_or_permission(self, user: dict) -> dict:
        """Check if user has required role OR any of the required permissions (for testing)."""
        user_role = user.get("role")
        user_permissions = user.get("permissions", [])
        
        has_allowed_role = user_role in self.allowed_roles
        has_required_permission = any(
            perm in user_permissions for perm in self.required_permissions
        )
        
        if not has_allowed_role and not has_required_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(self.allowed_roles)} "
                       f"OR permission(s): {', '.join(self.required_permissions)}"
            )
        
        return user

    async def __call__(self, user: dict = Depends(get_current_user)) -> dict:
        """Check if user has required role OR any of the required permissions."""
        return self._check_role_or_permission(user)


# Pre-defined permission checkers
require_users_read = PermissionChecker(required_permissions=["users:read"])
require_users_write = PermissionChecker(required_permissions=["users:write"])
require_users_delete = PermissionChecker(required_permissions=["users:delete"])

require_roles_read = PermissionChecker(required_permissions=["roles:read"])
require_roles_write = PermissionChecker(required_permissions=["roles:write"])

require_permissions_read = PermissionChecker(required_permissions=["permissions:read"])
require_permissions_write = PermissionChecker(required_permissions=["permissions:write"])
