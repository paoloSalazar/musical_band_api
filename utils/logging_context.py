"""
Request-scoped user context for logging.

Provides context variables that carry the authenticated user's name and role
across the lifetime of a single request, so that log records emitted from any
layer (web handlers, services, data access) include user context.

Context variables are isolated per asyncio task in FastAPI, making them safe
for use in concurrent async request handling. Unauthenticated requests (or
requests before authentication runs) automatically fall back to the defaults
``anonymous`` / ``None``.

Usage:
    from utils.logging_context import set_user_context, get_user_name

    set_user_context("admin@example.com", "admin")
    logger = logging.getLogger(__name__)
    logger.info(f"Doing work for {get_user_name()}")
"""

import contextvars

user_name_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "user_name", default="anonymous"
)

user_role_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "user_role", default="None"
)

_DEFAULT_USER_NAME = "anonymous"
_DEFAULT_USER_ROLE = "None"


def set_user_context(user_name: str | None, user_role: str | None) -> None:
    """
    Set the user context for the current request.

    Args:
        user_name: The authenticated user's email (from the JWT ``sub``),
            or ``None`` to clear.
        user_role: The authenticated user's role name (e.g. "admin"),
            or ``None`` to clear.

    Note:
        Passing ``None`` for either value resets that context variable to its
        default (``anonymous`` / ``None``), matching the behaviour of
        :func:`reset_user_context`.
    """
    user_name_context.set(user_name if user_name is not None else _DEFAULT_USER_NAME)
    user_role_context.set(user_role if user_role is not None else _DEFAULT_USER_ROLE)


def clear_user_context() -> None:
    """
    Reset the user context to the anonymous/None defaults.

    Intended to be called at the end of a request so that context variables do
    not leak into subsequent requests that may reuse the same asyncio task.
    """
    user_name_context.set(_DEFAULT_USER_NAME)
    user_role_context.set(_DEFAULT_USER_ROLE)


def reset_user_context() -> None:
    """
    Restore the user context to the anonymous/None defaults.

    This is an alias for :func:`clear_user_context` provided to make call sites
    self-documenting: middleware and auth-failure paths "reset" context at the
    start of a request or when authentication fails.
    """
    clear_user_context()


def get_user_name() -> str:
    """Return the user name (email) for the current context (default ``anonymous``)."""
    return user_name_context.get()


def get_user_role() -> str:
    """Return the user role for the current context, defaulting to ``None``."""
    return user_role_context.get()
