"""
Service layer for EventPayment business logic.

Provides business logic operations for payment management,
including validation and data transformation.

Functions:
    - create_payment: Create a new payment with validation
    - get_event_payment_summary: Get payment summary for an event
    - validate_payment_amount: Validate payment amount based on rules
    - validate_payment_deadline: Validate payment is before event deadline
"""
import logging
from decimal import Decimal
from datetime import datetime, timedelta

from models.event_payment import EventPayment, PaymentType
from models.event import EventStatus
from schemas.event_payment import (
    EventPaymentCreate,
    EventPaymentResponse,
    EventPaymentSummary,
    PaymentType as SchemaPaymentType
)
import data.event_payment as payment_data
import data.event as event_data
import services.event as event_service
from exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

# Constants
ADVANCE_MINIMUM_PERCENT = 0.30  # 30% minimum for advance payment
PAYMENT_DEADLINE_HOURS = 24  # Payment must be 24 hours before event


def create_payment_data(payment: EventPayment) -> EventPayment:
    """
    Create a new payment record in the database.
    
    Args:
        payment: The EventPayment object to create.
    
    Returns:
        Created EventPayment object.
    """
    return payment_data.create(payment)


def create_payment(
    event_id: int,
    user_id: int,
    amount: Decimal,
    payment_type: SchemaPaymentType,
    notes: str | None = None
) -> EventPaymentResponse:
    """
    Create a new payment with business validation.
    
    Args:
        event_id: The ID of the event being paid for.
        user_id: The ID of the user making the payment.
        amount: The payment amount.
        payment_type: Type of payment (ADVANCE, REMAINING, TOTAL).
        notes: Optional notes for the payment.
    
    Returns:
        EventPaymentResponse with created payment data.
    
    Raises:
        NotFoundError: If event doesn't exist.
        ValidationError: If payment validation fails.
    """
    # Get event to validate it exists and get final price
    event = event_data.get_one(event_id)
    if not event:
        raise NotFoundError(f"Event with ID {event_id} not found")
    
    if event.price is None:
        raise ValidationError("Event final price not set. Please set price before making payments.")
    
    final_price = Decimal(str(event.price))
    
    # Check if TOTAL payment already exists for this event
    existing_payments = payment_data.get_payments_by_event(event_id)
    has_total_payment = any(
        p.payment_type == PaymentType.TOTAL for p in existing_payments
    )
    if has_total_payment:
        raise ValidationError("A TOTAL payment has already been made for this event. No further payments are allowed.")
    
    # Calculate remaining balance and validate ADVANCE/REMAINING don't exceed it
    total_paid = sum(p.amount for p in existing_payments)
    remaining_balance = final_price - total_paid
    
    if payment_type in (SchemaPaymentType.ADVANCE, SchemaPaymentType.REMAINING):
        if amount > remaining_balance:
            raise ValidationError(
                f"Payment amount ({amount}) exceeds remaining balance ({remaining_balance}). "
                f"Final price: {final_price}, Already paid: {total_paid}"
            )
    
    # Validate payment amount
    validate_payment_amount(
        amount=amount,
        payment_type=payment_type,
        final_price=final_price
    )
    
    # Validate payment deadline for advance payments
    validate_payment_deadline(event.start_datetime, payment_type)
    
    # Convert enum to model enum
    model_payment_type = PaymentType(payment_type.value)
    
    # Create payment record
    payment = EventPayment(
        event_id=event_id,
        user_id=user_id,
        amount=amount,
        payment_type=model_payment_type,
        notes=notes
    )
    
    created = create_payment_data(payment)
    
    # Auto-confirm event if status is PENDING
    if event.status == EventStatus.PENDING:
        event_service.change_status(event_id, EventStatus.CONFIRMED)
    
    # Convert to response schema
    return EventPaymentResponse(
        id=created.id,
        event_id=created.event_id,
        user_id=created.user_id,
        amount=created.amount,
        payment_type=SchemaPaymentType(created.payment_type) if isinstance(created.payment_type, str) else SchemaPaymentType(created.payment_type.value),
        payment_date=created.payment_date,
        notes=created.notes,
        created_at=created.created_at
    )


def get_event_payment_summary(event_id: int, final_price: Decimal) -> EventPaymentSummary:
    """
    Get payment summary for an event.
    
    Args:
        event_id: The ID of the event.
        final_price: The final price of the event.
    
    Returns:
        EventPaymentSummary with payment totals.
    """
    total_paid = payment_data.get_total_paid(event_id)
    final_decimal = Decimal(str(final_price))
    pending = final_decimal - total_paid
    
    return EventPaymentSummary(
        event_id=event_id,
        total_paid=total_paid,
        pending_balance=max(pending, Decimal("0.00")),
        final_price=final_decimal,
        is_fully_paid=pending <= Decimal("0.00")
    )


def validate_payment_amount(
    amount: Decimal,
    payment_type: SchemaPaymentType,
    final_price: Decimal
) -> bool:
    """
    Validate payment amount based on payment type and rules.
    
    Args:
        amount: The payment amount.
        payment_type: Type of payment.
        final_price: The final price of the event.
    
    Returns:
        True if valid.
    
    Raises:
        ValueError: If validation fails.
    """
    final_decimal = Decimal(str(final_price))
    amount_decimal = Decimal(str(amount))
    
    if payment_type == SchemaPaymentType.ADVANCE:
        minimum = final_decimal * Decimal(str(ADVANCE_MINIMUM_PERCENT))
        if amount_decimal < minimum:
            raise ValueError(
                f"ADVANCE payment must be at least {ADVANCE_MINIMUM_PERCENT * 100}% "
                f"({minimum} of {final_decimal})"
            )
    
    if payment_type == SchemaPaymentType.TOTAL:
        if amount_decimal != final_decimal:
            raise ValueError(
                f"TOTAL payment must equal the event's final price ({final_decimal}), "
                f"but got {amount_decimal}"
            )
    
    # REMAINING has no minimum, but can't exceed remaining
    return True


def validate_payment_deadline(
    event_start: datetime,
    payment_type: SchemaPaymentType
) -> bool:
    """
    Validate that payment is made before event deadline.
    
    Args:
        event_start: The event start datetime.
        payment_type: Type of payment.
    
    Returns:
        True if valid.
    
    Raises:
        ValueError: If payment is too close to event.
    """
    # Only validate deadline for ADVANCE payments
    if payment_type != SchemaPaymentType.ADVANCE:
        return True
    
    # Check if event is within 24 hours
    deadline = event_start - timedelta(hours=PAYMENT_DEADLINE_HOURS)
    if datetime.now() > deadline:
        raise ValueError(
            f"ADVANCE payments must be made at least "
            f"{PAYMENT_DEADLINE_HOURS} hours before event start"
        )
    
    return True