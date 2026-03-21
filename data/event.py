"""
Data access layer for Event entities.

Provides CRUD operations for event management in the Musical Band API.

Functions:
    - get_one: Get event by ID
    - get_all: Get all events
    - create: Create a new event
    - modify: Update an existing event
    - delete: Delete an event
"""

import logging
from config.database import SessionLocal
from models.event import Event
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from exceptions import DatabaseError, DatabaseConnectionError

logger = logging.getLogger(__name__)


def get_one(event_id: int) -> Event | None:
    """
    Retrieve an event by its ID.

    Args:
        event_id: The ID of the event to retrieve.

    Returns:
        The Event object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(Event).filter(Event.id == event_id).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting event '{event_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting event '{event_id}'")
        raise DatabaseError("Failed to get event")
    finally:
        db.close()


def get_one_by_id(event_id: int) -> Event | None:
    """
    Retrieve an event by its ID (alias for get_one).

    Args:
        event_id: The ID of the event to retrieve.

    Returns:
        The Event object if found, None otherwise.
    """
    return get_one(event_id)


def get_all() -> list[Event]:
    """
    Retrieve all events from the database.

    Returns:
        List of Event objects.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(Event).all()
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting all events")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while getting all events")
        raise DatabaseError("Failed to get events")
    finally:
        db.close()


def create(event: Event) -> Event:
    """
    Create a new event in the database.

    Args:
        event: The Event object to create.

    Returns:
        The created Event object.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db.add(event)
        db.commit()
        db.refresh(event)
        logger.info(f"Created event with id {event.id}")
        return event
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while creating event")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating event: {str(e)}")
        db.rollback()
        raise DatabaseError("Failed to create event")
    finally:
        db.close()


def modify(event: Event) -> Event | None:
    """
    Update an existing event in the database.

    Args:
        event: The Event object with updated data.

    Returns:
        The updated Event object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        existing_event = db.query(Event).filter(Event.id == event.id).first()
        if existing_event is None:
            return None

        # Update fields
        existing_event.name = event.name
        existing_event.place = event.place
        existing_event.description = event.description
        existing_event.start_datetime = event.start_datetime
        existing_event.end_datetime = event.end_datetime
        existing_event.is_all_day = event.is_all_day
        if event.status:
            existing_event.status = event.status

        db.commit()
        db.refresh(existing_event)
        logger.info(f"Modified event with id {event.id}")
        return existing_event
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while modifying event '{event.id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while modifying event '{event.id}': {str(e)}")
        db.rollback()
        raise DatabaseError("Failed to modify event")
    finally:
        db.close()


def delete(event_id: int) -> bool:
    """
    Delete an event from the database.

    Args:
        event_id: The ID of the event to delete.

    Returns:
        True if event was deleted, False if event not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if event is None:
            return False

        db.delete(event)
        db.commit()
        logger.info(f"Deleted event with id {event_id}")
        return True
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while deleting event '{event_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting event '{event_id}': {str(e)}")
        db.rollback()
        raise DatabaseError("Failed to delete event")
    finally:
        db.close()


def get_events_in_date_range(start_date: str, end_date: str, user_id: int | None = None) -> list[Event]:
    """
    Retrieve events within a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        user_id: Optional user ID to filter events by owner.

    Returns:
        List of Event objects within the date range.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        from datetime import datetime
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        # Include the entire end date by setting time to 23:59:59
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        
        query = db.query(Event).filter(
            Event.start_datetime >= start_datetime,
            Event.start_datetime <= end_datetime
        )
        
        if user_id is not None:
            query = query.filter(Event.user_id == user_id)
        
        return query.all()
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting events in date range")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting events in date range: {str(e)}")
        raise DatabaseError("Failed to get events in date range")
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        raise DatabaseError("Invalid date format")
    finally:
        db.close()
