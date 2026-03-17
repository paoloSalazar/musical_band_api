"""
Data access layer for UserDetail entities.

Provides CRUD operations for user details in the Musical Band API.

Functions:
    - get_one: Get user detail by ID
    - get_by_user_id: Get all details for a user
    - get_all: Get all user details
    - create: Create a new user detail
    - update: Update an existing user detail
    - delete: Delete a user detail
    - delete_by_user_id: Delete all details for a user
"""

import logging
from typing import List
from config.database import SessionLocal
from models.user_detail import UserDetail
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from exceptions import DatabaseError, DatabaseConnectionError

logger = logging.getLogger(__name__)


def get_one(detail_id: int) -> UserDetail | None:
    """
    Retrieve a user detail by its ID.

    Args:
        detail_id: The unique identifier of the user detail.

    Returns:
        The UserDetail object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(UserDetail).filter(UserDetail.id == detail_id).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error in get_one: {str(e)}")
        raise DatabaseConnectionError(f"Database connection error: {str(e)}")
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_one: {str(e)}")
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        db.close()


def get_by_user_id(user_id: int) -> List[UserDetail]:
    """
    Retrieve all details for a specific user.

    Args:
        user_id: The ID of the user.

    Returns:
        List of UserDetail objects.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(UserDetail).filter(UserDetail.user_id == user_id).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error in get_by_user_id: {str(e)}")
        raise DatabaseConnectionError(f"Database connection error: {str(e)}")
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_by_user_id: {str(e)}")
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        db.close()


def get_all() -> List[UserDetail]:
    """
    Retrieve all user details.

    Returns:
        List of UserDetail objects.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(UserDetail).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error in get_all: {str(e)}")
        raise DatabaseConnectionError(f"Database connection error: {str(e)}")
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        db.close()


def create(detail_data: dict) -> UserDetail:
    """
    Create a new user detail.

    Args:
        detail_data: Dictionary containing user detail data.

    Returns:
        The created UserDetail object.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        new_detail = UserDetail(**detail_data)
        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)
        return new_detail
    except (OperationalError, InterfaceError) as e:
        db.rollback()
        logger.error(f"Database connection error in create: {str(e)}")
        raise DatabaseConnectionError(f"Database connection error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in create: {str(e)}")
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        db.close()


def update(detail_id: int, detail_data: dict) -> UserDetail | None:
    """
    Update an existing user detail.

    Args:
        detail_id: The ID of the user detail to update.
        detail_data: Dictionary containing fields to update.

    Returns:
        The updated UserDetail object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        detail = db.query(UserDetail).filter(UserDetail.id == detail_id).first()
        if detail is None:
            return None
        
        for key, value in detail_data.items():
            if value is not None:
                setattr(detail, key, value)
        
        db.commit()
        db.refresh(detail)
        return detail
    except (OperationalError, InterfaceError) as e:
        db.rollback()
        logger.error(f"Database connection error in update: {str(e)}")
        raise DatabaseConnectionError(f"Database connection error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in update: {str(e)}")
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        db.close()


def delete(detail_id: int) -> bool:
    """
    Delete a user detail.

    Args:
        detail_id: The ID of the user detail to delete.

    Returns:
        True if deleted, False if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        detail = db.query(UserDetail).filter(UserDetail.id == detail_id).first()
        if detail is None:
            return False
        
        db.delete(detail)
        db.commit()
        return True
    except (OperationalError, InterfaceError) as e:
        db.rollback()
        logger.error(f"Database connection error in delete: {str(e)}")
        raise DatabaseConnectionError(f"Database connection error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in delete: {str(e)}")
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        db.close()


def delete_by_user_id(user_id: int) -> bool:
    """
    Delete all details for a specific user.

    Args:
        user_id: The ID of the user whose details to delete.

    Returns:
        True if any were deleted, False if none existed.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        details = db.query(UserDetail).filter(UserDetail.user_id == user_id).all()
        if not details:
            return False
        
        for detail in details:
            db.delete(detail)
        
        db.commit()
        return True
    except (OperationalError, InterfaceError) as e:
        db.rollback()
        logger.error(f"Database connection error in delete_by_user_id: {str(e)}")
        raise DatabaseConnectionError(f"Database connection error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in delete_by_user_id: {str(e)}")
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        db.close()
