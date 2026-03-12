"""
Service layer for User business logic.

Provides business logic operations for user management,
including validation, password handling, and data transformation.

Functions:
    - get_all: Get all users
    - get_one: Get user by email
    - create: Create a new user
    - modify: Update user profile
    - modify_password: Change user password
"""

import logging
from schemas.user import UserResponse, UserCreate, UserUpdate, UserResponseWithRole, UserPaginationResponse
import data.user as data
from models.user import User as DBUser
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError, UnauthorizedError
from auth.auth import get_password_hash, verify_password

logger = logging.getLogger(__name__)


def get_all() -> list[UserResponse]:
    """
    Retrieve all users from the database.

    Returns:
        List of UserResponse objects.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        db_users = data.get_all()
        users = [UserResponse.model_validate(user) for user in db_users]
        logger.info(f"Retrieved {len(users)} users")
        return users
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in get_all")
        raise DatabaseError("Service error")


def get_all_paginated(skip: int = 0, limit: int = 20) -> UserPaginationResponse:
    """
    Retrieve users from the database with pagination.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        UserPaginationResponse with list of UserResponseWithRole objects and metadata.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        db_users, total = data.get_all_paginated(skip=skip, limit=limit)
        users = [
            UserResponseWithRole(
                id=user.id,
                name=user.name,
                lastname=user.lastname,
                second_lastname=user.second_lastname,
                email=user.email,
                role_id=user.role_id,
                role=user.role.name  # Get role name from relationship
            )
            for user in db_users
        ]
        logger.info(f"Retrieved {len(users)} users (total: {total}, skip: {skip}, limit: {limit})")
        return UserPaginationResponse(
            data=users,
            total=total,
            skip=skip,
            limit=limit
        )
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in get_all_paginated")
        raise DatabaseError("Service error")


def get_one(email: str) -> UserResponse:
    """
    Retrieve a user by their email address.

    Args:
        email: The email address of the user.

    Returns:
        UserResponse object.

    Raises:
        NotFoundError: If user with email is not found.
        DatabaseError: If database operation fails.
    """
    try:
        db_user = data.get_one(email)
        if db_user is None:
            logger.warning(f"User with email {email} not found")
            raise NotFoundError(f"User with email {email} not found")
        user = UserResponse.model_validate(db_user)
        logger.info(f"Retrieved user with email {email}")
        return user
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in get_one")
        raise DatabaseError("Service error")


def get_one_by_id(user_id: int) -> UserResponseWithRole:
    """
    Retrieve a user by their ID.

    Args:
        user_id: The ID of the user.

    Returns:
        UserResponseWithRole object with role_name.

    Raises:
        NotFoundError: If user with ID is not found.
        DatabaseError: If database operation fails.
    """
    try:
        db_user = data.get_one_by_id(user_id)
        if db_user is None:
            logger.warning(f"User with id {user_id} not found")
            raise NotFoundError(f"User with id {user_id} not found")
        user = UserResponseWithRole(
            id=db_user.id,
            name=db_user.name,
            lastname=db_user.lastname,
            second_lastname=db_user.second_lastname,
            email=db_user.email,
            role_id=db_user.role_id,
            role=db_user.role.name  # Get role name from relationship
        )
        logger.info(f"Retrieved user with id {user_id}")
        return user
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in get_one_by_id")
        raise DatabaseError("Service error")


def create(user_create: UserCreate) -> UserResponse:
    """
    Create a new user in the database.

    Args:
        user_create: UserCreate schema with user data.

    Returns:
        Created UserResponse object.

    Raises:
        ConflictError: If user with email already exists.
        DatabaseError: If database operation fails.
    """
    try:
        existing_user = data.get_one(user_create.email)
        if existing_user is not None:
            logger.warning(f"User with email {user_create.email} already exists")
            raise ConflictError(f"User with email {user_create.email} already exists")

        db_user = DBUser(
            name=user_create.name,
            lastname=user_create.lastname,
            second_lastname=user_create.second_lastname,
            email=user_create.email,
            password=get_password_hash(user_create.password),
            role_id=user_create.role_id
        )
        created_db_user = data.create(db_user)
        user = UserResponse.model_validate(created_db_user)
        logger.info(f"Created user with email {user_create.email}")
        return user
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in create")
        raise DatabaseError("Service error")


def modify(user_update: UserUpdate) -> UserResponse:
    """
    Update an existing user's profile.

    Args:
        user_update: UserUpdate schema with fields to update.

    Returns:
        Updated UserResponse object.

    Raises:
        NotFoundError: If user to update is not found.
        DatabaseError: If database operation fails.
    """
    try:
        existing_user = data.get_one(user_update.email)
        if existing_user is None:
            logger.warning(f"User with email {user_update.email} not found")
            raise NotFoundError(f"User with email {user_update.email} not found")

        db_user = DBUser(
            id=existing_user.id,
            name=user_update.name if user_update.name else existing_user.name,
            lastname=user_update.lastname if user_update.lastname else existing_user.lastname,
            second_lastname=user_update.second_lastname if user_update.second_lastname else existing_user.second_lastname,
            email=user_update.email if user_update.email else existing_user.email,
            password=existing_user.password,  # Keep existing password
            role_id=user_update.role_id if user_update.role_id else existing_user.role_id
        )
        modified_db_user = data.modify(db_user)
        if modified_db_user:
            logger.info(f"Modified user with email {user_update.email}")
            return UserResponse.model_validate(modified_db_user)
        else:
            logger.warning(f"User with email {user_update.email} not found during modification")
            raise NotFoundError(f"User with email {user_update.email} not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in modify")
        raise DatabaseError("Service error")


def modify_password(email: str, current_password: str, new_password: str) -> bool:
    """
    Change a user's password.

    Args:
        email: User's email address.
        current_password: Current password for verification.
        new_password: New password to set.

    Returns:
        True if password was changed successfully.

    Raises:
        NotFoundError: If user is not found.
        UnauthorizedError: If current password is incorrect.
        DatabaseError: If database operation fails.
    """
    try:
        existing_user = data.get_one(email)
        if existing_user is None:
            logger.warning(f"User with email {email} not found")
            raise NotFoundError(f"User with email {email} not found")

        # Verify current password
        if not verify_password(current_password, existing_user.password):
            logger.warning(f"Invalid current password for user {email}")
            raise UnauthorizedError("Current password is incorrect")

        # Update password
        db_user = DBUser(
            id=existing_user.id,
            name=existing_user.name,
            lastname=existing_user.lastname,
            second_lastname=existing_user.second_lastname,
            email=existing_user.email,
            password=get_password_hash(new_password),
            role_id=existing_user.role_id
        )
        modified_db_user = data.modify(db_user)
        if modified_db_user:
            logger.info(f"Modified password for user {email}")
            return True
        else:
            logger.warning(f"User with email {email} not found during password modification")
            raise NotFoundError(f"User with email {email} not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in modify_password")
        raise DatabaseError("Service error")
