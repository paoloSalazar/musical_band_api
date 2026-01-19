from model.user_role import UserRole
import data.user_role as data

def get_all() -> list[UserRole]:
    """return all user roles"""
    return data.get_all()

def get_one(name: str) -> UserRole | None:
    """return one user role by name"""
    return data.get_one(name)

def create(user_role: UserRole) -> UserRole:
    return data.create(user_role)

def modify(user_role: UserRole) -> UserRole:
    return data.modify(user_role)

def replace(user_role: UserRole) -> UserRole:
    return data.replace(user_role)

def delete(name: str) -> bool:
    return data.delete(name)