import logging
from schemas.user_role import UserRole, UserRoleCreate
import data.user_role as data
from models.user_role import UserRole as DBUserRole
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

def get_all() -> list[UserRole]:
    """return all user roles"""
    try:
        db_roles = data.get_all()
        roles = [UserRole.model_validate(role) for role in db_roles]
        logger.info(f"Retrieved {len(roles)} user roles")
        return roles
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in get_all")
        raise DatabaseError("Service error")

def get_one(name: str) -> UserRole | None:
    """return one user role by name"""
    try:
        db_role = data.get_one(name)
        if db_role:
            logger.info(f"Retrieved user role '{name}'")
            return UserRole.model_validate(db_role)
        else:
            logger.warning(f"User role '{name}' not found")
            raise NotFoundError(f"User role '{name}' not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in get_one")
        raise DatabaseError("Service error")

def create(user_role: UserRoleCreate) -> UserRole:
    try:
        # Check if already exists
        existing = data.get_one(user_role.name)
        if existing:
            logger.warning(f"Attempted to create duplicate user role '{user_role.name}'")
            raise ConflictError(f"User role '{user_role.name}' already exists")
        # Convert Pydantic to SQLAlchemy model
        db_role = DBUserRole(name=user_role.name, description=user_role.description)
        created = data.create(db_role)
        logger.info(f"Created new user role '{user_role.name}'")
        return UserRole.model_validate(created)
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in create")
        raise DatabaseError("Service error")

def modify(user_role: UserRole) -> UserRole:
    try:
        # Check if exists
        existing = data.get_one(user_role.name)
        if not existing:
            logger.warning(f"Attempted to modify non-existent user role '{user_role.name}'")
            raise NotFoundError(f"User role '{user_role.name}' not found")
        # Assuming user_role has id, convert to DB model
        db_role = DBUserRole(id=user_role.id, name=user_role.name, description=user_role.description)
        modified = data.modify(db_role)
        if modified:
            logger.info(f"Modified user role '{user_role.name}'")
            return UserRole.model_validate(modified)
        else:
            logger.warning(f"User role '{user_role.name}' not found during modification")
            raise NotFoundError(f"User role '{user_role.name}' not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in modify")
        raise DatabaseError("Service error")

def replace(user_role: UserRole) -> UserRole:
    try:
        # Assuming user_role has id
        db_role = DBUserRole(id=user_role.id, name=user_role.name, description=user_role.description)
        replaced = data.replace(db_role)
        if replaced:
            return UserRole.model_validate(replaced)
        else:
            raise NotFoundError(f"User role with id {user_role.id} not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in replace")
        raise DatabaseError("Service error")

def delete(name: str) -> bool:
    try:
        # Check if exists
        existing = data.get_one(name)
        if not existing:
            raise NotFoundError(f"User role '{name}' not found")
        return data.delete(name)
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in delete")
        raise DatabaseError("Service error")