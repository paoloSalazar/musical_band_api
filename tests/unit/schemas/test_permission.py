import pytest
from datetime import datetime
from schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionWithRoles,
)


def test_permission_create():
    """Test creating a PermissionCreate instance"""
    schema = PermissionCreate(name="read_users", description="Permission to read users")
    assert schema.name == "read_users"
    assert schema.description == "Permission to read users"


def test_permission_create_minimal():
    """Test creating a PermissionCreate with minimal fields"""
    schema = PermissionCreate(name="write_posts")
    assert schema.name == "write_posts"
    assert schema.description is None


def test_permission_create_required_name():
    """Test that name is required in PermissionCreate"""
    schema = PermissionCreate(name="admin")
    assert schema.name == "admin"


def test_permission_update_partial():
    """Test PermissionUpdate with partial fields"""
    schema = PermissionUpdate()
    assert schema.name is None
    assert schema.description is None


def test_permission_update_name_only():
    """Test PermissionUpdate with only name updated"""
    schema = PermissionUpdate(name="new_name")
    assert schema.name == "new_name"
    assert schema.description is None


def test_permission_update_description_only():
    """Test PermissionUpdate with only description updated"""
    schema = PermissionUpdate(description="New description")
    assert schema.name is None
    assert schema.description == "New description"


def test_permission_response():
    """Test PermissionResponse schema"""
    schema = PermissionResponse(id=1, name="read_users", description="Read access")
    assert schema.id == 1
    assert schema.name == "read_users"
    assert schema.description == "Read access"


def test_permission_response_from_attributes():
    """Test PermissionResponse from model attributes"""
    # Simulating what happens when converting from ORM model
    class MockPermission:
        id = 1
        name = "write_users"
        description = "Write access"
    
    schema = PermissionResponse.model_validate(MockPermission())
    assert schema.id == 1
    assert schema.name == "write_users"
    assert schema.description == "Write access"


def test_permission_with_roles():
    """Test PermissionWithRoles schema"""
    schema = PermissionWithRoles(
        id=1,
        name="manage_users",
        description="Manage users permission",
        roles=[1, 2, 3]
    )
    assert schema.id == 1
    assert schema.name == "manage_users"
    assert schema.description == "Manage users permission"
    assert schema.roles == [1, 2, 3]


def test_permission_with_roles_empty():
    """Test PermissionWithRoles with no roles"""
    schema = PermissionWithRoles(
        id=2,
        name="read_only",
        description="Read only access",
        roles=[]
    )
    assert schema.roles == []


def test_permission_create_to_dict():
    """Test converting PermissionCreate to dictionary"""
    schema = PermissionCreate(name="delete_items", description="Delete items permission")
    data = schema.model_dump()
    assert data == {"name": "delete_items", "description": "Delete items permission"}


def test_permission_response_to_dict():
    """Test converting PermissionResponse to dictionary"""
    schema = PermissionResponse(id=5, name="admin", description="Admin access")
    data = schema.model_dump()
    assert data == {"id": 5, "name": "admin", "description": "Admin access"}


def test_permission_with_roles_to_dict():
    """Test converting PermissionWithRoles to dictionary"""
    schema = PermissionWithRoles(
        id=3,
        name="edit_content",
        description="Edit content permission",
        roles=[1, 4]
    )
    data = schema.model_dump()
    assert data == {
        "id": 3,
        "name": "edit_content",
        "description": "Edit content permission",
        "roles": [1, 4]
    }
