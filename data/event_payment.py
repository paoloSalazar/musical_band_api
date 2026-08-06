"""
Data access layer for EventPayment entities.

Provides CRUD operations for event payment management in the Musical Band API.

Functions:
    - get_one: Get payment by ID
    - get_payments_by_event: Get all payments for an event
    - get_payments_by_user: Get all payments by a user
    - create: Create a new payment
    - modify: Update an existing payment
    - delete: Delete a payment
    - get_total_paid: Calculate total paid for an event
    - get_pending_balance: Calculate pending balance for an event
"""

import logging
from decimal import Decimal
from config.database import SessionLocal
from models.event_payment import EventPayment
from models.event import Event
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from sqlalchemy import func
from exceptions import DatabaseError, DatabaseConnectionError
from data.integrity_checker import check_integrity_before_deletion
from exceptions import ConflictError

logger = logging.getLogger(__name__)


def get_one(payment_id: int) -> EventPayment | None:
    """
    Retrieve a payment by its ID.

    Args:
        payment_id: The ID of the payment to retrieve.

    Returns:
        The EventPayment object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(EventPayment).filter(EventPayment.id == payment_id).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting payment '{payment_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting payment '{payment_id}'")
        raise DatabaseError("Failed to get payment")
    finally:
        db.close()


def get_payments_by_event(event_id: int) -> list[EventPayment]:
    """
    Retrieve all payments for a specific event.

    Args:
        event_id: The ID of the event.

    Returns:
        List of EventPayment objects for the event.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(EventPayment).filter(EventPayment.event_id == event_id).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting payments for event '{event_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting payments for event '{event_id}'")
        raise DatabaseError("Failed to get payments")
    finally:
        db.close()


def get_payments_by_user(user_id: int) -> list[EventPayment]:
    """
    Retrieve all payments made by a specific user.

    Args:
        user_id: The ID of the user.

    Returns:
        List of EventPayment objects made by the user.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(EventPayment).filter(EventPayment.user_id == user_id).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting payments for user '{user_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting payments for user '{user_id}'")
        raise DatabaseError("Failed to get payments")
    finally:
        db.close()


def create(payment: EventPayment) -> EventPayment:
    """
    Create a new payment.

    Args:
        payment: The EventPayment object to create.

    Returns:
        The created EventPayment object with ID assigned.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    except (OperationalError, InterfaceError) as e:
        db.rollback()
        logger.error("Database connection error while creating payment")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating payment: {e}")
        raise DatabaseError("Failed to create payment")
    finally:
        db.close()


def modify(payment: EventPayment) -> EventPayment:
    """
    Update an existing payment.

    Args:
        payment: The EventPayment object with updated data.

    Returns:
        The updated EventPayment object.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db.commit()
        return payment
    except (OperationalError, InterfaceError) as e:
        db.rollback()
        logger.error("Database connection error while modifying payment")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while modifying payment: {e}")
        raise DatabaseError("Failed to modify payment")
    finally:
        db.close()


def delete(payment_id: int) -> bool:
    """
    Delete a payment by its ID.

    Args:
        payment_id: The ID of the payment to delete.

    Returns:
        True if deleted successfully.

    Raises:
        DatabaseConnectionError: If database connection fails.
        ConflictError: If payment has related records preventing deletion.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        payment = db.query(EventPayment).filter(EventPayment.id == payment_id).first()
        if not payment:
            return False

        # Check integrity constraints BEFORE attempting delete
        integrity_error = check_integrity_before_deletion('event_payment', payment_id)
        if integrity_error:
            raise ConflictError(integrity_error)

        db.delete(payment)
        db.commit()
        return True
    except (OperationalError, InterfaceError) as e:
        db.rollback()
        logger.error(f"Database connection error while deleting payment '{payment_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while deleting payment '{payment_id}': {str(e)}")

        # Check for constraint violations that might slip through our integrity check
        error_str = str(e).upper()
        if ("'C': '23503'" in error_str or '23503' in error_str or
            "'C': '23502'" in error_str or '23502' in error_str):
            raise ConflictError("This payment cannot be deleted because it has associated records. Please remove these associations first.")
        else:
            raise DatabaseError("Failed to delete payment")
    except ConflictError:
        # Re-raise ConflictError as-is
        raise
    finally:
        db.close()


def get_total_paid(event_id: int) -> Decimal:
    """
    Calculate the total amount paid for an event.

    Args:
        event_id: The ID of the event.

    Returns:
        The total amount paid as Decimal.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        result = db.query(func.coalesce(func.sum(EventPayment.amount), 0)).filter(
            EventPayment.event_id == event_id
        ).scalar()
        return result or Decimal("0.00")
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while calculating total paid for event '{event_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while calculating total paid for event '{event_id}'")
        raise DatabaseError("Failed to calculate total paid")
    finally:
        db.close()


def get_pending_balance(event_id: int, final_price: Decimal | int) -> Decimal:
    """
    Calculate the pending balance for an event.

    Args:
        event_id: The ID of the event.
        final_price: The final price of the event.

    Returns:
        The pending balance as Decimal.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    total_paid = get_total_paid(event_id)
    final_price_decimal = Decimal(str(final_price))
    pending = final_price_decimal - total_paid
    return max(pending, Decimal("0.00"))