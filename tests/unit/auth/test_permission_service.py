"""Tests for permission service."""

import pytest
from unittest.mock import Mock


def test_permission_service_exists():
    """PermissionService should exist."""
    from services.auth import PermissionService
    assert PermissionService is not None


def test_permission_service_has_has_permission():
    """PermissionService should have has_permission method."""
    from services.auth import PermissionService
    service = PermissionService()
    assert hasattr(service, 'has_permission')
    assert callable(service.has_permission)


def test_permission_service_has_get_user_permissions():
    """PermissionService should have get_user_permissions method."""
    from services.auth import PermissionService
    service = PermissionService()
    assert hasattr(service, 'get_user_permissions')
    assert callable(service.get_user_permissions)
