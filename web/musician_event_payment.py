"""
Musician Event Payment API endpoints.

Provides REST endpoints for musician event payment management.

Endpoints:
    - POST /api/events/{event_id}/musicians/{musician_id}/payments - Add payment
    - GET /api/events/{event_id}/musicians/{musician_id}/payments - List payments
    - GET /api/events/{event_id}/musicians/{musician_id}/payments/summary - Payment summary
"""

import logging
from typing import Annotated, List
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends
from auth.auth import get_current_user as get_auth_current_user
from auth.roles import RoleChecker, RoleAndPermissionChecker
from schemas.musician_event_payment import (
    MusicianEventPaymentCreate,
    MusicianEventPaymentResponse,
    MusicianPaymentSummaryResponse,
)
import services.musician_event_payment as service
from exceptions import DatabaseError, NotFoundError, ValidationError, UnauthorizedError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events")

# Authorization dependencies
musician_roles = ["musician", "auxiliar_musician", "helper"]
admin_roles = ["admin"]
require_read_musician_event_payment = RoleAndPermissionChecker(
    required_roles=musician_roles + admin_roles,
    required_permissions=["read:musician_event_payment"]
)
require_write_musician_event_payment = RoleAndPermissionChecker(
    required_roles=admin_roles,
    required_permissions=["write:musician_event_payment"]
)
require_user_or_admin = RoleChecker(allowed_roles=["user", "admin"])


def get_current_user(current_user: Annotated[dict, Depends(get_auth_current_user)]) -> dict:
    """
    Get current user from JWT token.

    Args:
        current_user: Current user from JWT token (injected by dependency).

    Returns:
        Dictionary containing user information.
    """
    return current_user


@router.post(
    "/{event_id}/musicians/{musician_id}/payments",
    response_model=MusicianEventPaymentResponse,
    dependencies=[Depends(require_write_musician_event_payment)],
    summary="Add payment to musician for event",
    description="Create a new payment record for a musician assigned to an event."
)
def create_musician_payment(
    event_id: int,
    musician_id: int,
    payment: MusicianEventPaymentCreate,
    current_user: Annotated[dict, Depends(get_current_user)]
) -> MusicianEventPaymentResponse:
    """
    Create a new payment for a musician assigned to an event.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.
        payment: Payment data to create.
        current_user: Current authenticated user.

    Returns:
        Created payment information.

    Raises:
        HTTPException: For validation, authorization, or not found errors.
    """
    try:
        return service.create_musician_payment(payment, current_user)
    except ValidationError as e:
        logger.warning(f"Validation error creating payment for event {event_id}, musician {musician_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        logger.warning(f"Not found error creating payment for event {event_id}, musician {musician_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized error creating payment for event {event_id}, musician {musician_id}: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error creating payment for event {event_id}, musician {musician_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{event_id}/musicians/{musician_id}/payments",
    response_model=List[MusicianEventPaymentResponse],
    dependencies=[Depends(require_read_musician_event_payment)],
    summary="List payments for musician in event",
    description="Retrieve all payment records for a specific musician in an event."
)
def get_musician_payments(
    event_id: int,
    musician_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
) -> List[MusicianEventPaymentResponse]:
    """
    Get all payments for a musician in a specific event.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.
        current_user: Current authenticated user.

    Returns:
        List of payment records.

    Raises:
        HTTPException: For authorization or not found errors.
    """
    try:
        return service.get_payments_for_event(event_id, musician_id, current_user)
    except NotFoundError as e:
        logger.warning(f"Not found error getting payments for event {event_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized error getting payments for event {event_id}: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error getting payments for event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{event_id}/musicians/{musician_id}/payments/summary",
    response_model=MusicianPaymentSummaryResponse,
    dependencies=[Depends(require_read_musician_event_payment)],
    summary="Get payment summary for musician in event",
    description="Retrieve payment summary (total paid, count) for a specific musician in an event."
)
def get_musician_payment_summary(
    event_id: int,
    musician_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
) -> MusicianPaymentSummaryResponse:
    """
    Get payment summary for a musician in a specific event.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.
        current_user: Current authenticated user.

    Returns:
        Payment summary information.

    Raises:
        HTTPException: For authorization or not found errors.
    """
    try:
        return service.get_payment_summary_for_musician_event(event_id, musician_id, current_user)
    except NotFoundError as e:
        logger.warning(f"Not found error getting payment summary for event {event_id}, musician {musician_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized error getting payment summary for event {event_id}, musician {musician_id}: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error getting payment summary for event {event_id}, musician {musician_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")