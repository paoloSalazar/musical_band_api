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
from auth.auth import decode_access_token
from auth.auth import get_current_user as get_auth_current_user
from auth.roles import RoleAndPermissionChecker
from schemas.user_role import UserRole
from schemas.auth import Token
from schemas.user import UserResponse, UserCreate, UserLogin, UserUpdate, UserPasswordUpdate, UserPaginationResponse, UserResponseWithRole
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


@router.get("/me")
def get_current_user_info(current_user: Annotated[dict, Depends(get_auth_current_user)]) -> dict:
    """
    Get current user information including roles and permissions.

    Requires authentication. Returns the authenticated user's profile
    along with their role and permissions for UI rendering.

    Args:
        current_user: Current user from JWT token (injected by dependency).

    Returns:
        Dictionary containing:
        - id: User's ID
        - name: User's first name
        - lastname: User's last name
        - second_lastname: User's second last name (optional)
        - email: User's email address
        - role: User's role name (e.g., "admin", "user")
        - role_id: User's role ID
        - permissions: List of permission names (e.g., ["users:read", "users:write"])

    Raises:
        HTTPException: 401 if not authenticated.
        HTTPException: 404 if user not found.
    """
    # Get full user profile from database
    try:
        user = service.get_one(current_user.get("email"))
        if not user:
            logger.warning(f"User not found: {current_user.get('email')}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"API request: Retrieved current user info for {current_user.get('email')}")
        return {
            "id": user.id,
            "name": user.name,
            "lastname": user.lastname,
            "second_lastname": user.second_lastname,
            "email": user.email,
            "role": current_user.get("role"),
            "role_id": current_user.get("role_id"),
            "permissions": current_user.get("permissions", []),
        }
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError as e:
        logger.error(f"Database error in get_current_user_info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/")
def get_all(current_user: Annotated[dict, Depends(get_current_user)], skip: int = 0, limit: int = 20, order_by: str | None = None) -> UserPaginationResponse:
    """
    Retrieve users from the database with pagination.

    Requires authentication.

    Query Parameters:
        skip: Number of records to skip (default: 0).
        limit: Maximum number of records to return (default: 20).
        order_by: Field name to order results by (e.g., 'name', 'email', 'created_at'). Optional.

    Returns:
        UserPaginationResponse with list of UserResponseWithRole objects and metadata.

    Raises:
        HTTPException: 500 if database error occurs.
    """
    try:
        result = service.get_all_paginated(skip=skip, limit=limit, order_by=order_by)
        logger.info(f"API request: Retrieved {len(result.data)} users (total: {result.total}, skip: {skip}, limit: {limit}, order_by: {order_by}) by {current_user.get('sub')}")
        return result
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}", dependencies=[Depends(RoleAndPermissionChecker(required_roles=["admin"], required_permissions=["read:users", "write:users", "delete:users"]))])
def get_one_by_id(current_user: Annotated[dict, Depends(get_current_user)], user_id: int) -> UserResponseWithRole:
    """
    Retrieve a user by their ID.

    Requires admin role AND read:users, write:users, delete:users permissions.

    Args:
        user_id: The ID of the user.

    Returns:
        UserResponseWithRole object with role_name.

    Raises:
        HTTPException: 404 if user not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        user = service.get_one_by_id(user_id)
        logger.info(f"API request: Retrieved user with id {user_id}")
        return user
    except NotFoundError:
        logger.warning(f"User with id {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError as e:
        logger.error(f"Database error in get_one_by_id: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{user_id}", dependencies=[Depends(RoleAndPermissionChecker(required_roles=["admin"], required_permissions=["read:users","write:users"]))])
def modify_by_id(current_user: Annotated[dict, Depends(get_current_user)], user_id: int, user_update: UserUpdate) -> UserResponseWithRole:
    """
    Update an existing user's profile by their ID.

    Requires admin role AND write:users permission.

    Args:
        user_id: The ID of the user to update.
        user_update: UserUpdate schema with fields to update (name, lastname, second_lastname, role_id).

    Returns:
        Updated UserResponseWithRole object.

    Raises:
        HTTPException: 403 if user lacks admin role or write:users permission.
        HTTPException: 404 if user not found.
        HTTPException: 500 if database error occurs.
    """
    try:
        updated_user = service.modify_by_id(user_id, user_update)
        logger.info(f"API request: Modified user with id {user_id} by {current_user.get('sub')}")
        return updated_user
    except NotFoundError:
        logger.warning(f"User with id {user_id} not found for modification")
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError as e:
        logger.error(f"Database error in modify_by_id: {str(e)}")
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


@router.post("/", dependencies=[Depends(RoleAndPermissionChecker(required_roles=["admin"], required_permissions=["write:users"]))])
def create(user: UserCreate) -> UserResponse:
    """
    Create a new user account.

    Requires admin role AND write:users permission.

    Args:
        user: UserCreate schema with user data.

    Returns:
        Created UserResponse object.

    Raises:
        HTTPException: 403 if user lacks admin role or write:users permission.
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
