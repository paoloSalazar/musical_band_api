"""
User Role API endpoints.

Provides REST endpoints for role management with RBAC protection.

Authorization:
    All endpoints require admin role AND specific permissions.

Endpoints:
    - GET /api/user-roles/ - List all roles
    - GET /api/user-roles/{name} - Get role by name
    - POST /api/user-roles/ - Create new role
    - PATCH /api/user-roles/ - Update role description
    - PUT /api/user-roles/ - Replace role data
    - DELETE /api/user-roles/{name} - Delete role
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
import services.user_role as service
from schemas.user_role import UserRole, UserRoleCreate
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError
from auth.auth import get_current_user
from auth.roles import (
    create_permission_checker,
    create_role_and_permission_checker,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user-roles")


# ============================================
# User Role Endpoints
# ============================================


@router.get("/", dependencies=[Depends(create_role_and_permission_checker(["admin"], ["read:user_roles"]))])
def get_all() -> list[UserRole]:
    """
    Retrieve all user roles from the database.

    Requires: Admin role AND read:user_roles permission.

    Returns:
        List of UserRole objects.

    Raises:
        HTTPException: 500 if database error occurs.
    """
    try:
        roles = service.get_all()
        logger.info(f"API request: Retrieved {len(roles)} user roles")
        return roles
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{name}", dependencies=[Depends(create_role_and_permission_checker(["admin"], ["read:user_roles"]))])
def get_one(name: str) -> UserRole | None:
    """
    Retrieve a user role by its name.

    Requires: Admin role AND read:user_roles permission.

    Args:
        name: The unique name of the role.

    Returns:
        UserRole object.

    Raises:
        HTTPException: 404 if role not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        role = service.get_one(name)
        logger.info(f"API request: Retrieved user role '{name}'")
        return role
    except NotFoundError as e:
        logger.warning(f"User role '{name}' not found: {str(e)}")
        raise HTTPException(status_code=404, detail=f"User role '{name}' not found")
    except DatabaseError as e:
        logger.error("Database error in get_one")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", dependencies=[Depends(create_role_and_permission_checker(["admin"], ["write:user_roles"]))])
def create(user_role: UserRoleCreate) -> UserRole | None:
    """
    Create a new user role.

    Requires: Admin role AND write:user_roles permission.

    Args:
        user_role: UserRoleCreate schema with role data.

    Returns:
        Created UserRole object.

    Raises:
        HTTPException: 409 if role already exists.
        HTTPException: 500 if database error occurs.
    """
    try:
        return service.create(user_role)
    except ConflictError as e:
        logger.warning(f"Conflict in create: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        logger.error("Database error in create")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/", dependencies=[Depends(create_role_and_permission_checker(["admin"], ["read:user_roles", "write:user_roles"]))])
def modify(user_role: UserRole) -> UserRole | None:
    """
    Update a user role's description.

    Requires: Admin role AND write:user_roles permission.

    Args:
        user_role: UserRole schema with updated description.

    Returns:
        Updated UserRole object.

    Raises:
        HTTPException: 404 if role not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        return service.modify(user_role)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error("Database error in get_all")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/", dependencies=[Depends(create_role_and_permission_checker(["admin"], ["read:user_roles", "write:user_roles"]))])
def replace(user_role: UserRole) -> UserRole | None:
    """
    Replace an existing user role's data.

    Requires: Admin role AND write:user_roles permission.

    Args:
        user_role: UserRole schema with replacement data.

    Returns:
        Replaced UserRole object.

    Raises:
        HTTPException: 404 if role not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        return service.replace(user_role)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{name}", dependencies=[Depends(create_role_and_permission_checker(["admin"], ["delete:user_roles"]))])
def delete(name: str) -> bool | None:
    """
    Delete a user role by name.

    Requires: Admin role AND delete:user_roles permission.

    Args:
        name: The name of the role to delete.

    Returns:
        True if deleted successfully.

    Raises:
        HTTPException: 404 if role not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        return service.delete(name)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Internal server error")
