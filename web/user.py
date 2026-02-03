import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Request
from schemas.user_role import UserRole
from schemas.auth import Token
from schemas.user import UserResponse, UserCreate, UserLogin
import services.user as service
import services.auth as auth_service
from auth.auth import decode_access_token
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError, UnauthorizedError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users")


async def get_current_user(request: Request) -> dict:
    """Dependency to verify JWT token and return current user"""
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
    """Get all users (requires authentication)"""
    try:
        users = service.get_all()
        logger.info(f"API request: Retrieved {len(users)} users by {current_user.get('sub')}")
        return users
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{email}")
def get_one(current_user: Annotated[dict, Depends(get_current_user)], email: str) -> UserResponse:
    """Get one user by email"""
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
    """Create a new user"""
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
def modify(current_user: Annotated[dict, Depends(get_current_user)], user: UserResponse) -> UserResponse:
    """Modify an existing user"""
    try:
        updated_user = service.modify(user)
        logger.info(f"API request: Modified user with email {user.email} by {current_user.get('sub')}")
        return updated_user
    except NotFoundError:
        logger.warning(f"User with email {user.email} not found for modification")
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError as e:
        logger.error(f"Database error in modify: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=Token)
def login(login_data: UserLogin) -> Token:
    """Authenticate user and return access token"""
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
