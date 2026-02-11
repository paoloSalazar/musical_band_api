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
