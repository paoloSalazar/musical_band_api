"""
User Detail API endpoints.

Provides REST endpoints for managing user details.

Endpoints:
    - GET /api/users/{user_id}/details - Get all details for a user
    - GET /api/users/{user_id}/details/{detail_id} - Get a specific user detail
    - POST /api/users/{user_id}/details - Create a new user detail
    - PATCH /api/users/{user_id}/details/{detail_id} - Update a user detail
    - DELETE /api/users/{user_id}/details/{detail_id} - Delete a user detail
"""

import logging
from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from auth.auth import get_current_user as get_auth_current_user
from schemas.user_detail import UserDetailCreate, UserDetailUpdate, UserDetailResponse
import services.user_detail as service
from exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users")


def get_current_user(current_user: Annotated[dict, Depends(get_auth_current_user)]) -> dict:
    """
    Get current user from JWT token.
    
    Args:
        current_user: Current user from JWT token (injected by dependency).
    
    Returns:
        Dictionary containing user information.
    """
    return current_user


@router.get("/{user_id}/details", response_model=List[UserDetailResponse])
def get_all_by_user(
    current_user: Annotated[dict, Depends(get_current_user)], 
    user_id: int
) -> List[UserDetailResponse]:
    """
    Retrieve all details for a specific user.

    Requires authentication.

    Args:
        user_id: The ID of the user.

    Returns:
        List of UserDetailResponse objects.

    Raises:
        HTTPException: 500 if database error occurs.
    """
    try:
        details = service.get_by_user_id(user_id)
        logger.info(f"API request: Retrieved {len(details)} details for user {user_id}")
        return details
    except DatabaseError as e:
        logger.error(f"Database error in get_all_by_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}/details/{detail_id}", response_model=UserDetailResponse)
def get_one(
    current_user: Annotated[dict, Depends(get_current_user)], 
    user_id: int, 
    detail_id: int
) -> UserDetailResponse:
    """
    Retrieve a specific user detail.

    Requires authentication.

    Args:
        user_id: The ID of the user.
        detail_id: The ID of the detail.

    Returns:
        UserDetailResponse object.

    Raises:
        HTTPException: 404 if detail not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        detail = service.get_one(detail_id)
        if detail is None or detail.user_id != user_id:
            logger.warning(f"User detail with id {detail_id} not found")
            raise HTTPException(status_code=404, detail="User detail not found")
        logger.info(f"API request: Retrieved user detail with id {detail_id}")
        return detail
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User detail not found")
    except DatabaseError as e:
        logger.error(f"Database error in get_one: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{user_id}/details", response_model=UserDetailResponse, status_code=201)
def create(
    current_user: Annotated[dict, Depends(get_current_user)], 
    user_id: int, 
    detail: UserDetailCreate
) -> UserDetailResponse:
    """
    Create a new user detail.

    Requires authentication.

    Args:
        user_id: The ID of the user.
        detail: UserDetailCreate schema with detail data.

    Returns:
        Created UserDetailResponse object.

    Raises:
        HTTPException: 500 if database error occurs.
    """
    if detail.user_id != user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    
    try:
        new_detail = service.create(detail)
        logger.info(f"API request: Created user detail for user {user_id}")
        return new_detail
    except DatabaseError as e:
        logger.error(f"Database error in create: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{user_id}/details/{detail_id}", response_model=UserDetailResponse)
def update(
    current_user: Annotated[dict, Depends(get_current_user)], 
    user_id: int, 
    detail_id: int, 
    detail: UserDetailUpdate
) -> UserDetailResponse:
    """
    Update a user detail.

    Requires authentication.

    Args:
        user_id: The ID of the user.
        detail_id: The ID of the detail to update.
        detail: UserDetailUpdate schema with fields to update.

    Returns:
        Updated UserDetailResponse object.

    Raises:
        HTTPException: 404 if detail not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        existing_detail = service.get_one(detail_id)
        if existing_detail is None or existing_detail.user_id != user_id:
            logger.warning(f"User detail with id {detail_id} not found")
            raise HTTPException(status_code=404, detail="User detail not found")
        
        updated_detail = service.update(detail_id, detail)
        logger.info(f"API request: Updated user detail with id {detail_id}")
        return updated_detail
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User detail not found")
    except DatabaseError as e:
        logger.error(f"Database error in update: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{user_id}/details/{detail_id}", status_code=204)
def delete(
    current_user: Annotated[dict, Depends(get_current_user)], 
    user_id: int, 
    detail_id: int
):
    """
    Delete a user detail.

    Requires authentication.

    Args:
        user_id: The ID of the user.
        detail_id: The ID of the detail to delete.

    Returns:
        204 No Content on success.

    Raises:
        HTTPException: 404 if detail not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        existing_detail = service.get_one(detail_id)
        if existing_detail is None or existing_detail.user_id != user_id:
            logger.warning(f"User detail with id {detail_id} not found")
            raise HTTPException(status_code=404, detail="User detail not found")
        
        service.delete(detail_id)
        logger.info(f"API request: Deleted user detail with id {detail_id}")
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User detail not found")
    except DatabaseError as e:
        logger.error(f"Database error in delete: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
