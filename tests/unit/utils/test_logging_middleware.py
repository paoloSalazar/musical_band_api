import pytest

from utils.logging_context import (
    get_user_name,
    get_user_role,
    reset_user_context,
    set_user_context,
)
from utils.logging_middleware import reset_context_middleware


@pytest.fixture(autouse=True)
def _reset_context():
    """Ensure each test starts from a clean (default) context."""
    reset_user_context()
    yield
    reset_user_context()


@pytest.mark.asyncio
async def test_middleware_resets_context_before_handler_and_clears_after():
    """Stale context is reset before the handler runs, then cleared after."""
    # Simulate leaked context from a previous request on a reused asyncio task.
    set_user_context("stale@example.com", "admin")

    observed = {}

    async def call_next(request):
        observed["name"] = get_user_name()
        observed["role"] = get_user_role()
        return "RESPONSE"

    response = await reset_context_middleware(
        request=object(), call_next=call_next
    )

    # Context was reset to defaults BEFORE the handler ran.
    assert observed["name"] == "anonymous"
    assert observed["role"] == "None"
    # Context was cleared AFTER the handler completed.
    assert get_user_name() == "anonymous"
    assert get_user_role() == "None"
    # The handler's response passes through unchanged.
    assert response == "RESPONSE"


@pytest.mark.asyncio
async def test_middleware_clears_context_even_when_handler_raises():
    """The finally block clears context even if the handler raises."""

    async def call_next(request):
        # Context should already be reset by the time the handler runs.
        assert get_user_name() == "anonymous"
        raise RuntimeError("handler blew up")

    with pytest.raises(RuntimeError):
        await reset_context_middleware(request=object(), call_next=call_next)

    assert get_user_name() == "anonymous"
    assert get_user_role() == "None"
