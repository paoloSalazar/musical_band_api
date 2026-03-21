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
from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from auth.auth import decode_access_token
from auth.roles import RoleAndPermissionChecker
from schemas.event import EventCreate, EventResponse, EventUpdate, EventStatusEnum, PaginatedEventResponse
import services.event as event_service
from exceptions import NotFoundError, DatabaseError, ConflictError

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
def get_all(
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page (max: 100)"),
    status: Optional[str] = Query(None, description="Filter by status: PENDING, CONFIRMED, CANCELLED, COMPLETED"),
    search: Optional[str] = Query(None, description="Search in name and place fields"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_after: Optional[datetime] = Query(None, description="Filter events starting after this datetime"),
    end_before: Optional[datetime] = Query(None, description="Filter events ending before this datetime"),
    sort_by: str = Query("created_at", description="Sort by: name, start_datetime, created_at"),
    order: str = Query("desc", description="Sort order: asc, desc")
) -> PaginatedEventResponse:
    """
    Retrieve paginated and filtered events (table view).

    Requires authentication. All authenticated users can view events.

    Query Parameters:
        - page: Page number (default: 1)
        - limit: Items per page (default: 20, max: 100)
        - status: Filter by event status
        - search: Search in name and place
        - user_id: Filter by creator
        - start_after: Filter events starting after this datetime
        - end_before: Filter events ending before this datetime
        - sort_by: Sort by field (name, start_datetime, created_at)
        - order: Sort order (asc, desc)

    Returns:
        PaginatedEventResponse with items, total, page, limit, total_pages.
    """
    try:
        result = event_service.get_paginated(
            page=page,
            limit=limit,
            status=status,
            search=search,
            user_id=user_id,
            start_after=start_after,
            end_before=end_before,
            sort_by=sort_by,
            order=order
        )
        logger.info(f"API request: Retrieved page {page} ({len(result.items)} items) by {current_user.get('sub')}")
        return result
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/calendar")
def get_calendar(
    current_user: Annotated[dict, Depends(get_current_user)],
    year: int = Query(..., ge=2000, le=2100, description="Year (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    user_id: Optional[int] = Query(None, description="Filter by user ID")
) -> list[EventResponse]:
    """
    Retrieve events for a specific month (calendar view).

    Requires authentication. All authenticated users can view events.

    Query Parameters:
        - year: Year (required)
        - month: Month (1-12, required)
        - user_id: Filter by creator (optional)

    Returns:
        List of EventResponse objects for the specified month.
    """
    try:
        events = event_service.get_by_month(year, month, user_id)
        logger.info(f"API request: Retrieved {len(events)} events for {year}-{month:02d} by {current_user.get('sub')}")
        return events
    except DatabaseError as e:
        logger.error(f"Database error in get_calendar: {str(e)}")
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
    except ConflictError as e:
        logger.warning(f"Conflict error in create: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
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
    except ConflictError as e:
        logger.warning(f"Conflict error in modify: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
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
