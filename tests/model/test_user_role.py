import pytest
from model.user_role import UserRole

def test_user_role_creation():
    user_role = UserRole(name="admin", description="Administrator role")
    assert user_role.name == "admin"
    assert user_role.description == "Administrator role"
    assert user_role.id is None  # ID is assigned by DB