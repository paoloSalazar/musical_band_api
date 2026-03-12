"""
Data access layer for User entities.

Provides CRUD operations for user management in the Musical Band API.

Functions:
    - get_one: Get user by email
    - get_all: Get all users
    - create: Create a new user
    - modify: Update an existing user
"""

import logging
from config.database import SessionLocal
from models.user import User
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from sqlalchemy.orm import selectinload
from exceptions import DatabaseError, DatabaseConnectionError

logger = logging.getLogger(__name__)


def get_one(email: str) -> User | None:
    """
    Retrieve a user by their email address.

    Args:
        email: The email address of the user to retrieve.

    Returns:
        The User object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.

    Example:
        >>> user = get_one("john@example.com")
        >>> if user:
        ...     print(f"Found user: {user.name}")
    """
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting user '{email}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting user '{email}'")
        raise DatabaseError("Failed to get user")
    finally:
        db.close()


def get_one_by_id(user_id: int) -> User | None:
    """
    Retrieve a user by their ID.

    Args:
        user_id: The ID of the user to retrieve.

    Returns:
        The User object with role relationship if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.

    Example:
        >>> user = get_one_by_id(1)
        >>> if user:
        ...     print(f"Found user: {user.name}")
    """
    db = SessionLocal()
    try:
        return db.query(User).options(
            selectinload(User.role)
        ).filter(User.id == user_id).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting user by id '{user_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting user by id '{user_id}'")
        raise DatabaseError("Failed to get user")
    finally:
        db.close()


def get_all() -> list[User]:
    """
    Retrieve all users from the database.

    Returns:
        List of all User objects.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(User).all()
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting all users")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while getting all users")
        raise DatabaseError("Failed to get all users")
    finally:
        db.close()


def get_all_paginated(skip: int = 0, limit: int = 20) -> tuple[list[User], int]:
    """
    Retrieve users from the database with pagination and join with roles.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        Tuple of (list of User objects with role relationship, total count).

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        # Get total count
        total = db.query(User).count()
        # Get paginated results with role relationship loaded
        users = db.query(User).options(
            selectinload(User.role)
        ).offset(skip).limit(limit).all()
        return users, total
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting paginated users")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while getting paginated users")
        raise DatabaseError("Failed to get paginated users")
    finally:
        db.close()


def create(user: User) -> User:
    """
    Create a new user in the database.

    Args:
        user: The User object to create.

    Returns:
        The created User object.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails (e.g., duplicate email).
    """
    db = SessionLocal()
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while creating user '{user.email}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating user '{user.email}'")
        db.rollback()
        raise DatabaseError("Failed to create user")
    finally:
        db.close()


def modify(user: User) -> User:
    """
    Update an existing user in the database.

    Args:
        user: The User object with updated fields.

    Returns:
        The updated User object, or None if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if db_user:
            db_user.name = user.name
            db_user.lastname = user.lastname
            db_user.second_lastname = user.second_lastname
            db_user.email = user.email
            db_user.password = user.password
            db_user.role_id = user.role_id
            db.commit()
            db.refresh(db_user)
        return db_user
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while modifying user '{user.email}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while modifying user '{user.email}'")
        db.rollback()
        raise DatabaseError("Failed to modify user")
    finally:
        db.close()
