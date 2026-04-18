"""
Event Musician API endpoints.

Provides REST endpoints for event musician assignment management.

Endpoints:
    - GET /api/events/{event_id}/musicians - List musicians for event
    - POST /api/events/{event_id}/musicians - Assign musician to event
    - PATCH /api/events/{event_id}/musicians/{musician_id} - Update musician assignment
    - DELETE /api/events/{event_id}/musicians/{musician_id} - Remove musician from event
    - GET /api/events/{event_id}/musicians/summary - Get musicians summary for event
"""

import logging
from typing import Annotated, List
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends
from auth.auth import get_current_user as get_auth_current_user
from auth.roles import RoleChecker, RoleAndPermissionChecker
from schemas.event_musician import (
    EventMusicianCreate,
    EventMusicianUpdate,
    EventMusicianResponse,
    MusicianSummaryResponse,
    EventMusiciansSummaryResponse,
)
import services.event_musician as service
from exceptions import DatabaseError, NotFoundError, ConflictError, UnauthorizedError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events")

# Authorization dependencies
musician_roles = ["musician", "auxiliar_musician"]
admin_roles = ["admin"]
require_read_event_musician = RoleAndPermissionChecker(
    required_roles=musician_roles + admin_roles,
    required_permissions=["read:event_musician"]
)
require_write_event_musician = RoleAndPermissionChecker(
    required_roles=admin_roles,
    required_permissions=["write:event_musician"]
)
require_delete_event_musician = RoleAndPermissionChecker(
    required_roles=admin_roles,
    required_permissions=["delete:event_musician"]
)


def get_current_user(current_user: Annotated[dict, Depends(get_auth_current_user)]) -> dict:
    """
    Get current user from JWT token.

    Args:
        current_user: Current user from JWT token (injected by dependency).

    Returns:
        Dictionary containing user information.
    """
    return current_user


@router.get("/{event_id}/musicians", response_model=List[EventMusicianResponse])
def get_event_musicians(
    current_user: Annotated[dict, Depends(require_read_event_musician)],
    event_id: int
) -> List[EventMusicianResponse]:
    """
    Retrieve all musicians assigned to a specific event.

    Args:
        event_id: The ID of the event.

    Returns:
        List of EventMusicianResponse objects.

    Raises:
        HTTPException: 403 if unauthorized, 404 if event not found, 500 if database error.
    """
    try:
        musicians = service.get_by_event(event_id, current_user)
        logger.info(f"API request: Retrieved {len(musicians)} musicians for event {event_id}")
        return musicians
    except NotFoundError as e:
        logger.warning(f"Not found error in get_event_musicians: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_event_musicians: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{event_id}/musicians", response_model=EventMusicianResponse, status_code=201)
def assign_musician_to_event(
    current_user: Annotated[dict, Depends(require_write_event_musician)],
    event_id: int,
    musician_data: EventMusicianCreate
) -> EventMusicianResponse:
    """
    Assign a musician to an event.

    Args:
        event_id: The ID of the event.
        musician_data: The musician assignment data.

    Returns:
        Created EventMusicianResponse object.

    Raises:
        HTTPException: 403 if unauthorized, 404 if not found, 409 if conflict, 500 if database error.
    """
    try:
        assignment = service.assign_musician(musician_data, current_user)
        logger.info(f"API request: Assigned musician {assignment.musician_id} to event {event_id}")
        return assignment
    except ValidationError as e:
        logger.warning(f"Validation error in assign_musician_to_event: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        logger.warning(f"Not found error in assign_musician_to_event: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except ConflictError as e:
        logger.warning(f"Conflict error in assign_musician_to_event: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in assign_musician_to_event: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{event_id}/musicians/{musician_id}", response_model=EventMusicianResponse)
def update_event_musician(
    current_user: Annotated[dict, Depends(require_write_event_musician)],
    event_id: int,
    musician_id: int,
    musician_data: EventMusicianUpdate
) -> EventMusicianResponse:
    """
    Update a musician's assignment to an event.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.
        musician_data: The updated assignment data.

    Returns:
        Updated EventMusicianResponse object.

    Raises:
        HTTPException: 403 if unauthorized, 404 if not found, 409 if conflict, 500 if database error.
    """
    try:
        assignment = service.update_assignment_by_event_musician(event_id, musician_id, musician_data, current_user)
        logger.info(f"API request: Updated assignment for musician {musician_id} in event {event_id}")
        return assignment
    except NotFoundError as e:
        logger.warning(f"Not found error in update_event_musician: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except ConflictError as e:
        logger.warning(f"Conflict error in update_event_musician: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in update_event_musician: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{event_id}/musicians/{musician_id}")
def remove_musician_from_event(
    current_user: Annotated[dict, Depends(require_delete_event_musician)],
    event_id: int,
    musician_id: int
) -> dict:
    """
    Remove a musician from an event.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.

    Returns:
        Success message.

    Raises:
        HTTPException: 403 if unauthorized, 404 if not found, 500 if database error.
    """
    try:
        success = service.remove_musician_by_event_musician(event_id, musician_id, current_user)
        if success:
            logger.info(f"API request: Removed musician {musician_id} from event {event_id}")
            return {"message": "Musician removed from event successfully"}
        else:
            raise NotFoundError(f"Musician {musician_id} is not assigned to event {event_id}")
    except NotFoundError as e:
        logger.warning(f"Not found error in remove_musician_from_event: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in remove_musician_from_event: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/musicians/{musician_id}/assignments", response_model=List[EventMusicianResponse])
def get_musician_assignments(
    current_user: Annotated[dict, Depends(require_read_event_musician)],
    musician_id: int
) -> List[EventMusicianResponse]:
    """
    Retrieve all event assignments for a specific musician.

    Args:
        musician_id: The ID of the musician.

    Returns:
        List of EventMusicianResponse objects.

    Raises:
        HTTPException: 403 if unauthorized, 500 if database error.
    """
    try:
        assignments = service.get_by_musician(musician_id, current_user)
        logger.info(f"API request: Retrieved {len(assignments)} assignments for musician {musician_id}")
        return assignments
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_musician_assignments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{event_id}/musicians/summary", response_model=EventMusiciansSummaryResponse)
def get_event_musicians_summary(
    current_user: Annotated[dict, Depends(require_read_event_musician)],
    event_id: int
) -> EventMusiciansSummaryResponse:
    """
    Get summary of musicians assigned to an event.

    Args:
        event_id: The ID of the event.

    Returns:
        Dictionary with summary information.

    Raises:
        HTTPException: 403 if unauthorized, 404 if event not found, 500 if database error.
    """
    try:
        summary = service.get_musicians_summary(event_id, current_user)
        logger.info(f"API request: Retrieved musicians summary for event {event_id}")
        return summary
    except NotFoundError as e:
        logger.warning(f"Not found error in get_event_musicians_summary: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_event_musicians_summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")