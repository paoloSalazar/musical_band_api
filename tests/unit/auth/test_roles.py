"""Tests for RBAC roles and permissions."""

import pytest
from auth.roles import Role, Permission


def test_permission_exists():
    """Permission enum should exist."""
    assert hasattr(Permission, 'READ_USERS')
    assert hasattr(Permission, 'WRITE_USERS')
    assert hasattr(Permission, 'DELETE_USERS')
    assert hasattr(Permission, 'READ_ROLES')
    assert hasattr(Permission, 'WRITE_ROLES')
    assert hasattr(Permission, 'ADMIN')


def test_permission_values_are_strings():
    """Permission values should be strings."""
    assert isinstance(Permission.READ_USERS.value, str)
    assert isinstance(Permission.ADMIN.value, str)


def test_role_exists():
    """Role enum should exist."""
    assert hasattr(Role, 'ADMIN')
    assert hasattr(Role, 'MODERATOR')
    assert hasattr(Role, 'USER')


def test_admin_has_all_permissions():
    """Admin role should have all permissions."""
    admin = Role.ADMIN
    expected_permissions = [
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_ROLES,
        Permission.WRITE_ROLES,
        Permission.ADMIN,
    ]
    for perm in expected_permissions:
        assert perm in admin.permissions, f"Admin should have {perm}"


def test_moderator_permissions():
    """Moderator role should have read and write permissions but not delete or admin."""
    moderator = Role.MODERATOR
    assert Permission.READ_USERS in moderator.permissions
    assert Permission.WRITE_USERS in moderator.permissions
    assert Permission.READ_ROLES in moderator.permissions
    assert Permission.WRITE_ROLES in moderator.permissions
    assert Permission.DELETE_USERS not in moderator.permissions
    assert Permission.ADMIN not in moderator.permissions


def test_user_permissions():
    """User role should have only read permissions."""
    user = Role.USER
    assert Permission.READ_USERS in user.permissions
    assert Permission.WRITE_USERS not in user.permissions
    assert Permission.DELETE_USERS not in user.permissions
    assert Permission.READ_ROLES in user.permissions
    assert Permission.WRITE_ROLES not in user.permissions
    assert Permission.ADMIN not in user.permissions


def test_role_permissions_returns_set():
    """Role.permissions should return a set."""
    assert isinstance(Role.ADMIN.permissions, set)
