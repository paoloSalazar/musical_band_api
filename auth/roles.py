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


# ============================================
# Role Checker Factory Function
# ============================================


def create_role_checker(allowed_roles: list[str]) -> RoleChecker:
    """Factory function to create a RoleChecker with dynamic roles.
    
    Usage:
        Depends(create_role_checker(["admin", "moderator"]))
    """
    return RoleChecker(allowed_roles)


# Pre-defined role checkers for common use cases (kept for convenience)
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


class RoleAndPermissionChecker:
    """Dependency class that checks if user has required role AND ALL permissions."""

    def __init__(self, required_roles: list[str], required_permissions: list[str]):
        self.required_roles = required_roles
        self.required_permissions = required_permissions

    def _check_role_and_permission(self, user: dict) -> dict:
        """Check if user has required role AND all required permissions (for testing)."""
        user_role = user.get("role")
        user_permissions = user.get("permissions", [])
        
        has_required_role = user_role in self.required_roles
        missing_permissions = [
            perm for perm in self.required_permissions 
            if perm not in user_permissions
        ]
        
        if not has_required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(self.required_roles)}"
            )
        
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission(s): {', '.join(missing_permissions)}"
            )
        
        return user

    async def __call__(self, user: dict = Depends(get_current_user)) -> dict:
        """Check if user has required role AND all required permissions."""
        return self._check_role_and_permission(user)


# ============================================
# Permission Checker Factory Functions
# ============================================


def create_permission_checker(required_permissions: list[str]) -> PermissionChecker:
    """Factory function to create a PermissionChecker with dynamic permissions.
    
    Usage:
        Depends(create_permission_checker(["users:read", "users:write"]))
    """
    return PermissionChecker(required_permissions)


def create_role_or_permission_checker(
    allowed_roles: list[str], 
    required_permissions: list[str]
) -> RoleOrPermissionChecker:
    """Factory function to create a RoleOrPermissionChecker with dynamic parameters.
    
    Usage:
        Depends(create_role_or_permission_checker(["admin"], ["users:delete"]))
    """
    return RoleOrPermissionChecker(allowed_roles, required_permissions)


def create_role_and_permission_checker(
    required_roles: list[str], 
    required_permissions: list[str]
) -> RoleAndPermissionChecker:
    """Factory function to create a RoleAndPermissionChecker with dynamic parameters.
    
    Requires user to have BOTH the required role AND all permissions.
    
    Usage:
        Depends(create_role_and_permission_checker(["admin"], ["roles:read"]))
    """
    return RoleAndPermissionChecker(required_roles, required_permissions)
