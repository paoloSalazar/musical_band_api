"""
User API endpoints.

Provides REST endpoints for user management including authentication,
profile management, and user CRUD operations.

Endpoints:
    - GET /api/users/ - List all users
    - GET /api/users/{email} - Get user by email
    - POST /api/users/ - Create new user
    - PATCH /api/users/ - Update user profile
    - PATCH /api/users/{email}/password - Change password
    - POST /api/users/login - User login
"""

import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Request
from schemas.user_role import UserRole
from schemas.auth import Token
from schemas.user import UserResponse, UserCreate, UserLogin, UserUpdate, UserPasswordUpdate
import services.user as service
import services.auth as auth_service
from auth.auth import decode_access_token
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError, UnauthorizedError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users")


async def get_current_user(request: Request) -> dict:
    """
    Verify JWT token and return current user information.

    This is a FastAPI dependency that extracts the Bearer token
    from the Authorization header and decodes it.

    Args:
        request: The incoming HTTP request.

    Returns:
        Dictionary containing user information from JWT payload.

    Raises:
        HTTPException: 401 if token is missing or invalid.
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
def get_all(current_user: Annotated[dict, Depends(get_current_user)]) -> list[UserResponse]:
    """
    Retrieve all users from the database.

    Requires authentication.

    Returns:
        List of UserResponse objects.

    Raises:
        HTTPException: 500 if database error occurs.
    """
    try:
        users = service.get_all()
        logger.info(f"API request: Retrieved {len(users)} users by {current_user.get('sub')}")
        return users
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{email}")
def get_one(current_user: Annotated[dict, Depends(get_current_user)], email: str) -> UserResponse:
    """
    Retrieve a user by their email address.

    Requires authentication.

    Args:
        email: The email address of the user.

    Returns:
        UserResponse object.

    Raises:
        HTTPException: 404 if user not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        user = service.get_one(email)
        logger.info(f"API request: Retrieved user with email {email}")
        return user
    except NotFoundError:
        logger.warning(f"User with email {email} not found")
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError as e:
        logger.error(f"Database error in get_one: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/")
def create(user: UserCreate) -> UserResponse:
    """
    Create a new user account.

    Args:
        user: UserCreate schema with user data.

    Returns:
        Created UserResponse object.

    Raises:
        HTTPException: 409 if email already exists.
        HTTPException: 500 if database error occurs.
    """
    try:
        new_user = service.create(user)
        logger.info(f"API request: Created user with email {user.email}")
        return new_user
    except ConflictError:
        logger.warning(f"User with email {user.email} already exists")
        raise HTTPException(status_code=409, detail="User already exists")
    except DatabaseError as e:
        logger.error(f"Database error in create: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/")
def modify(current_user: Annotated[dict, Depends(get_current_user)], user_update: UserUpdate) -> UserResponse:
    """
    Update an existing user's profile.

    Requires authentication.

    Args:
        user_update: UserUpdate schema with fields to update.

    Returns:
        Updated UserResponse object.

    Raises:
        HTTPException: 404 if user not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        updated_user = service.modify(user_update)
        logger.info(f"API request: Modified user with email {user_update.email} by {current_user.get('sub')}")
        return updated_user
    except NotFoundError:
        logger.warning(f"User with email {user_update.email} not found for modification")
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError as e:
        logger.error(f"Database error in modify: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{email}/password")
def modify_password(current_user: Annotated[dict, Depends(get_current_user)], email: str, password_update: UserPasswordUpdate) -> dict:
    """
    Change a user's password.

    Requires authentication. Verifies current password before setting new one.

    Args:
        email: The email of the user.
        password_update: Current and new password.

    Returns:
        Success message.

    Raises:
        HTTPException: 404 if user not found.
        HTTPException: 401 if current password is incorrect.
        HTTPException: 500 if database error occurs.
    """
    try:
        success = service.modify_password(email, password_update.current_password, password_update.new_password)
        if success:
            logger.info(f"API request: Modified password for user {email} by {current_user.get('sub')}")
            return {"message": "Password updated successfully"}
    except NotFoundError:
        logger.warning(f"User with email {email} not found for password modification")
        raise HTTPException(status_code=404, detail="User not found")
    except UnauthorizedError:
        logger.warning(f"Invalid current password for user {email}")
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    except DatabaseError as e:
        logger.error(f"Database error in modify_password: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=Token)
def login(login_data: UserLogin) -> Token:
    """
    Authenticate a user and return a JWT access token.

    Args:
        login_data: UserLogin schema with email and password.

    Returns:
        Token response with access token.

    Raises:
        HTTPException: 401 if credentials are invalid.
        HTTPException: 500 if server error occurs.
    """
    try:
        token = auth_service.authenticate_user(login_data)
        logger.info(f"API request: User {login_data.email} logged in successfully")
        return token
    except NotFoundError:
        logger.warning(f"Login failed: User with email {login_data.email} not found")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except UnauthorizedError:
        logger.warning(f"Login failed: Invalid password for user {login_data.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
