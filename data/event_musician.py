"""
Data access layer for EventMusician entities.

Provides CRUD operations for event musician assignment management in the Musical Band API.

Functions:
    - get_by_event: Get musicians assigned to an event
    - get_by_musician: Get events a musician is assigned to
    - get_by_event_and_musician: Get specific assignment
    - is_assigned_to_event: Check if musician is assigned to event
    - create: Create new assignment
    - create_bulk: Create multiple assignments
    - update: Update existing assignment
    - delete: Delete assignment
"""

import logging
from config.database import SessionLocal
from models.event_musician import EventMusician
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from sqlalchemy.orm import selectinload
from exceptions import DatabaseError, DatabaseConnectionError

logger = logging.getLogger(__name__)


def get_by_event(event_id: int) -> list[EventMusician]:
    """
    Retrieve all musician assignments for a specific event.

    Args:
        event_id: The ID of the event.

    Returns:
        List of EventMusician objects for the event.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(EventMusician).options(
            selectinload(EventMusician.musician),
            selectinload(EventMusician.event)
        ).filter(EventMusician.event_id == event_id).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting musicians for event '{event_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting musicians for event '{event_id}'")
        raise DatabaseError("Failed to get event musicians")
    finally:
        db.close()


def get_by_musician(musician_id: int) -> list[EventMusician]:
    """
    Retrieve all event assignments for a specific musician.

    Args:
        musician_id: The ID of the musician.

    Returns:
        List of EventMusician objects for the musician.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(EventMusician).options(
            selectinload(EventMusician.event),
            selectinload(EventMusician.musician)
        ).filter(EventMusician.musician_id == musician_id).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting events for musician '{musician_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting events for musician '{musician_id}'")
        raise DatabaseError("Failed to get musician events")
    finally:
        db.close()


def get_by_id(assignment_id: int) -> EventMusician | None:
    """
    Retrieve an assignment by its ID.

    Args:
        assignment_id: The ID of the assignment.

    Returns:
        The EventMusician object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(EventMusician).filter(
            EventMusician.id == assignment_id
        ).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting assignment by id '{assignment_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting assignment by id '{assignment_id}'")
        raise DatabaseError("Failed to get event musician assignment")
    finally:
        db.close()


def get_by_event_and_musician(event_id: int, musician_id: int) -> EventMusician | None:
    """
    Retrieve a specific assignment for an event and musician.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.

    Returns:
        The EventMusician object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(EventMusician).options(
            selectinload(EventMusician.musician)
        ).filter(
            EventMusician.event_id == event_id,
            EventMusician.musician_id == musician_id
        ).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting assignment for event '{event_id}' and musician '{musician_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting assignment for event '{event_id}' and musician '{musician_id}'")
        raise DatabaseError("Failed to get event musician assignment")
    finally:
        db.close()


def is_assigned_to_event(event_id: int, musician_id: int) -> bool:
    """
    Check if a musician is assigned to a specific event.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.

    Returns:
        True if assigned, False otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        assignment = db.query(EventMusician).filter(
            EventMusician.event_id == event_id,
            EventMusician.musician_id == musician_id
        ).first()
        return assignment is not None
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while checking assignment for event '{event_id}' and musician '{musician_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while checking assignment for event '{event_id}' and musician '{musician_id}'")
        raise DatabaseError("Failed to check musician assignment")
    finally:
        db.close()


def create(musician: EventMusician) -> EventMusician:
    """
    Create a new event musician assignment in the database.

    Args:
        musician: The EventMusician object to create.

    Returns:
        The created EventMusician object.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails (e.g., duplicate assignment).
    """
    db = SessionLocal()
    try:
        db.add(musician)
        db.commit()
        db.refresh(musician)
        # Load relationships
        db.refresh(musician, ['musician', 'event'])
        return musician
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while creating assignment for event '{musician.event_id}' and musician '{musician.musician_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating assignment for event '{musician.event_id}' and musician '{musician.musician_id}'")
        db.rollback()
        raise DatabaseError("Failed to create event musician")
    finally:
        db.close()


def create_bulk(musicians: list[EventMusician]) -> list[EventMusician]:
    """
    Create multiple event musician assignments in bulk.

    Args:
        musicians: List of EventMusician objects to create.

    Returns:
        List of created EventMusician objects.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db.add_all(musicians)
        db.commit()
        for musician in musicians:
            db.refresh(musician)
        return musicians
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while bulk creating event musician assignments")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while bulk creating event musician assignments")
        db.rollback()
        raise DatabaseError("Failed to bulk create event musicians")
    finally:
        db.close()


def update(musician: EventMusician, updates: dict) -> EventMusician | None:
    """
    Update an existing event musician assignment in the database.

    Args:
        musician: The EventMusician object to update.
        updates: Dict of field updates.

    Returns:
        The updated EventMusician object, or None if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_musician = db.query(EventMusician).filter(
            EventMusician.id == musician.id
        ).first()
        if db_musician:
            for key, value in updates.items():
                if hasattr(db_musician, key):
                    setattr(db_musician, key, value)
            db.commit()
            db.refresh(db_musician)
            # Load relationships
            db.refresh(db_musician, ['musician'])
        return db_musician
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while updating assignment '{musician.id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating assignment '{musician.id}'")
        db.rollback()
        raise DatabaseError("Failed to update event musician")
    finally:
        db.close()


def delete(musician_id: int) -> bool:
    """
    Delete an event musician assignment from the database.

    Args:
        musician_id: The ID of the assignment to delete.

    Returns:
        True if deleted, False if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_musician = db.query(EventMusician).filter(
            EventMusician.id == musician_id
        ).first()
        if db_musician:
            db.delete(db_musician)
            db.commit()
            return True
        return False
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while deleting assignment '{musician_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting assignment '{musician_id}'")
        db.rollback()
        raise DatabaseError("Failed to delete event musician")
    finally:
        db.close()