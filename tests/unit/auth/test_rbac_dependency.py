"""Tests for RBAC FastAPI dependencies."""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from auth.roles import Role, Permission


def test_require_permission_exists():
    """require_permission function should exist."""
    from auth.auth import require_permission
    assert callable(require_permission)


def test_require_role_exists():
    """require_role function should exist."""
    from auth.auth import require_role
    assert callable(require_role)


def test_get_current_user_exists():
    """get_current_user function should exist."""
    from auth.auth import get_current_user
    assert callable(get_current_user)
