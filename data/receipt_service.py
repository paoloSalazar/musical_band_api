"""
Data access layer for receipt data retrieval.

Functions:
    - get_receipt_data: Get receipt data for an event
"""

import logging
from config.database import SessionLocal
from models.event import Event
from models.user import User
from models.event_payment import EventPayment
from models.user_detail import UserDetail
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError

logger = logging.getLogger(__name__)


def get_receipt_data(event_id: int) -> dict | None:
    """
    Retrieve receipt data for an event.

    Args:
        event_id: The ID of the event.

    Returns:
        Dictionary with receipt data or None if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        event = db.query(Event).options(
            joinedload(Event.user),
            joinedload(Event.payments)
        ).filter(Event.id == event_id).first()

        if not event:
            return None

        user = event.user
        if not user:
            raise NotFoundError("User not found for event")

        ci = None
        user_details = db.query(UserDetail).filter(
            UserDetail.user_id == user.id,
            UserDetail.detail_type == "ci"
        ).first()
        if user_details:
            ci = user_details.detail_value

        payments = db.query(EventPayment).filter(
            EventPayment.event_id == event_id
        ).all()

        total_paid = sum(float(p.amount) for p in payments) if payments else 0
        balance = float(event.price or 0) - total_paid

        return {
            "event_id": event.id,
            "event_name": event.name,
            "event_place": event.place,
            "event_date": event.start_datetime.strftime("%d/%m/%Y") if event.start_datetime else None,
            "event_price": float(event.price or 0),
            "event_user_id": event.user_id,
            "client_name": f"{user.name} {user.lastname}",
            "client_ci": ci,
            "client_phone": user.phone_number,
            "payments": [{"id": p.id, "amount": float(p.amount)} for p in payments],
            "total_paid": total_paid,
            "balance": balance,
        }
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting receipt for event '{event_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting receipt for event '{event_id}'")
        raise DatabaseError("Failed to get receipt data")
    finally:
        db.close()