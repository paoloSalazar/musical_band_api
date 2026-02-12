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
    """Get all user roles (Admin + roles:read permission required)"""
    try:
        roles = service.get_all()
        logger.info(f"API request: Retrieved {len(roles)} user roles")
        return roles
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{name}", dependencies=[Depends(create_role_and_permission_checker(["admin"], ["read:user_roles"]))])
def get_one(name: str) -> UserRole | None:
    """Get one user role by name (Admin + roles:read permission required)"""
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
    """Create a new user role (Admin + roles:write permission required)"""
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
    """Modify fields of an existing user role (Admin + roles:write permission required)"""
    try:
        return service.modify(user_role)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error("Database error in get_all")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/", dependencies=[Depends(create_role_and_permission_checker(["admin"], ["read:user_roles", "write:user_roles"]))])
def replace(user_role: UserRole) -> UserRole | None:
    """Replace an existing user role (Admin + roles:write permission required)"""
    try:
        return service.replace(user_role)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{name}", dependencies=[Depends(create_role_and_permission_checker(["admin"], ["delete:user_roles"]))])
def delete(name: str) -> None:
    """Delete a user role (Admin + roles:write permission required)"""
    try:
        service.delete(name)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Internal server error")
