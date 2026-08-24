"""
Centralized logging configuration.

Sets up the root logger with a :class:`utils.custom_formatter.ContextAwareFormatter`
so that every log record carries the request-scoped ``user_name`` and
``user_role`` context. Replaces the previous ``logging.basicConfig`` call in
``main.py``.

Run once at application startup (before other module imports that emit log
records). Safe to call repeatedly: existing handlers are closed and replaced.

Usage:
    from utils.logging_config import configure_logging

    configure_logging()
"""

import logging

from utils.custom_formatter import ContextAwareFormatter, LOG_FORMAT

LOG_FILE_PATH = "logs/logs.txt"


def configure_logging() -> None:
    """
    Configure the root logger with file + stream handlers and user-aware format.

    - Attaches a :class:`~logging.FileHandler` (``logs/logs.txt``) and a
      :class:`~logging.StreamHandler` (console), both using
      :class:`ContextAwareFormatter` with :data:`LOG_FORMAT`.
    - Sets the root logger level to ``INFO``.
    - Suppresses chatty framework loggers (SQLAlchemy internals, watchfiles).

    Existing handlers on the root logger are removed and closed first, so the
    function is idempotent and safe to call more than once.
    """
    root = logging.getLogger()

    # Remove any pre-existing handlers so repeated calls do not duplicate logs.
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()

    root.setLevel(logging.INFO)

    formatter = ContextAwareFormatter(LOG_FORMAT)

    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    # Suppress watchfiles logging (used by uvicorn reload)
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

    # Suppress SQLAlchemy detailed logging (queries, connection details)
    logging.getLogger("sqlalchemy").setLevel(logging.CRITICAL)
    for name in [
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "sqlalchemy.orm",
        "sqlalchemy.dialects",
        "sqlalchemy.engine.base",
    ]:
        logging.getLogger(name).setLevel(logging.CRITICAL)
