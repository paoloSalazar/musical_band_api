import pytest
from schemas.user import UserCreate, UserBase, UserResponse


def test_user_base_creation():
    """Test creating a UserBase instance"""
    user = UserBase(
        name="John",
        lastname="Doe",
        email="john.doe@example.com",
        role_id=1
    )
    assert user.name == "John"
    assert user.lastname == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.role_id == 1


def test_user_base_optional_second_lastname():
    """Test UserBase with optional second_lastname"""
    user = UserBase(
        name="Jane",
        lastname="Smith",
        email="jane.smith@example.com",
        role_id=2
    )
    assert user.name == "Jane"
    assert user.lastname == "Smith"
    assert user.second_lastname is None
    assert user.email == "jane.smith@example.com"


def test_user_create():
    """Test UserCreate inherits from UserBase"""
    user = UserCreate(
        name="Alice",
        lastname="Johnson",
        second_lastname="Marie",
        email="alice.johnson@example.com",
        password="securepass",
        role_id=3
    )
    assert user.name == "Alice"
    assert user.lastname == "Johnson"
    assert user.second_lastname == "Marie"
    assert user.email == "alice.johnson@example.com"
    assert user.password == "securepass"
    assert user.role_id == 3


def test_user_full():
    """Test User with id"""
    user = UserResponse(
        id=1,
        name="John",
        lastname="Doe",
        email="john.doe@example.com",
        role_id=1
    )
    assert user.id == 1
    assert user.name == "John"
    assert user.lastname == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.role_id == 1


def test_user_from_dict():
    """Test creating User from dictionary"""
    data = {
        "id": 2,
        "name": "Jane",
        "lastname": "Smith",
        "email": "jane.smith@example.com",
        "role_id": 2
    }
    user = UserResponse(**data)
    assert user.id == 2
    assert user.name == "Jane"
    assert user.lastname == "Smith"
    assert user.email == "jane.smith@example.com"
    assert user.role_id == 2


def test_user_to_dict():
    """Test converting User to dictionary"""
    user = UserResponse(
        id=3,
        name="Bob",
        lastname="Wilson",
        email="bob.wilson@example.com",
        role_id=1
    )
    data = user.model_dump()
    expected = {
        "id": 3,
        "name": "Bob",
        "lastname": "Wilson",
        "second_lastname": None,
        "email": "bob.wilson@example.com",
        "role_id": 1
    }
    assert data == expected