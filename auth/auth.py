"""
Authentication and JWT token management for the Musical Band API.

This module provides:
- Password hashing and verification using bcrypt
- JWT access token creation and decoding
- User authentication dependency for FastAPI endpoints

Example:
    >>> from auth.auth import get_password_hash, verify_password, create_access_token
    >>> hashed = get_password_hash("secure_password")
    >>> verify_password("secure_password", hashed)
    True
"""

from datetime import datetime, timedelta, timezone
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
import base64

# Import JWT configuration from config module
from config.jwt_config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration (loaded from environment variables)
SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its bcrypt hash.

    Truncates password to 72 bytes (bcrypt limit) before verification.

    Args:
        plain_password: The plain text password to verify.
        hashed_password: The bcrypt hash to verify against.

    Returns:
        True if the password matches, False otherwise.

    Example:
        >>> verify_password("my_password", get_password_hash("my_password"))
        True
    """
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Truncates password to 72 bytes (bcrypt limit) for security.

    Args:
        password: The plain text password to hash.

    Returns:
        The bcrypt hashed password.

    Example:
        >>> hash = get_password_hash("my_secure_password")
        >>> hash.startswith("$2b$")
        True
    """
    safe_password = password.encode('utf-8')[:72]
    return pwd_context.hash(safe_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token with the given payload.

    Args:
        data: Dictionary containing the token payload (e.g., user_id, role_id).
        expires_delta: Optional custom expiration time delta.
                       If not provided, uses default from config.

    Returns:
        Encoded JWT token string.

    Example:
        >>> token = create_access_token({"user_id": 1, "role_id": 2})
        >>> len(token) > 0
        True
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token string to decode.

    Returns:
        Dictionary containing the token payload if valid.
        Empty dictionary if token is invalid or expired.

    Example:
        >>> token = create_access_token({"user_id": 1})
        >>> payload = decode_access_token(token)
        >>> payload.get("user_id")
        1
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return {}


# Auth Dependencies
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models.user_role import UserRole
from config.database import get_db
from utils.logging_context import set_user_context, reset_user_context

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get the current authenticated user from the JWT token.

    This is a FastAPI dependency that extracts and validates the JWT token
    from the Authorization header, then retrieves the user's role and
    permissions from the database.

    Args:
        credentials: HTTP Bearer token credentials from the request header.
        db: Database session dependency.

    Returns:
        Dictionary containing user information:
        - id: User's ID
        - email: User's email address
        - role: User's role name (e.g., "admin", "user")
        - permissions: List of permission names (e.g., ["users:read", "users:write"])
        - role_id: User's role ID

    Raises:
        HTTPException: 401 if token is invalid or expired.

    Example:
        >>> # Used as a dependency in FastAPI endpoints
        >>> @router.get("/me")
        >>> async def get_me(user: dict = Depends(get_current_user)):
        >>>     return user
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        reset_user_context()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user role name and permissions from database
    role_id = payload.get("role_id")
    role_name = None
    user_permissions = []
    if role_id:
        role = db.query(UserRole).filter(UserRole.id == role_id).first()
        if role:
            role_name = role.name
            user_permissions = [p.name for p in role.permissions]

    set_user_context(payload.get("sub"), role_name)

    return {
        "id": payload.get("user_id"),
        "email": payload.get("sub"),
        "role": role_name or payload.get("role_id"),
        "permissions": user_permissions,
        "role_id": role_id,
    }
