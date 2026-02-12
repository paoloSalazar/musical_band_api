import pytest
from models.permission import Permission


def test_permission_creation():
    """Test creating a Permission instance"""
    permission = Permission(name="read_users", description="Permission to read users")
    assert permission.name == "read_users"
    assert permission.description == "Permission to read users"
    assert permission.id is None  # ID is assigned by DB


def test_permission_creation_minimal():
    """Test creating a Permission with minimal fields"""
    permission = Permission(name="write_posts")
    assert permission.name == "write_posts"
    assert permission.description is None


def test_permission_repr():
    """Test Permission __repr__ method"""
    permission = Permission(name="delete_users", description="Permission to delete users")
    repr_str = repr(permission)
    assert repr_str == "<Permission(name=delete_users, description=Permission to delete users)>"


def test_permission_repr_no_description():
    """Test Permission __repr__ with no description"""
    permission = Permission(name="read_only")
    repr_str = repr(permission)
    assert repr_str == "<Permission(name=read_only, description=None)>"


def test_permission_equality():
    """Test Permission equality based on attributes"""
    perm1 = Permission(id=1, name="admin", description="Admin permission")
    perm2 = Permission(id=1, name="admin", description="Admin permission")
    assert perm1.name == perm2.name
    assert perm1.description == perm2.description


def test_permission_with_roles_relationship():
    """Test Permission roles relationship attribute exists"""
    permission = Permission(name="manage_settings", description="Manage system settings")
    # The relationship attribute should exist (even if empty initially)
    assert hasattr(permission, 'roles')
    assert permission.roles == []
