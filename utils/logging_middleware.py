"""
Request-scoped logging context middleware.

An HTTP middleware that isolates the request-scoped user context (see
:mod:`utils.logging_context`):

- **At request start**: resets the context to the ``anonymous``/``None``
  defaults, so stale values left behind by a previous request on a reused
  asyncio task cannot leak into the current request's log records.
- **At request end** (in a ``finally``): clears the context again, so any
  background work scheduled after the response is produced does not carry
  request-specific user information.

This middleware does **not** authenticate users or decode JWTs. User context
is populated once, authoritatively, in ``auth.auth.get_current_user`` (Phase 4
of the logging improvements plan). Endpoints that bypass that dependency are
unauthenticated by definition, so they correctly log ``anonymous``/``None``.

Registration (in ``main.py``):

    from utils.logging_middleware import reset_context_middleware
    app.middleware("http")(reset_context_middleware)
"""

from __future__ import annotations

from utils.logging_context import clear_user_context, reset_user_context


async def reset_context_middleware(request, call_next):
    """
    Isolate the logging context for the duration of a single request.

    Args:
        request: The incoming Starlette/FastAPI request (passed through to the
            next middleware / route handler).
        call_next: The ASGI callable that dispatches to the rest of the
            middleware stack and route handlers.

    Returns:
        The response produced by ``call_next(request)``, unmodified.
    """
    reset_user_context()
    try:
        return await call_next(request)
    finally:
        clear_user_context()
