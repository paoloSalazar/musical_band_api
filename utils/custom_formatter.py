"""
Context-aware logging formatter.

A :class:`logging.Formatter` subclass that injects the request-scoped
``user_name`` and ``user_role`` values (see :mod:`utils.logging_context`) into
every log record, so the standard format string can reference them with the
``%(user_name)s`` and ``%(user_role)s`` placeholders.

When no user context is set (e.g. unauthenticated requests or background
tasks), the values fall back to ``anonymous`` / ``None`` via the context
variable defaults.

Usage:
    from utils.custom_formatter import ContextAwareFormatter

    handler = logging.StreamHandler()
    handler.setFormatter(ContextAwareFormatter(ContextAwareFormatter.LOG_FORMAT))
    logging.getLogger().addHandler(handler)
"""

import logging

from utils.logging_context import get_user_name, get_user_role

LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(user_name)s - "
    "%(user_role)s - %(message)s"
)


class ContextAwareFormatter(logging.Formatter):
    """Logging formatter that enriches records with request-scoped user context."""

    LOG_FORMAT: str = LOG_FORMAT

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the specified record as text.

        Injects ``user_name`` and ``user_role`` attributes onto the record from
        the current ``contextvars`` context before delegating to the base
        formatter, so the format string can use ``%(user_name)s`` /
        ``%(user_role)s``.

        Args:
            record: The log record to format.

        Returns:
            The formatted log message string.
        """
        record.user_name = get_user_name()
        record.user_role = get_user_role()
        return super().format(record)
