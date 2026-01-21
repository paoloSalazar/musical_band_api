from schemas.user_role import UserRole, UserRoleCreate
import data.user_role as data
from models.user_role import UserRole as DBUserRole

def get_all() -> list[UserRole]:
    """return all user roles"""
    db_roles = data.get_all()
    return [UserRole.model_validate(role) for role in db_roles]

def get_one(name: str) -> UserRole | None:
    """return one user role by name"""
    db_role = data.get_one(name)
    return UserRole.model_validate(db_role) if db_role else None

def create(user_role: UserRoleCreate) -> UserRole:
    # Convert Pydantic to SQLAlchemy model
    db_role = DBUserRole(name=user_role.name, description=user_role.description)
    created = data.create(db_role)
    return UserRole.model_validate(created)

def modify(user_role: UserRole) -> UserRole:
    # Assuming user_role has id, convert to DB model
    db_role = DBUserRole(id=user_role.id, name=user_role.name, description=user_role.description)
    modified = data.modify(db_role)
    return UserRole.model_validate(modified)

def replace(user_role: UserRole) -> UserRole:
    # Assuming user_role has id
    db_role = DBUserRole(id=user_role.id, name=user_role.name, description=user_role.description)
    replaced = data.replace(db_role)
    return UserRole.model_validate(replaced)

def delete(name: str) -> bool:
    return data.delete(name)