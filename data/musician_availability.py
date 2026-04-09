"""
Data access layer for MusicianAvailability entities.

Provides CRUD operations for musician availability management in the Musical Band API.

Functions:
    - get_by_musician: Get availability by musician ID
    - get_by_musician_and_date: Get specific availability entry
    - get_all_by_date: Get all musicians unavailable on a specific date
    - create: Create new availability entry
    - create_bulk: Create multiple availability entries
    - update: Update existing availability entry
    - delete: Delete availability entry
    - check_availability: Check if musician is available on a date
"""

import logging
from config.database import SessionLocal
from models.musician_availability import MusicianAvailability
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from sqlalchemy.orm import selectinload
from datetime import date
from exceptions import DatabaseError, DatabaseConnectionError

logger = logging.getLogger(__name__)


def get_by_musician(musician_id: int) -> list[MusicianAvailability]:
    """
    Retrieve all availability entries for a specific musician.

    Args:
        musician_id: The ID of the musician.

    Returns:
        List of MusicianAvailability objects for the musician.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.

    Example:
        >>> availabilities = get_by_musician(1)
        >>> for av in availabilities:
        ...     print(f"Unavailable: {av.unavailable_date}")
    """
    db = SessionLocal()
    try:
        return db.query(MusicianAvailability).options(
            selectinload(MusicianAvailability.musician)
        ).filter(MusicianAvailability.musician_id == musician_id).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting availability for musician '{musician_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting availability for musician '{musician_id}'")
        raise DatabaseError("Failed to get musician availability")
    finally:
        db.close()


def get_by_musician_and_date(musician_id: int, unavailable_date: date) -> MusicianAvailability | None:
    """
    Retrieve a specific availability entry for a musician on a date.

    Args:
        musician_id: The ID of the musician.
        unavailable_date: The date to check.

    Returns:
        The MusicianAvailability object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(MusicianAvailability).filter(
            MusicianAvailability.musician_id == musician_id,
            MusicianAvailability.unavailable_date == unavailable_date
        ).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting availability for musician '{musician_id}' on '{unavailable_date}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting availability for musician '{musician_id}' on '{unavailable_date}'")
        raise DatabaseError("Failed to get musician availability")
    finally:
        db.close()


def get_all_by_date(unavailable_date: date) -> list[MusicianAvailability]:
    """
    Retrieve all musicians unavailable on a specific date.

    Args:
        unavailable_date: The date to check.

    Returns:
        List of MusicianAvailability objects for the date.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(MusicianAvailability).options(
            selectinload(MusicianAvailability.musician)
        ).filter(MusicianAvailability.unavailable_date == unavailable_date).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting availability for date '{unavailable_date}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting availability for date '{unavailable_date}'")
        raise DatabaseError("Failed to get availability by date")
    finally:
        db.close()


def check_availability(musician_id: int, check_date: date) -> bool:
    """
    Check if a musician is available on a specific date.

    Args:
        musician_id: The ID of the musician.
        check_date: The date to check.

    Returns:
        True if available, False if unavailable.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        availability = db.query(MusicianAvailability).filter(
            MusicianAvailability.musician_id == musician_id,
            MusicianAvailability.unavailable_date == check_date
        ).first()
        return availability is None
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while checking availability for musician '{musician_id}' on '{check_date}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while checking availability for musician '{musician_id}' on '{check_date}'")
        raise DatabaseError("Failed to check musician availability")
    finally:
        db.close()


def create(availability: MusicianAvailability) -> MusicianAvailability:
    """
    Create a new availability entry in the database.

    Args:
        availability: The MusicianAvailability object to create.

    Returns:
        The created MusicianAvailability object.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails (e.g., duplicate entry).
    """
    db = SessionLocal()
    try:
        db.add(availability)
        db.commit()
        db.refresh(availability)
        return availability
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while creating availability for musician '{availability.musician_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating availability for musician '{availability.musician_id}'")
        db.rollback()
        raise DatabaseError("Failed to create musician availability")
    finally:
        db.close()


def create_bulk(availabilities: list[MusicianAvailability]) -> list[MusicianAvailability]:
    """
    Create multiple availability entries in bulk.

    Args:
        availabilities: List of MusicianAvailability objects to create.

    Returns:
        List of created MusicianAvailability objects.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db.add_all(availabilities)
        db.commit()
        for availability in availabilities:
            db.refresh(availability)
        return availabilities
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while bulk creating availability entries")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while bulk creating availability entries")
        db.rollback()
        raise DatabaseError("Failed to bulk create musician availability")
    finally:
        db.close()


def update(availability: MusicianAvailability) -> MusicianAvailability | None:
    """
    Update an existing availability entry in the database.

    Args:
        availability: The MusicianAvailability object with updated fields.

    Returns:
        The updated MusicianAvailability object, or None if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_availability = db.query(MusicianAvailability).filter(
            MusicianAvailability.id == availability.id
        ).first()
        if db_availability:
            db_availability.unavailable_date = availability.unavailable_date
            db_availability.reason = availability.reason
            db.commit()
            db.refresh(db_availability)
        return db_availability
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while updating availability '{availability.id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating availability '{availability.id}'")
        db.rollback()
        raise DatabaseError("Failed to update musician availability")
    finally:
        db.close()


def delete(availability_id: int) -> bool:
    """
    Delete an availability entry from the database.

    Args:
        availability_id: The ID of the availability entry to delete.

    Returns:
        True if deleted, False if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_availability = db.query(MusicianAvailability).filter(
            MusicianAvailability.id == availability_id
        ).first()
        if db_availability:
            db.delete(db_availability)
            db.commit()
            return True
        return False
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while deleting availability '{availability_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting availability '{availability_id}'")
        db.rollback()
        raise DatabaseError("Failed to delete musician availability")
    finally:
        db.close()


def delete_by_musician_and_date(musician_id: int, unavailable_date: date) -> bool:
    """
    Delete a specific availability entry by musician and date.

    Args:
        musician_id: The ID of the musician.
        unavailable_date: The date of the availability entry.

    Returns:
        True if deleted, False if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_availability = db.query(MusicianAvailability).filter(
            MusicianAvailability.musician_id == musician_id,
            MusicianAvailability.unavailable_date == unavailable_date
        ).first()
        if db_availability:
            db.delete(db_availability)
            db.commit()
            return True
        return False
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while deleting availability for musician '{musician_id}' on '{unavailable_date}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting availability for musician '{musician_id}' on '{unavailable_date}'")
        db.rollback()
        raise DatabaseError("Failed to delete musician availability")
    finally:
        db.close()