"""
Data access layer for MusicianEventPayment entities.

Provides CRUD operations for musician event payment management in the Musical Band API.

Functions:
    - get_one: Get payment by ID
    - get_payments_by_event: Get all payments for an event
    - get_payments_by_musician: Get all payments by a musician
    - get_payments_by_event_and_musician: Get payments for specific event-musician pair
    - create: Create a new payment
    - modify: Update an existing payment
    - delete: Delete a payment
    - get_total_paid_by_musician_for_event: Calculate total paid by musician for event
    - get_total_paid_by_musician: Calculate total paid by musician across all events
"""

import logging
from decimal import Decimal
from config.database import SessionLocal
from models.musician_event_payment import MusicianEventPayment
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from sqlalchemy import func
from exceptions import DatabaseError, DatabaseConnectionError
from data.integrity_checker import check_integrity_before_deletion
from exceptions import ConflictError

logger = logging.getLogger(__name__)


def get_one(payment_id: int) -> MusicianEventPayment | None:
    """
    Retrieve a payment by its ID.

    Args:
        payment_id: The ID of the payment to retrieve.

    Returns:
        The MusicianEventPayment object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(MusicianEventPayment).filter(MusicianEventPayment.id == payment_id).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting musician payment '{payment_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting musician payment '{payment_id}'")
        raise DatabaseError("Failed to get musician payment")
    finally:
        db.close()


def get_payments_by_event(event_id: int) -> list[MusicianEventPayment]:
    """
    Retrieve all payments for a specific event.

    Args:
        event_id: The ID of the event.

    Returns:
        List of MusicianEventPayment objects for the event.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(MusicianEventPayment).filter(MusicianEventPayment.event_id == event_id).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting musician payments for event '{event_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting musician payments for event '{event_id}'")
        raise DatabaseError("Failed to get musician payments")
    finally:
        db.close()


def get_payments_by_musician(musician_id: int) -> list[MusicianEventPayment]:
    """
    Retrieve all payments made to a specific musician.

    Args:
        musician_id: The ID of the musician.

    Returns:
        List of MusicianEventPayment objects for the musician.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(MusicianEventPayment).filter(MusicianEventPayment.musician_id == musician_id).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting musician payments for musician '{musician_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting musician payments for musician '{musician_id}'")
        raise DatabaseError("Failed to get musician payments")
    finally:
        db.close()


def get_payments_by_event_and_musician(event_id: int, musician_id: int) -> list[MusicianEventPayment]:
    """
    Retrieve all payments for a specific event and musician.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.

    Returns:
        List of MusicianEventPayment objects for the event-musician pair.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(MusicianEventPayment).filter(
            MusicianEventPayment.event_id == event_id,
            MusicianEventPayment.musician_id == musician_id
        ).all()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting musician payments for event '{event_id}' and musician '{musician_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting musician payments for event '{event_id}' and musician '{musician_id}'")
        raise DatabaseError("Failed to get musician payments")
    finally:
        db.close()


def create(payment: MusicianEventPayment) -> MusicianEventPayment:
    """
    Create a new payment.

    Args:
        payment: The MusicianEventPayment object to create.

    Returns:
        The created MusicianEventPayment object with ID assigned.

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
        logger.error("Database connection error while creating musician payment")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating musician payment: {e}")
        raise DatabaseError("Failed to create musician payment")
    finally:
        db.close()


def modify(payment: MusicianEventPayment) -> MusicianEventPayment:
    """
    Update an existing payment.

    Args:
        payment: The MusicianEventPayment object with updated data.

    Returns:
        The updated MusicianEventPayment object.

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
        logger.error("Database connection error while modifying musician payment")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while modifying musician payment: {e}")
        raise DatabaseError("Failed to modify musician payment")
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
        payment = db.query(MusicianEventPayment).filter(MusicianEventPayment.id == payment_id).first()
        if not payment:
            return False

        # Check integrity constraints BEFORE attempting delete
        integrity_error = check_integrity_before_deletion('musician_event_payment', payment_id)
        if integrity_error:
            raise ConflictError(integrity_error)

        db.delete(payment)
        db.commit()
        return True
    except (OperationalError, InterfaceError) as e:
        db.rollback()
        logger.error(f"Database connection error while deleting musician payment '{payment_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while deleting musician payment '{payment_id}': {str(e)}")

        # Check for constraint violations that might slip through our integrity check
        error_str = str(e).upper()
        if ("'C': '23503'" in error_str or '23503' in error_str or
            "'C': '23502'" in error_str or '23502' in error_str):
            raise ConflictError("This musician payment cannot be deleted because it has associated records. Please remove these associations first.")
        else:
            raise DatabaseError("Failed to delete musician payment")
    except ConflictError:
        # Re-raise ConflictError as-is
        raise
    finally:
        db.close()


def get_total_paid_by_musician_for_event(event_id: int, musician_id: int) -> Decimal:
    """
    Calculate the total amount paid to a musician for a specific event.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.

    Returns:
        The total amount paid as Decimal.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        result = db.query(func.coalesce(func.sum(MusicianEventPayment.amount), 0)).filter(
            MusicianEventPayment.event_id == event_id,
            MusicianEventPayment.musician_id == musician_id
        ).scalar()
        return result or Decimal("0.00")
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while calculating total paid for event '{event_id}' and musician '{musician_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while calculating total paid for event '{event_id}' and musician '{musician_id}'")
        raise DatabaseError("Failed to calculate total paid")
    finally:
        db.close()


def get_total_paid_by_musician(musician_id: int) -> Decimal:
    """
    Calculate the total amount paid to a musician across all events.

    Args:
        musician_id: The ID of the musician.

    Returns:
        The total amount paid as Decimal.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        result = db.query(func.coalesce(func.sum(MusicianEventPayment.amount), 0)).filter(
            MusicianEventPayment.musician_id == musician_id
        ).scalar()
        return result or Decimal("0.00")
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while calculating total paid for musician '{musician_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while calculating total paid for musician '{musician_id}'")
        raise DatabaseError("Failed to calculate total paid")
    finally:
        db.close()