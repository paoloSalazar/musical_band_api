"""
Musician Availability API endpoints.

Provides REST endpoints for musician availability management.

Endpoints:
    - GET /api/musician-availability/{musician_id} - Get availability for musician
    - GET /api/musician-availability/check/{musician_id}/{date} - Check availability
    - POST /api/musician-availability - Create availability entry
    - POST /api/musician-availability/bulk - Create bulk availability
    - PATCH /api/musician-availability/{availability_id} - Update availability
    - DELETE /api/musician-availability/{availability_id} - Delete availability
    - DELETE /api/musician-availability/{musician_id}/{date} - Delete by musician/date

Admin endpoints:
    - GET /api/admin/musician-availability/date/{date} - Get all unavailable musicians on date
"""

import logging
from typing import Annotated, List
from datetime import date
from fastapi import APIRouter, HTTPException, Depends
from auth.auth import get_current_user as get_auth_current_user
from auth.roles import RoleChecker
from schemas.musician_availability import (
    MusicianAvailabilityCreate,
    MusicianAvailabilityUpdate,
    MusicianAvailabilityResponse,
    MusicianAvailabilitySummaryResponse
)
import services.musician_availability as service
from exceptions import DatabaseError, NotFoundError, ConflictError, UnauthorizedError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/musician-availability")
admin_router = APIRouter(prefix="/api/admin/musician-availability")

# Authorization dependencies
require_admin = RoleChecker(allowed_roles=["admin"])


def get_current_user(current_user: Annotated[dict, Depends(get_auth_current_user)]) -> dict:
    """
    Get current user from JWT token.

    Args:
        current_user: Current user from JWT token (injected by dependency).

    Returns:
        Dictionary containing user information.
    """
    return current_user


