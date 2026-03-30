"""
Event Payment API endpoints.

Provides REST endpoints for event payment management.

Endpoints:
    - POST /api/events/{event_id}/payments - Add payment
    - GET /api/events/{event_id}/payments - List payments
    - GET /api/events/{event_id}/payments/summary - Payment summary
"""

import logging
from typing import Annotated
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from auth.auth import decode_access_token
from schemas.event_payment import (
    EventPaymentCreate,
    EventPaymentResponse,
    EventPaymentSummary,
    PaymentType as SchemaPaymentType
)
import services.event_payment as payment_service
import services.event as event_service
import data.event_payment as payment_data
from exceptions import NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events")


async def get_current_user(request: Request) -> dict:
    """
    Verify JWT token and return current user information.
    """
    authorization = request.headers.get("Authorization")
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


@router.post("/{event_id}/payments", response_model=EventPaymentResponse, status_code=201)
def add_payment(
    current_user: Annotated[dict, Depends(get_current_user)],
    event_id: int,
    payment_data: EventPaymentCreate
) -> EventPaymentResponse:
    """
    Add a new payment for an event.

    Requires authentication.

    Args:
        current_user: Current user from JWT token.
        event_id: ID of the event to add payment for.
        payment_data: Payment details.

    Returns:
        EventPaymentResponse with created payment data.

    Raises:
        HTTPException 401: Unauthorized
        HTTPException 403: Forbidden
        HTTPException 404: Event not found
        HTTPException 409: Validation error
    """
    try:
        # Convert schema PaymentType to service PaymentType
        payment_type = SchemaPaymentType(payment_data.payment_type.value)
        
        result = payment_service.create_payment(
            event_id=event_id,
            user_id=payment_data.user_id,
            amount=payment_data.amount,
            payment_type=payment_type,
            notes=payment_data.notes
        )
        
        logger.info(f"Payment created successfully for event {event_id}: {result}")
        return result
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/{event_id}/payments", response_model=list[EventPaymentResponse])
def list_payments(
    current_user: Annotated[dict, Depends(get_current_user)],
    event_id: int,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page (max: 100)")
) -> list[EventPaymentResponse]:
    """
    List all payments for an event.

    Requires authentication.

    Args:
        current_user: Current user from JWT token.
        event_id: ID of the event.
        page: Page number (1-indexed).
        limit: Items per page.

    Returns:
        List of EventPaymentResponse objects.

    Raises:
        HTTPException 401: Unauthorized
        HTTPException 404: Event not found
    """
    try:
        # Validate event exists
        event = event_service.get_one(event_id)
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        # Get payments
        payments = payment_data.get_payments_by_event(event_id)
        
        # Convert to response schema
        result = []
        for p in payments:
            result.append(EventPaymentResponse(
                id=p.id,
                event_id=p.event_id,
                user_id=p.user_id,
                amount=p.amount,
                payment_type=SchemaPaymentType(p.payment_type) if isinstance(p.payment_type, str) else SchemaPaymentType(p.payment_type.value),
                payment_date=p.payment_date,
                notes=p.notes,
                created_at=p.created_at
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing payments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{event_id}/payments/summary", response_model=EventPaymentSummary)
def get_payment_summary(
    current_user: Annotated[dict, Depends(get_current_user)],
    event_id: int
) -> EventPaymentSummary:
    """
    Get payment summary for an event.

    Requires authentication.

    Args:
        current_user: Current user from JWT token.
        event_id: ID of the event.

    Returns:
        EventPaymentSummary with total paid, pending balance, final price, and fully paid status.

    Raises:
        HTTPException 401: Unauthorized
        HTTPException 404: Event not found
    """
    try:
        # Get event to validate it exists and get final price
        event = event_service.get_one(event_id)
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        
        if event.price is None:
            raise HTTPException(status_code=400, detail="Event final price not set")
        
        summary = payment_service.get_event_payment_summary(
            event_id=event_id,
            final_price=Decimal(str(event.price))
        )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")