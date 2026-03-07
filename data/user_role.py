"""
Data access layer for UserRole entities.

Provides CRUD operations for role management in the Musical Band API.

Functions:
    - get_one: Get role by name
    - get_all: Get all roles
    - create: Create a new role
    - modify: Update role description
    - replace: Replace role data
    - delete: Delete a role by name
"""

import logging
from config.database import SessionLocal
from models.user_role import UserRole
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError, IntegrityError
from exceptions import DatabaseError, DatabaseConnectionError, ConflictError

logger = logging.getLogger(__name__)


def get_one(name: str) -> UserRole | None:
    """
    Retrieve a user role by its name.

    Args:
        name: The unique name of the role (e.g., "admin", "user").

    Returns:
        The UserRole object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.

    Example:
        >>> role = get_one("admin")
        >>> if role:
        ...     print(f"Found role: {role.description}")
    """
    db = SessionLocal()
    try:
        return db.query(UserRole).filter(UserRole.name == name).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting user role '{name}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting user role '{name}'")
        raise DatabaseError("Failed to get user role")
    finally:
        db.close()


def get_by_id(role_id: int) -> UserRole | None:
    """
    Retrieve a user role by its ID.

    Args:
        role_id: The unique ID of the role.

    Returns:
        The UserRole object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(UserRole).filter(UserRole.id == role_id).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting user role by id '{role_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting user role by id '{role_id}'")
        raise DatabaseError("Failed to get user role")
    finally:
        db.close()


def get_all() -> list[UserRole]:
    """
    Retrieve all user roles from the database.

    Returns:
        List of all UserRole objects.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(UserRole).all()
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting all user roles")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while getting all user roles")
        raise DatabaseError("Failed to get all user roles")
    finally:
        db.close()


def create(user_role: UserRole) -> UserRole:
    """
    Create a new user role in the database.

    Args:
        user_role: The UserRole object to create.

    Returns:
        The created UserRole object.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails (e.g., duplicate name).
    """
    db = SessionLocal()
    try:
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        return user_role
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while creating user role '{user_role.name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating user role '{user_role.name}'")
        db.rollback()
        raise DatabaseError("Failed to create user role")
    finally:
        db.close()


def modify(user_role: UserRole) -> UserRole:
    """
    Update a user role's description.

    Args:
        user_role: The UserRole object with updated description.

    Returns:
        The updated UserRole object, or None if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_user = db.query(UserRole).filter(UserRole.name == user_role.name).first()
        if db_user:
            db_user.description = user_role.description
            db.commit()
            db.refresh(db_user)
        return db_user
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while modifying user role '{user_role.name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while modifying user role '{user_role.name}'")
        db.rollback()
        raise DatabaseError("Failed to modify user role")
    finally:
        db.close()


def replace(user_role: UserRole) -> UserRole:
    """
    Replace an existing user role's data.

    Args:
        user_role: The UserRole object with replacement data.

    Returns:
        The replaced UserRole object, or None if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_user = db.query(UserRole).filter(UserRole.id == user_role.id).first()
        if db_user:
            db_user.name = user_role.name
            db_user.description = user_role.description
            db.commit()
            db.refresh(db_user)
        return db_user
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while replacing user role '{user_role.name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while replacing user role '{user_role.name}'")
        db.rollback()
        raise DatabaseError("Failed to replace user role")
    finally:
        db.close()


def delete(name: str) -> bool:
    """
    Delete a user role by name.

    Args:
        name: The name of the role to delete.

    Returns:
        True if deleted, False if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
        ConflictError: If role has permissions assigned.
    """
    db = SessionLocal()
    try:
        db_user = db.query(UserRole).filter(UserRole.name == name).first()
        if not db_user:
            return False
        
        # Check if role has any permissions assigned BEFORE attempting delete
        # This prevents cascade delete and gives a friendly error message
        if db_user.permissions:
            assigned_permissions = [perm.name for perm in db_user.permissions]
            perm_str = "', '".join(assigned_permissions)
            raise ConflictError(
                f"Role '{name}' has permission(s) assigned: '{perm_str}'. "
                f"Remove these permissions from the role before deleting."
            )
        
        db.delete(db_user)
        db.commit()
        return True
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while deleting user role '{name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except IntegrityError as e:
        db.rollback()
        # Check if this is a foreign key constraint violation
        error_msg = str(e).lower()
        if 'foreign key constraint' in error_msg or 'restrict' in error_msg:
            # Get the permissions that are assigned to this role
            assigned_permissions = []
            try:
                db2 = SessionLocal()
                role = db2.query(UserRole).filter(UserRole.name == name).first()
                if role:
                    assigned_permissions = [perm.name for perm in role.permissions]
                db2.close()
            except Exception:
                pass
            
            if assigned_permissions:
                perm_str = "', '".join(assigned_permissions)
                raise ConflictError(
                    f"Role '{name}' has permission(s) assigned: '{perm_str}'. "
                    f"Remove these permissions from the role before deleting."
                )
            raise ConflictError(f"Role '{name}' cannot be deleted because it is in use")
        logger.error(f"Integrity error while deleting user role '{name}': {e}")
        raise DatabaseError("Failed to delete user role due to data integrity issue")
    except ConflictError:
        # Re-raise ConflictError as-is
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting user role '{name}'")
        db.rollback()
        raise DatabaseError("Failed to delete user role")
    finally:
        db.close()
