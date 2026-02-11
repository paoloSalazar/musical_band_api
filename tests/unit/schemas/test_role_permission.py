import pytest
from datetime import datetime
from schemas.permission import RolePermissionCreate, RolePermissionResponse


def test_role_permission_create():
    """Test creating a RolePermissionCreate instance"""
    schema = RolePermissionCreate(role_id=1, permission_id=2)
    assert schema.role_id == 1
    assert schema.permission_id == 2


def test_role_permission_create_order():
    """Test RolePermissionCreate with reversed order"""
    schema = RolePermissionCreate(role_id=5, permission_id=10)
    assert schema.role_id == 5
    assert schema.permission_id == 10


def test_role_permission_response():
    """Test RolePermissionResponse schema"""
    schema = RolePermissionResponse(role_id=1, permission_id=2)
    assert schema.role_id == 1
    assert schema.permission_id == 2


def test_role_permission_response_from_attributes():
    """Test RolePermissionResponse from model attributes"""
    class MockRolePermission:
        role_id = 1
        permission_id = 2
    
    schema = RolePermissionResponse.model_validate(MockRolePermission())
    assert schema.role_id == 1
    assert schema.permission_id == 2


def test_role_permission_create_to_dict():
    """Test converting RolePermissionCreate to dictionary"""
    schema = RolePermissionCreate(role_id=3, permission_id=7)
    data = schema.model_dump()
    assert data == {"role_id": 3, "permission_id": 7}


def test_role_permission_response_to_dict():
    """Test converting RolePermissionResponse to dictionary"""
    schema = RolePermissionResponse(role_id=4, permission_id=8)
    data = schema.model_dump()
    assert data == {"role_id": 4, "permission_id": 8}


def test_role_permission_equality():
    """Test RolePermission schema equality"""
    schema1 = RolePermissionCreate(role_id=1, permission_id=2)
    schema2 = RolePermissionCreate(role_id=1, permission_id=2)
    assert schema1.role_id == schema2.role_id
    assert schema1.permission_id == schema2.permission_id


def test_role_permission_different_values():
    """Test RolePermission with different values"""
    schema1 = RolePermissionCreate(role_id=1, permission_id=2)
    schema2 = RolePermissionCreate(role_id=2, permission_id=1)
    assert schema1.role_id != schema2.role_id
    assert schema1.permission_id != schema2.permission_id
