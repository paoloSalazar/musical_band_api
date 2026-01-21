import pytest
from schemas.user_role import UserRole, UserRoleCreate, UserRoleBase


def test_user_role_base_creation():
    """Test creating a UserRoleBase instance"""
    role = UserRoleBase(name="admin", description="Administrator role")
    assert role.name == "admin"
    assert role.description == "Administrator role"


def test_user_role_base_optional_description():
    """Test UserRoleBase with optional description"""
    role = UserRoleBase(name="user")
    assert role.name == "user"
    assert role.description is None


def test_user_role_create():
    """Test UserRoleCreate inherits from UserRoleBase"""
    role = UserRoleCreate(name="moderator", description="Moderation role")
    assert role.name == "moderator"
    assert role.description == "Moderation role"


def test_user_role_full():
    """Test UserRole with id"""
    role = UserRole(id=1, name="admin", description="Administrator role")
    assert role.id == 1
    assert role.name == "admin"
    assert role.description == "Administrator role"


def test_user_role_from_dict():
    """Test creating UserRole from dictionary"""
    data = {"id": 2, "name": "user", "description": "Regular user"}
    role = UserRole(**data)
    assert role.id == 2
    assert role.name == "user"
    assert role.description == "Regular user"


def test_user_role_to_dict():
    """Test converting UserRole to dictionary"""
    role = UserRole(id=3, name="guest", description="Guest user")
    data = role.model_dump()
    assert data == {"id": 3, "name": "guest", "description": "Guest user"}