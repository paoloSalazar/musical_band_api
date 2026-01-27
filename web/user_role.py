import logging
from fastapi import APIRouter, HTTPException
import services.user_role as service
from schemas.user_role import UserRole, UserRoleCreate
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user-roles")

@router.get("/")
def get_all() -> list[UserRole]:
    """Get all user roles"""
    try:
        roles = service.get_all()
        logger.info(f"API request: Retrieved {len(roles)} user roles")
        return roles
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{name}")
def get_one(name: str) -> UserRole | None:
    """Get one user role by name"""
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

@router.post("/")
def create(user_role: UserRoleCreate) -> UserRole | None:
    """Create a new user role"""
    try:
        return service.create(user_role)
    except ConflictError as e:
        logger.warning(f"Conflict in create: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        logger.error("Database error in create")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/")
def modify(user_role: UserRole) -> UserRole | None:
    """Modify fields of an existing user role"""
    try:
        return service.modify(user_role)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error("Database error in get_all")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/")
def replace(user_role: UserRole) -> UserRole | None:
    """Replace an existing user role"""
    try:
        return service.replace(user_role)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{name}")
def delete(name: str) -> None:
    """Delete a user role"""
    try:
        service.delete(name)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Internal server error")