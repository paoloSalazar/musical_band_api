"""
Service layer for UserDetail entities.

Provides business logic operations for user details.

Functions:
    - get_one: Get user detail by ID
    - get_by_user_id: Get all details for a user
    - get_all: Get all user details
    - create: Create a new user detail
    - update: Update an existing user detail
    - delete: Delete a user detail
    - delete_by_user_id: Delete all details for a user
"""

import logging
from typing import List
import data.user_detail as data
from schemas.user_detail import UserDetailCreate, UserDetailUpdate, UserDetailResponse
from exceptions import DatabaseError

logger = logging.getLogger(__name__)


def get_one(detail_id: int) -> UserDetailResponse | None:
    """
    Retrieve a user detail by its ID.

    Args:
        detail_id: The unique identifier of the user detail.

    Returns:
        UserDetailResponse if found, None otherwise.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        detail = data.get_one(detail_id)
        if detail is None:
            return None
        return UserDetailResponse.model_validate(detail)
    except DatabaseError as e:
        logger.error(f"Database error in get_one: {str(e)}")
        raise


def get_by_user_id(user_id: int) -> List[UserDetailResponse]:
    """
    Retrieve all details for a specific user.

    Args:
        user_id: The ID of the user.

    Returns:
        List of UserDetailResponse objects.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        details = data.get_by_user_id(user_id)
        return [UserDetailResponse.model_validate(detail) for detail in details]
    except DatabaseError as e:
        logger.error(f"Database error in get_by_user_id: {str(e)}")
        raise


def get_all() -> List[UserDetailResponse]:
    """
    Retrieve all user details.

    Returns:
        List of UserDetailResponse objects.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        details = data.get_all()
        return [UserDetailResponse.model_validate(detail) for detail in details]
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise


def create(detail_data: UserDetailCreate) -> UserDetailResponse:
    """
    Create a new user detail.

    Args:
        detail_data: UserDetailCreate schema with user detail data.

    Returns:
        Created UserDetailResponse object.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        detail_dict = detail_data.model_dump()
        new_detail = data.create(detail_dict)
        return UserDetailResponse.model_validate(new_detail)
    except DatabaseError as e:
        logger.error(f"Database error in create: {str(e)}")
        raise


def update(detail_id: int, detail_data: UserDetailUpdate) -> UserDetailResponse | None:
    """
    Update an existing user detail.

    Args:
        detail_id: The ID of the user detail to update.
        detail_data: UserDetailUpdate schema with fields to update.

    Returns:
        Updated UserDetailResponse object if found, None otherwise.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        detail_dict = detail_data.model_dump(exclude_unset=True)
        updated_detail = data.update(detail_id, detail_dict)
        if updated_detail is None:
            return None
        return UserDetailResponse.model_validate(updated_detail)
    except DatabaseError as e:
        logger.error(f"Database error in update: {str(e)}")
        raise


def delete(detail_id: int) -> bool:
    """
    Delete a user detail.

    Args:
        detail_id: The ID of the user detail to delete.

    Returns:
        True if deleted, False if not found.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        return data.delete(detail_id)
    except DatabaseError as e:
        logger.error(f"Database error in delete: {str(e)}")
        raise


def delete_by_user_id(user_id: int) -> bool:
    """
    Delete all details for a specific user.

    Args:
        user_id: The ID of the user whose details to delete.

    Returns:
        True if any were deleted, False if none existed.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        return data.delete_by_user_id(user_id)
    except DatabaseError as e:
        logger.error(f"Database error in delete_by_user_id: {str(e)}")
        raise
