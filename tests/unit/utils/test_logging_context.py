import pytest
from utils.logging_context import (
    user_name_context,
    user_role_context,
    set_user_context,
    clear_user_context,
    reset_user_context,
    get_user_name,
    get_user_role,
)


@pytest.fixture(autouse=True)
def _reset_context():
    """Ensure each test starts from a clean (default) context."""
    reset_user_context()
    yield
    reset_user_context()


def test_defaults():
    """Context variables default to anonymous/None before any request."""
    assert get_user_name() == "anonymous"
    assert get_user_role() == "None"


def test_set_and_get_user_context():
    """set_user_context populates both context variables."""
    set_user_context("admin@example.com", "admin")
    assert get_user_name() == "admin@example.com"
    assert get_user_role() == "admin"


def test_clear_resets_to_defaults():
    """clear_user_context resets values to the anonymous/None defaults."""
    set_user_context("admin@example.com", "admin")
    clear_user_context()
    assert get_user_name() == "anonymous"
    assert get_user_role() == "None"


def test_reset_user_context():
    """reset_user_context restores defaults (used by middleware/auth failure path)."""
    set_user_context("admin@example.com", "admin")
    reset_user_context()
    assert get_user_name() == "anonymous"
    assert get_user_role() == "None"


def test_context_does_not_leak_after_clear():
    """Context must not retain prior values after reset."""
    set_user_context("admin@example.com", "admin")
    reset_user_context()
    assert user_name_context.get() == "anonymous"
    assert user_role_context.get() == "None"
