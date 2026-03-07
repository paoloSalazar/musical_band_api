"""
Service layer for UserRole business logic.

Provides business logic operations for role management,
including validation and data transformation.

Functions:
    - get_all: Get all roles
    - get_one: Get role by name
    - create: Create a new role
    - modify: Update role description
    - replace: Replace role data
    - delete: Delete a role
"""

import logging
from schemas.user_role import UserRole, UserRoleCreate, UserRoleUpdate
import data.user_role as data
from models.user_role import UserRole as DBUserRole
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)


def get_all() -> list[UserRole]:
    """
    Retrieve all user roles from the database.

    Returns:
        List of UserRole objects.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        db_roles = data.get_all()
        roles = [UserRole.model_validate(role) for role in db_roles]
        logger.info(f"Retrieved {len(roles)} user roles")
        return roles
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in get_all")
        raise DatabaseError("Service error")


def get_one(name: str) -> UserRole:
    """
    Retrieve a user role by its name.

    Args:
        name: The unique name of the role.

    Returns:
        UserRole object.

    Raises:
        NotFoundError: If role with name is not found.
        DatabaseError: If database operation fails.
    """
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
    """
    Create a new user role in the database.

    Args:
        user_role: UserRoleCreate schema with role data.

    Returns:
        Created UserRole object.

    Raises:
        ConflictError: If role with name already exists.
        DatabaseError: If database operation fails.
    """
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


def modify(role_id: int, role_update: UserRoleUpdate) -> UserRole:
    """
    Update a user role's description.

    Args:
        role_id: The ID of the role to update.
        role_update: UserRoleUpdate schema with updated fields.

    Returns:
        Updated UserRole object.

    Raises:
        NotFoundError: If role to update is not found.
        DatabaseError: If database operation fails.
    """
    try:
        # Check if exists by ID
        existing = data.get_by_id(role_id)
        if not existing:
            logger.warning(f"Attempted to modify non-existent user role with id '{role_id}'")
            raise NotFoundError(f"User role with id '{role_id}' not found")
        
        # Build update data - only include fields that are provided
        update_data = role_update.model_dump(exclude_unset=True)
        
        # If name is being updated, create new DBUserRole with new name
        if 'name' in update_data and update_data['name']:
            db_role = DBUserRole(
                id=role_id,
                name=update_data['name'],
                description=update_data.get('description', existing.description)
            )
        else:
            # Just update description
            db_role = DBUserRole(
                id=role_id,
                name=existing.name,
                description=update_data.get('description', existing.description)
            )
        
        modified = data.modify(db_role)
        if modified:
            logger.info(f"Modified user role with id '{role_id}'")
            return UserRole.model_validate(modified)
        else:
            logger.warning(f"User role with id '{role_id}' not found during modification")
            raise NotFoundError(f"User role with id '{role_id}' not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in modify")
        raise DatabaseError("Service error")


def replace(user_role: UserRole) -> UserRole:
    """
    Replace an existing user role's data.

    Args:
        user_role: UserRole schema with replacement data.

    Returns:
        Replaced UserRole object.

    Raises:
        NotFoundError: If role to replace is not found.
        DatabaseError: If database operation fails.
    """
    try:
        # Assuming user_role has id
        db_role = DBUserRole(id=user_role.id, name=user_role.name, description=user_role.description)
        replaced = data.replace(db_role)
        if replaced:
            logger.info(f"Replaced user role with id {user_role.id}")
            return UserRole.model_validate(replaced)
        else:
            raise NotFoundError(f"User role with id {user_role.id} not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in replace")
        raise DatabaseError("Service error")


def delete(name: str) -> bool:
    """
    Delete a user role by name.

    Args:
        name: The name of the role to delete.

    Returns:
        True if deleted successfully.

    Raises:
        NotFoundError: If role to delete is not found.
        ConflictError: If role has permissions assigned.
        DatabaseError: If database operation fails.
    """
    try:
        # Check if exists
        existing = data.get_one(name)
        if not existing:
            raise NotFoundError(f"User role '{name}' not found")
        logger.info(f"Deleted user role '{name}'")
        return data.delete(name)
    except ConflictError:
        # Re-raise ConflictError as-is
        raise
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in delete")
        raise DatabaseError("Service error")
