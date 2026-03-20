"""
Event API endpoints.

Provides REST endpoints for event management.

Endpoints:
    - GET /api/events - List all events
    - GET /api/events/{event_id} - Get event by ID
    - POST /api/events - Create new event
    - PATCH /api/events/{event_id} - Update event
    - DELETE /api/events/{event_id} - Delete event
    - PATCH /api/events/{event_id}/status - Change event status
"""

import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Request
from auth.auth import decode_access_token
from auth.roles import RoleAndPermissionChecker
from schemas.event import EventCreate, EventResponse, EventUpdate, EventStatusEnum
import services.event as event_service
from exceptions import NotFoundError, DatabaseError

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


@router.get("/")
def get_all(current_user: Annotated[dict, Depends(get_current_user)]) -> list[EventResponse]:
    """
    Retrieve all events.

    Requires authentication. All authenticated users can view all events.

    Returns:
        List of EventResponse objects.
    """
    try:
        events = event_service.get_all()
        logger.info(f"API request: Retrieved {len(events)} events by {current_user.get('sub')}")
        return events
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{event_id}")
def get_one(current_user: Annotated[dict, Depends(get_current_user)], event_id: int) -> EventResponse:
    """
    Retrieve an event by its ID.

    Requires authentication.

    Args:
        event_id: The ID of the event.

    Returns:
        EventResponse object.
    """
    try:
        event = event_service.get_one(event_id)
        logger.info(f"API request: Retrieved event {event_id} by {current_user.get('sub')}")
        return event
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Event not found")
    except DatabaseError as e:
        logger.error(f"Database error in get_one: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", dependencies=[Depends(RoleAndPermissionChecker(required_roles=["client"], required_permissions=["write:events"]))])
def create(current_user: Annotated[dict, Depends(get_current_user)], event: EventCreate) -> EventResponse:
    """
    Create a new event.

    Requires client role AND write:events permission.

    Args:
        event: EventCreate schema with event data.

    Returns:
        Created EventResponse object.
    """
    try:
        # Set user_id from the authenticated user
        event_data = EventCreate(
            name=event.name,
            place=event.place,
            description=event.description,
            start_datetime=event.start_datetime,
            end_datetime=event.end_datetime,
            is_all_day=event.is_all_day,
            user_id=current_user.get("user_id", 1)  # Default to 1 if not in token
        )
        
        created_event = event_service.create(event_data)
        logger.info(f"API request: Created event {created_event.id} by {current_user.get('sub')}")
        return created_event
    except DatabaseError as e:
        logger.error(f"Database error in create: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{event_id}", dependencies=[Depends(RoleAndPermissionChecker(required_roles=["client"], required_permissions=["write:events"]))])
def modify(
    current_user: Annotated[dict, Depends(get_current_user)],
    event_id: int,
    event_update: EventUpdate
) -> EventResponse:
    """
    Update an existing event.

    Requires client role AND write:events permission.

    Args:
        event_id: The ID of the event to update.
        event_update: EventUpdate schema with fields to update.

    Returns:
        Updated EventResponse object.
    """
    try:
        # Check if user owns the event or is admin
        event = event_service.get_one(event_id)
        
        # Get user's role from token
        user_role = current_user.get("role")
        
        # Only allow owner or admin to modify
        if user_role != "admin" and event.user_id != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Not authorized to modify this event")
        
        updated_event = event_service.modify(event_id, event_update)
        logger.info(f"API request: Modified event {event_id} by {current_user.get('sub')}")
        return updated_event
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Event not found")
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error in modify: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{event_id}", dependencies=[Depends(RoleAndPermissionChecker(required_roles=["client"], required_permissions=["delete:events"]))])
def delete(current_user: Annotated[dict, Depends(get_current_user)], event_id: int) -> dict:
    """
    Delete an event.

    Requires client role AND delete:events permission.

    Args:
        event_id: The ID of the event to delete.

    Returns:
        Success message.
    """
    try:
        # Check if user owns the event or is admin
        event = event_service.get_one(event_id)
        
        # Get user's role from token
        user_role = current_user.get("role")
        
        # Only allow owner or admin to delete
        if user_role != "admin" and event.user_id != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Not authorized to delete this event")
        
        event_service.delete(event_id)
        logger.info(f"API request: Deleted event {event_id} by {current_user.get('sub')}")
        return {"message": "Event deleted successfully"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Event not found")
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error in delete: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{event_id}/status", dependencies=[Depends(RoleAndPermissionChecker(required_roles=["admin"], required_permissions=["manage:events"]))])
def change_status(
    current_user: Annotated[dict, Depends(get_current_user)],
    event_id: int,
    status_update: dict
) -> EventResponse:
    """
    Change an event's status.

    Requires admin role AND manage:events permission.

    Args:
        event_id: The ID of the event.
        status_update: Dictionary with 'status' key.

    Returns:
        Updated EventResponse object.
    """
    try:
        new_status = EventStatusEnum(status_update.get("status"))
        updated_event = event_service.change_status(event_id, new_status)
        logger.info(f"API request: Changed status of event {event_id} to {new_status} by {current_user.get('sub')}")
        return updated_event
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Event not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status value")
    except DatabaseError as e:
        logger.error(f"Database error in change_status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
