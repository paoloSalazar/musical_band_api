import pytest
from models.user import User

def test_user_creation():
    user = User(
        name="John",
        lastname="Doe",
        second_lastname="Smith",
        email="john.doe@example.com",
        password="hashedpass",
        role_id=1
    )
    assert user.name == "John"
    assert user.lastname == "Doe"
    assert user.second_lastname == "Smith"
    assert user.email == "john.doe@example.com"
    assert user.password == "hashedpass"
    assert user.role_id == 1
    assert user.id is None  # ID is assigned by DB

def test_user_repr():
    user = User(
        name="Jane",
        lastname="Doe",
        email="jane.doe@example.com",
        password="pass",
        role_id=2
    )
    repr_str = repr(user)
    assert repr_str == "<User(name=Jane, email=jane.doe@example.com)>"