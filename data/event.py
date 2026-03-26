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
from datetime import datetime
from decimal import Decimal
from config.database import SessionLocal
from models.event import Event
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from sqlalchemy.orm import joinedload
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


def get_one_with_user(event_id: int) -> Event | None:
    """
    Retrieve an event by its ID with user information loaded (JOIN).

    Args:
        event_id: The ID of the event to retrieve.

    Returns:
        The Event object with user loaded if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(Event).options(joinedload(Event.user)).filter(Event.id == event_id).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting event '{event_id}' with user")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting event '{event_id}' with user")
        raise DatabaseError("Failed to get event with user")
    finally:
        db.close()


def get_all_with_users() -> list[Event]:
    """
    Retrieve all events from the database with user information loaded (JOIN).

    Returns:
        List of Event objects with users loaded.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(Event).options(joinedload(Event.user)).all()
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting all events with users")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while getting all events with users")
        raise DatabaseError("Failed to get events with users")
    finally:
        db.close()


def get_paginated(
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
    search: str | None = None,
    user_id: int | None = None,
    start_after: datetime = None,
    end_before: datetime = None,
    sort_by: str = "created_at",
    order: str = "desc"
) -> tuple[list[Event], int]:
    """
    Retrieve paginated and filtered events from the database.

    Args:
        page: Page number (1-indexed).
        limit: Number of items per page.
        status: Filter by event status.
        search: Search term for name and place fields.
        user_id: Filter by user ID.
        start_after: Filter events starting after this datetime.
        end_before: Filter events ending before this datetime.
        sort_by: Field to sort by (name, start_datetime, created_at).
        order: Sort order (asc or desc).

    Returns:
        Tuple of (list of Event objects, total count).

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        query = db.query(Event).options(joinedload(Event.user))
        
        # Apply filters
        if status:
            query = query.filter(Event.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Event.name.ilike(search_term)) | (Event.place.ilike(search_term))
            )
        
        if user_id is not None:
            query = query.filter(Event.user_id == user_id)
        
        if start_after:
            query = query.filter(Event.start_datetime >= start_after)
        
        if end_before:
            query = query.filter(Event.end_datetime <= end_before)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        sort_column = Event.created_at
        if sort_by == "name":
            sort_column = Event.name
        elif sort_by == "start_datetime":
            sort_column = Event.start_datetime
        
        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # Apply pagination
        offset = (page - 1) * limit
        events = query.offset(offset).limit(limit).all()
        
        return events, total
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting paginated events")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting paginated events: {str(e)}")
        raise DatabaseError("Failed to get paginated events")
    finally:
        db.close()


def get_events_by_month(year: int, month: int, user_id: int | None = None) -> list[Event]:
    """
    Retrieve events for a specific month (calendar view).

    Args:
        year: Year (e.g., 2026).
        month: Month (1-12).
        user_id: Optional user ID to filter events by owner.

    Returns:
        List of Event objects for the specified month.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        # Calculate start and end of month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        query = db.query(Event).options(joinedload(Event.user)).filter(
            Event.start_datetime >= start_date,
            Event.start_datetime < end_date
        )
        
        if user_id is not None:
            query = query.filter(Event.user_id == user_id)
        
        return query.order_by(Event.start_datetime.asc()).all()
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting events by month")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting events by month: {str(e)}")
        raise DatabaseError("Failed to get events by month")
    except ValueError as e:
        logger.error(f"Invalid year/month values: {str(e)}")
        raise DatabaseError("Invalid year or month values")
    finally:
        db.close()


def set_price(event_id: int, price: Decimal) -> Event | None:
    """
    Set the price of an event.

    Args:
        event_id: The ID of the event to update.
        price: The new price value.

    Returns:
        The updated Event object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    from decimal import Decimal
    db = SessionLocal()
    try:
        existing_event = db.query(Event).filter(Event.id == event_id).first()
        if existing_event is None:
            return None

        existing_event.price = price

        db.commit()
        db.refresh(existing_event)
        logger.info(f"Set price {price} on event with id {event_id}")
        return existing_event
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while setting price on event '{event_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while setting price on event '{event_id}': {str(e)}")
        db.rollback()
        raise DatabaseError("Failed to set event price")
    finally:
        db.close()


def get_price(event_id: int) -> Decimal | None:
    """
    Get the price of an event.

    Args:
        event_id: The ID of the event.

    Returns:
        The price as Decimal if found and set, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if event is None:
            return None

        return event.price
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting price for event '{event_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting price for event '{event_id}': {str(e)}")
        raise DatabaseError("Failed to get event price")
    finally:
        db.close()
