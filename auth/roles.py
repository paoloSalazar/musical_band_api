"""
Role-Based Access Control (RBAC) dependencies for FastAPI.

This module provides authorization checkers for managing access to
endpoints based on user roles and permissions.

Available Checkers:
    - RoleChecker: Validates user has one of allowed roles
    - PermissionChecker: Validates user has all required permissions
    - RoleOrPermissionChecker: Validates user has role OR any permission
    - RoleAndPermissionChecker: Validates user has role AND all permissions

Usage:
    >>> from auth.roles import require_admin
    >>> @router.get("/admin-only", dependencies=[Depends(require_admin)])
    >>> def admin_endpoint():
    >>>     return {"message": "Admin access granted"}

    >>> # Using factory functions for dynamic roles/permissions
    >>> from auth.roles import create_permission_checker
    >>> require_users_write = create_permission_checker(["users:write"])
"""

from fastapi import Depends, HTTPException, status
from auth.auth import get_current_user


class RoleChecker:
    """
    Authorization dependency that checks if the user has an allowed role.

    Args:
        allowed_roles: List of role names that are allowed access.
                      Example: ["admin", "moderator"]

    Raises:
        HTTPException: 403 if user's role is not in allowed_roles.

    Example:
        >>> require_admin = RoleChecker(allowed_roles=["admin"])
        >>> @router.get("/admin", dependencies=[Depends(require_admin)])
        >>> def admin_only():
        >>>     return {"message": "Admin access"}
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def _check_role(self, user: dict) -> dict:
        """
        Check if the user's role is in the allowed roles list.

        This method is used for testing purposes to bypass FastAPI
        dependency injection.

        Args:
            user: User dictionary containing 'role' key.

        Returns:
            The user dictionary if role is valid.

        Raises:
            HTTPException: 403 if role is missing or not allowed.
        """
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

    async def __call__(self, user: dict = Depends(get_current_user)) -> dict:
        """
        Check if the user's role is in the allowed roles list.

        This method is called by FastAPI's dependency injection system.

        Args:
            user: Current authenticated user from get_current_user.

        Returns:
            The user dictionary if authorization passes.

        Raises:
            HTTPException: 403 if user lacks required role.
        """
        return self._check_role(user)


def create_role_checker(allowed_roles: list[str]) -> RoleChecker:
    """
    Factory function to create a RoleChecker with dynamic roles.

    Use this function when roles need to be determined at runtime
    (e.g., loaded from database).

    Args:
        allowed_roles: List of role names that are allowed access.

    Returns:
        Configured RoleChecker instance.

    Example:
        >>> # Dynamic role checking based on endpoint config
        >>> admin_or_moderator = create_role_checker(["admin", "moderator"])
        >>> @router.get("/manage", dependencies=[Depends(admin_or_moderator)])
        >>> def manage_endpoint():
        >>>     return {"message": "Access granted"}
    """
    return RoleChecker(allowed_roles)


# Pre-defined role checkers for common use cases
require_admin = RoleChecker(allowed_roles=["admin"])
require_admin_or_moderator = RoleChecker(allowed_roles=["admin", "moderator"])
require_any_role = RoleChecker(allowed_roles=["admin", "moderator", "user"])


class PermissionChecker:
    """
    Authorization dependency that checks if the user has required permissions.

    Unlike RoleChecker which checks a single role, this checker validates
    that the user has ALL specified permissions.

    Args:
        required_permissions: List of permission names required.
                              Example: ["users:read", "users:write"]

    Raises:
        HTTPException: 403 if user is missing any required permission.

    Example:
        >>> require_users_read = PermissionChecker(required_permissions=["users:read"])
        >>> @router.get("/users", dependencies=[Depends(require_users_read)])
        >>> def list_users():
        >>>     return [{"id": 1, "name": "John"}]
    """

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def _check_permission(self, user: dict) -> dict:
        """
        Check if user has all required permissions.

        This method is used for testing purposes.

        Args:
            user: User dictionary containing 'permissions' key (list of str).

        Returns:
            The user dictionary if all permissions are present.

        Raises:
            HTTPException: 403 if any permission is missing.
        """
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
        """
        Check if user has all required permissions.

        Args:
            user: Current authenticated user from get_current_user.

        Returns:
            The user dictionary if authorization passes.

        Raises:
            HTTPException: 403 if user lacks required permissions.
        """
        return self._check_permission(user)


class RoleOrPermissionChecker:
    """
    Authorization dependency that checks if user has required role OR permission.

    This provides flexible access control where users can access an endpoint
    either by having a specific role OR by having a specific permission.

    Args:
        allowed_roles: List of role names that grant access.
        required_permissions: List of permission names that grant access.

    Raises:
        HTTPException: 403 if user lacks both role AND all permissions.

    Example:
        >>> # Admins OR users with delete permission
        >>> require_admin_or_delete = RoleOrPermissionChecker(
        ...     allowed_roles=["admin"],
        ...     required_permissions=["users:delete"]
        ... )
    """

    def __init__(self, allowed_roles: list[str], required_permissions: list[str]):
        self.allowed_roles = allowed_roles
        self.required_permissions = required_permissions

    def _check_role_or_permission(self, user: dict) -> dict:
        """
        Check if user has allowed role OR any required permission.

        Args:
            user: User dictionary with 'role' and 'permissions' keys.

        Returns:
            The user dictionary if access is granted.

        Raises:
            HTTPException: 403 if access is denied.
        """
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
        """
        Check if user has required role OR any required permission.

        Args:
            user: Current authenticated user from get_current_user.

        Returns:
            The user dictionary if authorization passes.

        Raises:
            HTTPException: 403 if user lacks both role and permissions.
        """
        return self._check_role_or_permission(user)


class RoleAndPermissionChecker:
    """
    Authorization dependency that requires BOTH role AND all permissions.

    This provides strict access control where users must have the required
    role AND all specified permissions.

    Args:
        required_roles: List of roles where at least one must match.
        required_permissions: List of permissions where ALL must be present.

    Raises:
        HTTPException: 403 if user lacks role or any permission.

    Example:
        >>> # Requires admin role AND users:manage permission
        >>> require_admin_and_manage = RoleAndPermissionChecker(
        ...     required_roles=["admin"],
        ...     required_permissions=["users:manage"]
        ... )
    """

    def __init__(self, required_roles: list[str], required_permissions: list[str]):
        self.required_roles = required_roles
        self.required_permissions = required_permissions

    def _check_role_and_permission(self, user: dict) -> dict:
        """
        Check if user has required role AND all required permissions.

        Args:
            user: User dictionary with 'role' and 'permissions' keys.

        Returns:
            The user dictionary if all requirements are met.

        Raises:
            HTTPException: 403 if role is missing or any permission is missing.
        """
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
        """
        Check if user has required role AND all required permissions.

        Args:
            user: Current authenticated user from get_current_user.

        Returns:
            The user dictionary if authorization passes.

        Raises:
            HTTPException: 403 if requirements are not met.
        """
        return self._check_role_and_permission(user)


def create_permission_checker(required_permissions: list[str]) -> PermissionChecker:
    """
    Factory function to create a PermissionChecker with dynamic permissions.

    Use this function when permissions need to be determined at runtime.

    Args:
        required_permissions: List of permission names required.

    Returns:
        Configured PermissionChecker instance.

    Example:
        >>> read_users = create_permission_checker(["users:read"])
        >>> @router.get("/users", dependencies=[Depends(read_users)])
        >>> def list_users():
        >>>     return []
    """
    return PermissionChecker(required_permissions)


def create_role_or_permission_checker(
    allowed_roles: list[str],
    required_permissions: list[str]
) -> RoleOrPermissionChecker:
    """
    Factory function to create a RoleOrPermissionChecker with dynamic parameters.

    Args:
        allowed_roles: List of role names that grant access.
        required_permissions: List of permission names that grant access.

    Returns:
        Configured RoleOrPermissionChecker instance.

    Example:
        >>> access = create_role_or_permission_checker(
        ...     allowed_roles=["admin"],
        ...     required_permissions=["reports:view"]
        ... )
    """
    return RoleOrPermissionChecker(allowed_roles, required_permissions)


def create_role_and_permission_checker(
    required_roles: list[str],
    required_permissions: list[str]
) -> RoleAndPermissionChecker:
    """
    Factory function to create a RoleAndPermissionChecker with dynamic parameters.

    Requires user to have BOTH the required role AND all permissions.

    Args:
        required_roles: List of roles where at least one must match.
        required_permissions: List of permissions where ALL must be present.

    Returns:
        Configured RoleAndPermissionChecker instance.

    Example:
        >>> strict_access = create_role_and_permission_checker(
        ...     required_roles=["manager"],
        ...     required_permissions=["budget:read", "budget:write"]
        ... )
    """
    return RoleAndPermissionChecker(required_roles, required_permissions)
