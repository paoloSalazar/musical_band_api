"""
Pytest configuration for model tests.

This file ensures all SQLAlchemy models are imported and registered
before any tests run. This prevents "mapper initialization" errors
that can occur when models with relationships are imported in isolation.
"""

# Import all models to ensure they are registered with SQLAlchemy
from models.user import User
from models.user_role import UserRole
from models.user_detail import UserDetail
from models.permission import Permission
from models.event import Event
from models.musician_availability import MusicianAvailability

# This import ensures all models are registered with the Base metadata
# and their relationships are properly configured
from config.database import Base
