from fastapi import APIRouter
from model.user_role import UserRole
import service.user_role as service

router = APIRouter(prefix="/api/user-roles")

@router.get("/")
def get_all() -> list[UserRole]:
    """Get all user roles"""
    return service.get_all()

@router.get("/{name}")
def get_one(name: str) -> UserRole | None:
    """Get one user role by name"""
    return service.get_one(name)

@router.post("/")
def create(user_role: UserRole) -> UserRole | None:
    """Create a new user role"""
    return service.create(user_role)

@router.patch("/")
def modify(user_role: UserRole) -> UserRole | None:
    """Modify fields of an existing user role"""
    return service.modify(user_role)

@router.put("/")
def replace(user_role: UserRole) -> UserRole | None:
    """Replace an existing user role"""
    return service.replace(user_role)

@router.delete("/{name}")
def delete(name: str) -> None:
    """Delete a user role"""
    return service.delete(name)