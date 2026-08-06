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
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from exceptions import DatabaseError, DatabaseConnectionError, ConflictError
from data.integrity_checker import check_integrity_before_deletion

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
        ConflictError: If role has users or permissions assigned.
    """
    db = SessionLocal()
    try:
        db_role = db.query(UserRole).filter(UserRole.name == name).first()
        if not db_role:
            return False

        # Check integrity constraints BEFORE attempting delete
        integrity_error = check_integrity_before_deletion('role', name)
        if integrity_error:
            raise ConflictError(integrity_error)

        db.delete(db_role)
        db.commit()
        return True
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while deleting user role '{name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting user role '{name}': {str(e)}")
        db.rollback()

        # Check for constraint violations that might slip through our integrity check
        error_str = str(e).upper()
        if ("'C': '23503'" in error_str or '23503' in error_str or
            "'C': '23502'" in error_str or '23502' in error_str):
            raise ConflictError("This role cannot be deleted because it has associated users or permissions. Please remove these associations first.")
        else:
            raise DatabaseError("Failed to delete user role")
    except ConflictError:
        # Re-raise ConflictError as-is
        raise
    finally:
        db.close()
