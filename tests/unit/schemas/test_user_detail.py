import pytest
from schemas.user_detail import (
    UserDetailCreate,
    UserDetailUpdate,
    UserDetailResponse,
)


def test_user_detail_create():
    """Test creating a UserDetailCreate instance"""
    schema = UserDetailCreate(
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )
    assert schema.user_id == 1
    assert schema.detail_type == "phone"
    assert schema.detail_value == "+1234567890"


def test_user_detail_create_with_address():
    """Test creating a UserDetailCreate with address type"""
    schema = UserDetailCreate(
        user_id=1,
        detail_type="address",
        detail_value="123 Main St"
    )
    assert schema.user_id == 1
    assert schema.detail_type == "address"
    assert schema.detail_value == "123 Main St"


def test_user_detail_update_partial():
    """Test UserDetailUpdate with partial fields"""
    schema = UserDetailUpdate()
    assert schema.detail_value is None


def test_user_detail_update_value_only():
    """Test UserDetailUpdate with only value updated"""
    schema = UserDetailUpdate(detail_value="+0987654321")
    assert schema.detail_value == "+0987654321"


def test_user_detail_response():
    """Test UserDetailResponse schema"""
    schema = UserDetailResponse(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )
    assert schema.id == 1
    assert schema.user_id == 1
    assert schema.detail_type == "phone"
    assert schema.detail_value == "+1234567890"


def test_user_detail_response_from_attributes():
    """Test UserDetailResponse from model attributes"""
    # Simulating what happens when converting from ORM model
    class MockUserDetail:
        id = 1
        user_id = 1
        detail_type = "email"
        detail_value = "test@example.com"
    
    schema = UserDetailResponse.model_validate(MockUserDetail())
    assert schema.id == 1
    assert schema.user_id == 1
    assert schema.detail_type == "email"
    assert schema.detail_value == "test@example.com"


def test_user_detail_create_to_dict():
    """Test converting UserDetailCreate to dictionary"""
    schema = UserDetailCreate(
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )
    data = schema.model_dump()
    assert data == {
        "user_id": 1,
        "detail_type": "phone",
        "detail_value": "+1234567890"
    }


def test_user_detail_response_to_dict():
    """Test converting UserDetailResponse to dictionary"""
    schema = UserDetailResponse(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )
    data = schema.model_dump()
    assert data == {
        "id": 1,
        "user_id": 1,
        "detail_type": "phone",
        "detail_value": "+1234567890"
    }
