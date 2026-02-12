"""
Authentication service.

Provides business logic for user authentication including
password verification and JWT token generation.

Functions:
    - authenticate_user: Verify credentials and return access token
    - hash_password_for_user: Hash password for a user model
"""

import logging
from datetime import timedelta
from schemas.auth import Token
from schemas.user import UserLogin
from auth.auth import verify_password, get_password_hash, create_access_token
import data.user as data
from models.user import User as DBUser
from exceptions import NotFoundError, UnauthorizedError

logger = logging.getLogger(__name__)


def authenticate_user(login: UserLogin) -> Token:
    """
    Authenticate a user with email and password.

    Args:
        login: UserLogin schema containing email and password.

    Returns:
        Token response with JWT access token.

    Raises:
        NotFoundError: If user with email is not found.
        UnauthorizedError: If password is incorrect.
    """
    try:
        # Find user by email
        db_user = data.get_one(login.email)
        if db_user is None:
            logger.warning(f"Authentication failed: User with email {login.email} not found")
            raise NotFoundError("Invalid email or password")

        # Verify password
        if not verify_password(login.password, db_user.password):
            logger.warning(f"Authentication failed: Invalid password for user {login.email}")
            raise UnauthorizedError("Invalid email or password")

        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": db_user.email, "user_id": db_user.id, "role_id": db_user.role_id},
            expires_delta=access_token_expires
        )

        logger.info(f"User {login.email} authenticated successfully")
        return Token(access_token=access_token, token_type="bearer")

    except (NotFoundError, UnauthorizedError):
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise


def hash_password_for_user(user: DBUser) -> str:
    """
    Hash a password for a user model.

    Args:
        user: The User model containing the password to hash.

    Returns:
        Hashed password string.
    """
    return get_password_hash(user.password)
