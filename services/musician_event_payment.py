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
from datetime import datetime, timezone

from models.musician_event_payment import MusicianEventPayment
from models.event_musician import PaymentStatus
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

    # Validate payment amount is positive
    if payment_data_input.amount <= Decimal("0.00"):
        raise ValidationError("Payment amount must be positive")

    # Get existing payments for this musician-event pair
    existing_payments = payment_data.get_payments_by_event_and_musician(
        payment_data_input.event_id,
        payment_data_input.musician_id
    )

    # Calculate total already paid
    total_already_paid = payment_data.get_total_paid_by_musician_for_event(
        payment_data_input.event_id,
        payment_data_input.musician_id
    )

    # Calculate total advance paid
    total_advance_paid = sum(p.amount for p in existing_payments if p.payment_type == PaymentType.ADVANCE)

    # Validate payment type business logic
    if payment_data_input.payment_type == PaymentType.ADVANCE:
        # Total ADVANCE payments cannot exceed 50% of salary
        max_advance = assignment.salary * Decimal("0.5")
        total_advance_after = total_advance_paid + payment_data_input.amount
        if total_advance_after > max_advance:
            raise ValidationError(
                f"Total ADVANCE payments cannot exceed 50% of salary. "
                f"Maximum total advance: {max_advance}, "
                f"Current total advance: {total_advance_paid}, "
                f"Requested amount: {payment_data_input.amount}, "
                f"Salary: {assignment.salary}"
            )

        # ADVANCE cannot exceed remaining salary
        if total_already_paid + payment_data_input.amount > assignment.salary:
            raise ValidationError(
                f"ADVANCE payment would exceed remaining salary. "
                f"Already paid: {total_already_paid}, "
                f"Payment amount: {payment_data_input.amount}, "
                f"Salary: {assignment.salary}"
            )

    elif payment_data_input.payment_type == PaymentType.REMAINING:
        # REMAINING can only be created if ADVANCE payments exist
        if total_advance_paid == Decimal("0.00"):
            raise ValidationError(
                "Cannot create REMAINING payment without prior ADVANCE payments. Use TOTAL payment type instead."
            )

        # REMAINING should fill the gap after ADVANCE
        remaining_amount = assignment.salary - total_already_paid
        if remaining_amount <= Decimal("0.00"):
            raise ValidationError(
                f"No remaining amount to pay. Total already paid: {total_already_paid}, Salary: {assignment.salary}"
            )
        if payment_data_input.amount > remaining_amount:
            raise ValidationError(
                f"REMAINING payment would exceed remaining salary. "
                f"Already paid: {total_already_paid}, "
                f"Payment amount: {payment_data_input.amount}, "
                f"Salary: {assignment.salary}"
            )
        if payment_data_input.amount < remaining_amount:
            raise ValidationError(
                f"REMAINING payment must equal the full remaining salary. "
                f"Expected: {remaining_amount}, Got: {payment_data_input.amount}"
            )

    elif payment_data_input.payment_type == PaymentType.TOTAL:
        # TOTAL should be the full payment, no partials allowed
        if existing_payments:
            raise ValidationError("Cannot create TOTAL payment when partial payments exist")
        if payment_data_input.amount != assignment.salary:
            raise ValidationError(
                f"TOTAL payment must equal the full salary amount. "
                f"Expected: {assignment.salary}, Got: {payment_data_input.amount}"
            )

    # Validate payment timing based on event dates
    current_time = datetime.now(timezone.utc)

    if payment_data_input.payment_type == PaymentType.ADVANCE:
        # ADVANCE payments must be made before event start date
        if current_time >= event.start_datetime.replace(tzinfo=timezone.utc):
            raise ValidationError(
                f"ADVANCE payments can only be made before event start date. "
                f"Event starts: {event.start_datetime}, Current time: {current_time}"
            )

    elif payment_data_input.payment_type in [PaymentType.REMAINING, PaymentType.TOTAL]:
        # REMAINING and TOTAL payments must be made on or after event end date
        if current_time < event.end_datetime.replace(tzinfo=timezone.utc):
            raise ValidationError(
                f"{payment_data_input.payment_type.value} payments can only be made on or after event end date. "
                f"Event ends: {event.end_datetime}, Current time: {current_time}"
            )

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

    # Update payment status in event_musician table
    new_total_paid = total_already_paid + payment_data_input.amount

    if new_total_paid >= assignment.salary:
        new_status = PaymentStatus.COMPLETED
    elif new_total_paid > 0:
        new_status = PaymentStatus.PARTIAL
    else:
        new_status = PaymentStatus.PENDING

    assignment_data.update_payment_status(
        payment_data_input.event_id,
        payment_data_input.musician_id,
        new_status.value
    )

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


def get_payments_for_event(event_id: int, musician_id: int, current_user: dict) -> list[MusicianEventPaymentResponse]:
    """
    Get all payments for a specific musician in an event.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.
        current_user: The current user making the request.

    Returns:
        List of MusicianEventPaymentResponse objects.

    Raises:
        NotFoundError: If event doesn't exist.
        UnauthorizedError: If user not authorized.
    """
    # Check if current user can view this musician's payments for this event
    event = event_data.get_one(event_id)
    if not event:
        raise NotFoundError(f"Event with id {event_id} not found")

    user_role = current_user['role']
    if user_role == 'admin':
        # Admins can view all payments
        pass
    elif user_role in ['musician', 'auxiliar_musician']:
        # Musicians can only view their own payments
        if current_user['id'] != musician_id:
            raise UnauthorizedError("You can only view your own payment information")
    else:
        # Other roles cannot access
        raise UnauthorizedError("Unauthorized to view musician payments")

    payments = payment_data.get_payments_by_event_and_musician(event_id, musician_id)

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
    # Check if current user can view this musician's payments for this event
    event = event_data.get_one(event_id)
    if not event:
        raise NotFoundError(f"Event with id {event_id} not found")

    user_role = current_user['role']
    if user_role == 'admin':
        # Admins can view all payments
        pass
    elif user_role in ['musician', 'auxiliar_musician']:
        # Musicians can only view their own payments
        if current_user['id'] != musician_id:
            raise UnauthorizedError("You can only view your own payment information")
    else:
        # Other roles cannot access
        raise UnauthorizedError("Unauthorized to view musician payments")

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