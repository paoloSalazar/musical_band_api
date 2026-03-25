import pytest
from models.user_detail import UserDetail


def test_user_detail_creation():
    """Test creating a UserDetail instance"""
    detail = UserDetail(
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )
    assert detail.user_id == 1
    assert detail.detail_type == "phone"
    assert detail.detail_value == "+1234567890"
    assert detail.id is None  # ID is assigned by DB


def test_user_detail_creation_with_id():
    """Test creating a UserDetail with ID"""
    detail = UserDetail(
        id=1,
        user_id=1,
        detail_type="address",
        detail_value="123 Main St"
    )
    assert detail.id == 1
    assert detail.user_id == 1
    assert detail.detail_type == "address"
    assert detail.detail_value == "123 Main St"


def test_user_detail_repr():
    """Test UserDetail __repr__ method"""
    detail = UserDetail(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )
    repr_str = repr(detail)
    assert "UserDetail" in repr_str
    assert "phone" in repr_str


def test_user_detail_equality():
    """Test UserDetail equality based on attributes"""
    detail1 = UserDetail(id=1, user_id=1, detail_type="email", detail_value="test@example.com")
    detail2 = UserDetail(id=1, user_id=1, detail_type="email", detail_value="test@example.com")
    assert detail1.user_id == detail2.user_id
    assert detail1.detail_type == detail2.detail_type
    assert detail1.detail_value == detail2.detail_value


def test_user_detail_with_user_relationship():
    """Test UserDetail user relationship attribute exists"""
    detail = UserDetail(user_id=1, detail_type="phone", detail_value="+1234567890")
    # The relationship attribute should exist
    assert hasattr(detail, 'user')
