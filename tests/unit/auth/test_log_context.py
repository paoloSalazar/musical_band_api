import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from auth.auth import get_current_user
from utils.logging_context import (
    get_user_name,
    get_user_role,
    reset_user_context,
)


@pytest.fixture(autouse=True)
def _reset_context():
    """Ensure each test starts from a clean (default) context."""
    reset_user_context()
    yield
    reset_user_context()


def _creds(token: str = "fake-token") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.mark.asyncio
async def test_get_current_user_sets_log_context(mocker):
    """A valid token sets user_name (email) and user_role on the log context."""
    payload = {"sub": "admin@example.com", "user_id": 1, "role_id": 1}
    mocker.patch("auth.auth.decode_access_token", return_value=payload)

    mock_db = mocker.MagicMock()
    mock_role = mocker.MagicMock()
    mock_role.name = "admin"
    mock_role.permissions = []
    mock_db.query.return_value.filter.return_value.first.return_value = mock_role

    user = await get_current_user(credentials=_creds(), db=mock_db)

    assert user["email"] == "admin@example.com"
    assert user["role"] == "admin"
    assert get_user_name() == "admin@example.com"
    assert get_user_role() == "admin"


@pytest.mark.asyncio
async def test_get_current_user_clears_context_on_invalid_token(mocker):
    """An invalid/expired token resets the context to defaults before raising 401."""
    mocker.patch("auth.auth.decode_access_token", return_value={})

    # Pre-populate context to prove it gets cleared.
    from utils.logging_context import set_user_context
    set_user_context("admin@example.com", "admin")

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=_creds(), db=mocker.MagicMock())

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert get_user_name() == "anonymous"
    assert get_user_role() == "None"


@pytest.mark.asyncio
async def test_get_current_user_sets_none_role_when_no_role_id(mocker):
    """A token without role_id sets the role to 'None' while still setting user_name."""
    payload = {"sub": "user@example.com", "user_id": 2}
    mocker.patch("auth.auth.decode_access_token", return_value=payload)

    user = await get_current_user(credentials=_creds(), db=mocker.MagicMock())

    assert user["email"] == "user@example.com"
    assert user["role_id"] is None
    assert get_user_name() == "user@example.com"
    assert get_user_role() == "None"


@pytest.mark.asyncio
async def test_get_current_user_sets_none_role_when_role_not_found(mocker):
    """When the role_id is present but not in the DB, the role falls back to 'None'."""
    payload = {"sub": "ghost@example.com", "user_id": 9, "role_id": 99}
    mocker.patch("auth.auth.decode_access_token", return_value=payload)

    mock_db = mocker.MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    user = await get_current_user(credentials=_creds(), db=mock_db)

    assert user["email"] == "ghost@example.com"
    assert get_user_name() == "ghost@example.com"
    assert get_user_role() == "None"
