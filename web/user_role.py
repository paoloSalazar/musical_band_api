from fastapi import APIRouter, HTTPException
import services.user_role as service
from schemas.user_role import UserRole, UserRoleCreate
from exceptions import DatabaseError, NotFoundError, ConflictError

router = APIRouter(prefix="/api/user-roles")

@router.get("/")
def get_all() -> list[UserRole]:
    """Get all user roles"""
    try:
        return service.get_all()
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{name}")
def get_one(name: str) -> UserRole | None:
    """Get one user role by name"""
    try:
        return service.get_one(name)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"User role '{name}' not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/")
def create(user_role: UserRoleCreate) -> UserRole | None:
    """Create a new user role"""
    try:
        return service.create(user_role)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/")
def modify(user_role: UserRole) -> UserRole | None:
    """Modify fields of an existing user role"""
    try:
        return service.modify(user_role)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError:
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