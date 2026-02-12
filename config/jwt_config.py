"""Configuration settings loaded from environment variables."""

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
    """Get environment variable with optional default."""
    return os.getenv(key, default) if default is not None else os.getenv(key, "")


# JWT Configuration
JWT_SECRET_KEY: str = get_env_var("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM: str = get_env_var("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(get_env_var("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


@lru_cache()
def get_jwt_settings() -> dict:
    """Get JWT settings as a dictionary (cached)."""
    return {
        "SECRET_KEY": JWT_SECRET_KEY,
        "ALGORITHM": JWT_ALGORITHM,
        "ACCESS_TOKEN_EXPIRE_MINUTES": JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    }