@router.get("/{musician_id}", response_model=List[MusicianAvailabilityResponse])
def get_by_musician(
    current_user: Annotated[dict, Depends(get_current_user)],
    musician_id: int
) -> List[MusicianAvailabilityResponse]:
    """
    Retrieve all availability entries for a specific musician.

    Args:
        musician_id: The ID of the musician.

    Returns:
        List of MusicianAvailabilityResponse objects.

    Raises:
        HTTPException: 403 if unauthorized, 500 if database error.
    """
    try:
        availabilities = service.get_by_musician(musician_id, current_user)
        logger.info(f"API request: Retrieved {len(availabilities)} availability entries for musician {musician_id}")
        return availabilities
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_by_musician: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/check/{musician_id}/{check_date}", response_model=bool)
def check_availability(
    current_user: Annotated[dict, Depends(get_current_user)],
    musician_id: int,
    check_date: date
) -> bool:
    """
    Check if a musician is available on a specific date.

    Args:
        musician_id: The ID of the musician.
        check_date: The date to check.

    Returns:
        True if available, False if unavailable.

    Raises:
        HTTPException: 500 if database error.
    """
    try:
        is_available = service.check_availability(musician_id, check_date, current_user)
        logger.info(f"API request: Musician {musician_id} availability check for {check_date}: {is_available}")
        return is_available
    except DatabaseError as e:
        logger.error(f"Database error in check_availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("", response_model=MusicianAvailabilityResponse, status_code=201)
def create_availability(
    current_user: Annotated[dict, Depends(get_current_user)],
    availability_data: MusicianAvailabilityCreate
) -> MusicianAvailabilityResponse:
    """
    Create a new availability entry for a musician.

    Args:
        availability_data: The availability data to create.

    Returns:
        Created MusicianAvailabilityResponse object.

    Raises:
        HTTPException: 403 if unauthorized, 409 if conflict, 500 if database error.
    """
    try:
        availability = service.create(availability_data, current_user)
        logger.info(f"API request: Created availability for musician {availability.musician_id} on {availability.unavailable_date}")
        return availability
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except ConflictError as e:
        logger.warning(f"Conflict error in create_availability: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error in create_availability: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in create_availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/bulk", response_model=List[MusicianAvailabilityResponse], status_code=201)
def create_bulk_availability(
    current_user: Annotated[dict, Depends(get_current_user)],
    availabilities_data: List[MusicianAvailabilityCreate]
) -> List[MusicianAvailabilityResponse]:
    """
    Create multiple availability entries for a musician.

    Args:
        availabilities_data: List of availability data to create.

    Returns:
        List of created MusicianAvailabilityResponse objects.

    Raises:
        HTTPException: 403 if unauthorized, 409 if conflict, 400 if validation error, 500 if database error.
    """
    try:
        availabilities = service.create_bulk(availabilities_data, current_user)
        total_created = len(availabilities)
        logger.info(f"API request: Created {total_created} bulk availability entries")
        return availabilities
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except ConflictError as e:
        logger.warning(f"Conflict error in create_bulk_availability: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error in create_bulk_availability: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in create_bulk_availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{availability_id}", response_model=MusicianAvailabilityResponse)
def update_availability(
    current_user: Annotated[dict, Depends(get_current_user)],
    availability_id: int,
    availability_data: MusicianAvailabilityUpdate
) -> MusicianAvailabilityResponse:
    """
    Update an existing availability entry.

    Args:
        availability_id: The ID of the availability entry to update.
        availability_data: The updated availability data.

    Returns:
        Updated MusicianAvailabilityResponse object.

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 409 if conflict, 500 if database error.
    """
    try:
        availability = service.update(availability_id, availability_data, current_user)
        logger.info(f"API request: Updated availability {availability_id}")
        return availability
    except NotFoundError as e:
        logger.warning(f"Not found error in update_availability: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except ConflictError as e:
        logger.warning(f"Conflict error in update_availability: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in update_availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{availability_id}")
def delete_availability(
    current_user: Annotated[dict, Depends(get_current_user)],
    availability_id: int
) -> dict:
    """
    Delete an availability entry.

    Args:
        availability_id: The ID of the availability entry to delete.

    Returns:
        Success message.

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 500 if database error.
    """
    try:
        success = service.delete(availability_id, current_user)
        if success:
            logger.info(f"API request: Deleted availability {availability_id}")
            return {"message": "Availability deleted successfully"}
        else:
            raise NotFoundError(f"Availability entry with id {availability_id} not found")
    except NotFoundError as e:
        logger.warning(f"Not found error in delete_availability: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in delete_availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{musician_id}/{delete_date}")
def delete_by_musician_and_date(
    current_user: Annotated[dict, Depends(get_current_user)],
    musician_id: int,
    delete_date: date
) -> dict:
    """
    Delete a specific availability entry by musician and date.

    Args:
        musician_id: The ID of the musician.
        delete_date: The date of the availability entry.

    Returns:
        Success message.

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 500 if database error.
    """
    try:
        success = service.delete_by_musician_and_date(musician_id, delete_date, current_user)
        if success:
            logger.info(f"API request: Deleted availability for musician {musician_id} on {delete_date}")
            return {"message": "Availability deleted successfully"}
        else:
            raise NotFoundError(f"Availability not found for musician {musician_id} on {delete_date}")
    except NotFoundError as e:
        logger.warning(f"Not found error in delete_by_musician_and_date: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in delete_by_musician_and_date: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Admin endpoints
@admin_router.get("/date/{check_date}", response_model=List[MusicianAvailabilityResponse])
def get_all_by_date(
    current_user: Annotated[dict, Depends(require_admin)],
    check_date: date
) -> List[MusicianAvailabilityResponse]:
    """
    Get all musicians unavailable on a specific date (Admin only).

    Args:
        check_date: The date to check.

    Returns:
        List of MusicianAvailabilityResponse objects for all unavailable musicians.

    Raises:
        HTTPException: 500 if database error.
    """
    try:
        availabilities = service.get_all_by_date(check_date, current_user)
        logger.info(f"Admin API request: Retrieved {len(availabilities)} unavailable musicians for date {check_date}")
        return availabilities
    except DatabaseError as e:
        logger.error(f"Database error in get_all_by_date: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")