"""
Service layer for MusicianEventPayment business logic.

Provides business logic operations for musician payment management,
including validation and data transformation.

Functions:
    - create_musician_payment: Create a new musician payment with validation
    - get_payments_for_event: Get all payments for an event (event owner only)
    - get_payments_for_musician: Get all payments for a musician (musician only)
    - get_payment_summary_for_musician_event: Get payment summary for musician-event pair
    - get_payment_summary_for_musician: Get total payment summary for musician
"""
import logging
from decimal import Decimal
from datetime import datetime

from models.musician_event_payment import MusicianEventPayment
from schemas.musician_event_payment import (
    MusicianEventPaymentCreate,
    MusicianEventPaymentResponse,
    MusicianPaymentSummaryResponse
)
from schemas.event_payment import PaymentType
import data.musician_event_payment as payment_data
import data.event as event_data
import data.user as user_data
import data.event_musician as assignment_data
from exceptions import NotFoundError, ValidationError, UnauthorizedError

logger = logging.getLogger(__name__)


def create_musician_payment(
    payment_data_input: MusicianEventPaymentCreate,
    current_user: dict
) -> MusicianEventPaymentResponse:
    """
    Create a new musician payment with business validation.

    Args:
        payment_data_input: The payment data to create.
        current_user: The current user making the request.

    Returns:
        MusicianEventPaymentResponse with created payment data.

    Raises:
        NotFoundError: If event or musician doesn't exist.
        ValidationError: If payment validation fails.
        UnauthorizedError: If user not authorized.
    """
    # Check if current user can manage this event's payments (admin or event owner)
    event = event_data.get_one(payment_data_input.event_id)
    if not event:
        raise NotFoundError(f"Event with id {payment_data_input.event_id} not found")

    if current_user['role'] != 'admin' and event.user_id != current_user['id']:
        raise UnauthorizedError("You can only manage payments for your own events")

    # Check if musician exists
    musician = user_data.get_one_by_id(payment_data_input.musician_id)
    if not musician:
        raise NotFoundError(f"Musician with id {payment_data_input.musician_id} not found")

    # Check if musician is assigned to this event
    assignment = assignment_data.get_by_event_and_musician(
        payment_data_input.event_id,
        payment_data_input.musician_id
    )
    if not assignment:
        raise ValidationError("Musician is not assigned to this event")

    # Validate payment amount doesn't exceed salary
    if payment_data_input.amount > assignment.salary:
        raise ValidationError(
            f"Payment amount ({payment_data_input.amount}) exceeds musician's salary "
            f"({assignment.salary})"
        )

    # Validate payment amount is positive
    if payment_data_input.amount <= Decimal("0.00"):
        raise ValidationError("Payment amount must be positive")

    # Create payment record
    payment = MusicianEventPayment(
        event_id=payment_data_input.event_id,
        musician_id=payment_data_input.musician_id,
        amount=payment_data_input.amount,
        payment_type=PaymentType(payment_data_input.payment_type.value),
        payment_date=payment_data_input.payment_date,
        notes=payment_data_input.notes
    )

    created = payment_data.create(payment)

    # Convert to response schema
    return MusicianEventPaymentResponse(
        id=created.id,
        event_id=created.event_id,
        musician_id=created.musician_id,
        amount=created.amount,
        payment_type=PaymentType(created.payment_type) if isinstance(created.payment_type, str) else PaymentType(created.payment_type.value),
        payment_date=created.payment_date,
        notes=created.notes,
        created_at=created.created_at,
        updated_at=created.updated_at
    )


def get_payments_for_event(event_id: int, current_user: dict) -> list[MusicianEventPaymentResponse]:
    """
    Get all musician payments for an event.

    Args:
        event_id: The ID of the event.
        current_user: The current user making the request.

    Returns:
        List of MusicianEventPaymentResponse objects.

    Raises:
        NotFoundError: If event doesn't exist.
        UnauthorizedError: If user not authorized.
    """
    # Check if current user can view this event's payments
    event = event_data.get_one(event_id)
    if not event:
        raise NotFoundError(f"Event with id {event_id} not found")

    if current_user['role'] != 'admin' and event.user_id != current_user['id']:
        raise UnauthorizedError("You can only manage payments for your own events")

    payments = payment_data.get_payments_by_event(event_id)

    # Convert to response schemas
    return [
        MusicianEventPaymentResponse(
            id=p.id,
            event_id=p.event_id,
            musician_id=p.musician_id,
            amount=p.amount,
            payment_type=PaymentType(p.payment_type) if isinstance(p.payment_type, str) else PaymentType(p.payment_type.value),
            payment_date=p.payment_date,
            notes=p.notes,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in payments
    ]


def get_payments_for_musician(musician_id: int, current_user: dict) -> list[MusicianEventPaymentResponse]:
    """
    Get all payments for a musician.

    Args:
        musician_id: The ID of the musician.
        current_user: The current user making the request.

    Returns:
        List of MusicianEventPaymentResponse objects.

    Raises:
        UnauthorizedError: If user not authorized.
    """
    # Check if current user can view this musician's payments
    if current_user['role'] != 'admin' and current_user['id'] != musician_id:
        raise UnauthorizedError("You can only view your own payment history")

    payments = payment_data.get_payments_by_musician(musician_id)

    # Convert to response schemas
    return [
        MusicianEventPaymentResponse(
            id=p.id,
            event_id=p.event_id,
            musician_id=p.musician_id,
            amount=p.amount,
            payment_type=PaymentType(p.payment_type) if isinstance(p.payment_type, str) else PaymentType(p.payment_type.value),
            payment_date=p.payment_date,
            notes=p.notes,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in payments
    ]


def get_payment_summary_for_musician_event(
    event_id: int,
    musician_id: int,
    current_user: dict
) -> MusicianPaymentSummaryResponse:
    """
    Get payment summary for a musician-event pair.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.
        current_user: The current user making the request.

    Returns:
        MusicianPaymentSummaryResponse with summary data.

    Raises:
        NotFoundError: If event doesn't exist.
        UnauthorizedError: If user not authorized.
    """
    # Check if current user can view this event's payments
    event = event_data.get_one(event_id)
    if not event:
        raise NotFoundError(f"Event with id {event_id} not found")

    if current_user['role'] != 'admin' and event.user_id != current_user['id']:
        raise UnauthorizedError("You can only manage payments for your own events")

    total_paid = payment_data.get_total_paid_by_musician_for_event(event_id, musician_id)
    payment_count = len(payment_data.get_payments_by_event_and_musician(event_id, musician_id))

    return MusicianPaymentSummaryResponse(
        musician_id=musician_id,
        total_paid=total_paid,
        payment_count=payment_count
    )


def get_payment_summary_for_musician(musician_id: int, current_user: dict) -> MusicianPaymentSummaryResponse:
    """
    Get total payment summary for a musician across all events.

    Args:
        musician_id: The ID of the musician.
        current_user: The current user making the request.

    Returns:
        MusicianPaymentSummaryResponse with summary data.

    Raises:
        UnauthorizedError: If user not authorized.
    """
    # Check if current user can view this musician's payments
    if current_user['role'] != 'admin' and current_user['id'] != musician_id:
        raise UnauthorizedError("You can only view your own payment history")

    total_paid = payment_data.get_total_paid_by_musician(musician_id)
    payment_count = len(payment_data.get_payments_by_musician(musician_id))

    return MusicianPaymentSummaryResponse(
        musician_id=musician_id,
        total_paid=total_paid,
        payment_count=payment_count
    )