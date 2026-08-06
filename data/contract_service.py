"""
Data access layer for contract data retrieval.

Functions:
    - get_contract_data: Get contract data for an event
"""

import logging
from datetime import datetime
from config.database import SessionLocal
from models.event import Event
from models.user import User
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError

logger = logging.getLogger(__name__)


def calculate_event_duration(event) -> str:
    """
    Calculate event duration string.

    Args:
        event: Event object with start_datetime, end_datetime, is_all_day.

    Returns:
        Duration string like "6 Horas" or "3 Horas".
    """
    if event.is_all_day:
        return "6 Horas"

    duration = event.end_datetime - event.start_datetime
    hours = int(duration.total_seconds() // 3600)
    return f"{hours} Horas"


def get_contract_data(event_id: int) -> dict | None:
    """
    Retrieve contract data for an event.

    Args:
        event_id: The ID of the event.

    Returns:
        Dictionary with contract data or None if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        event = db.query(Event).options(joinedload(Event.user)).filter(
            Event.id == event_id
        ).first()

        if not event:
            return None

        user = event.user
        if not user:
            raise NotFoundError("User not found for event")

        return {
            "event_id": event.id,
            "event_name": event.name,
            "event_location": event.place,
            "event_start_datetime": event.start_datetime,
            "event_end_datetime": event.end_datetime,
            "event_price": float(event.price or 0),
            "event_user_id": event.user_id,
            "client_name": f"{user.name} {user.lastname}",
            "client_ci": user.ci,
            "client_phone": user.phone_number,
            "event_duration": calculate_event_duration(event),
        }
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting contract for event '{event_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting contract for event '{event_id}'")
        raise DatabaseError("Failed to get contract data")
    finally:
        db.close()