"""
JWT configuration settings loaded from environment variables.

Provides secure configuration management for JWT authentication.

Environment Variables:
    JWT_SECRET_KEY: Secret key for signing tokens (change in production!)
    JWT_ALGORITHM: JWT algorithm (default: HS256)
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time in minutes (default: 30)

Example:
    >>> from config.jwt_config import JWT_SECRET_KEY, JWT_ALGORITHM
    >>> token = create_access_token({"user_id": 1}, expires_delta=timedelta(minutes=15))
"""

import os
from functools import lru_cache
from typing import Optional

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    # Look for .env file in the project root (current working directory)
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip loading
    pass


def get_env_var(key: str, default: Optional[str] = None) -> str:
    """
    Get an environment variable with an optional default value.

    Args:
        key: The name of the environment variable.
        default: Value to return if the variable is not set.

    Returns:
        The environment variable value, or the default if not set.

    Example:
        >>> get_env_var("DEBUG", "False")
        'False'
    """
    return os.getenv(key, default) if default is not None else os.getenv(key, "")


# JWT Configuration
JWT_SECRET_KEY: str = get_env_var("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM: str = get_env_var("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(get_env_var("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


@lru_cache()
def get_jwt_settings() -> dict:
    """
    Get JWT settings as a dictionary.

    Results are cached for performance.

    Returns:
        Dictionary containing:
        - SECRET_KEY: JWT signing secret
        - ALGORITHM: JWT algorithm
        - ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time

    Example:
        >>> settings = get_jwt_settings()
        >>> settings["SECRET_KEY"]
        'your-secret-key'
    """
    return {
        "SECRET_KEY": JWT_SECRET_KEY,
        "ALGORITHM": JWT_ALGORITHM,
        "ACCESS_TOKEN_EXPIRE_MINUTES": JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    }
