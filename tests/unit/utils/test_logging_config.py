import logging

import pytest

from utils.custom_formatter import ContextAwareFormatter, LOG_FORMAT
from utils.logging_config import configure_logging


@pytest.fixture(autouse=True)
def _restore_root_logger():
    """Snapshot and restore root logger + sqlalchemy suppression state."""
    root = logging.getLogger()
    sa_logger = logging.getLogger("sqlalchemy")
    saved = {
        "handlers": root.handlers[:],
        "level": root.level,
        "sa_level": sa_logger.level,
        "sa_prop": sa_logger.propagate,
    }
    yield
    # Close any handlers that configure_logging() added (e.g. FileHandler)
    for handler in list(root.handlers):
        if handler not in saved["handlers"]:
            handler.close()
            root.removeHandler(handler)
    root.handlers = saved["handlers"]
    root.level = saved["level"]
    sa_logger.setLevel(saved["sa_level"])
    sa_logger.propagate = saved["sa_prop"]


def _all_formatters():
    root = logging.getLogger()
    return [h.formatter for h in root.handlers if h.formatter]


def test_configure_logging_level_is_info():
    """Root logger level is set to INFO after configuration."""
    configure_logging()
    assert logging.getLogger().level == logging.INFO


def test_configure_logging_uses_custom_formatter():
    """At least one handler uses ContextAwareFormatter with the user-context format."""
    configure_logging()
    formatters = _all_formatters()

    assert formatters, "configure_logging() should attach at least one handler"
    assert any(isinstance(f, ContextAwareFormatter) for f in formatters)
    assert all(
        "%(user_name)s" in f._fmt and "%(user_role)s" in f._fmt for f in formatters
    )


def test_configure_logging_format_matches_constant():
    """The formatter's _fmt matches the shared LOG_FORMAT constant."""
    configure_logging()
    formatters = _all_formatters()
    assert any(f._fmt == LOG_FORMAT for f in formatters)


def test_configure_logging_attaches_file_and_stream_handlers():
    """Both a FileHandler and a StreamHandler are attached."""
    configure_logging()
    handlers = logging.getLogger().handlers

    assert any(isinstance(h, logging.FileHandler) for h in handlers)
    stream_handlers = [
        h for h in handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.FileHandler)
    ]
    assert stream_handlers


def test_configure_logging_suppresses_sqlalchemy():
    """SQLAlchemy debug logging is suppressed to CRITICAL."""
    configure_logging()

    for name in ["sqlalchemy", "sqlalchemy.engine", "sqlalchemy.pool"]:
        assert logging.getLogger(name).level == logging.CRITICAL


def test_configure_logging_file_handler_points_to_logs_dir():
    """The FileHandler writes to logs/logs.txt."""
    configure_logging()
    file_handlers = [
        h for h in logging.getLogger().handlers if isinstance(h, logging.FileHandler)
    ]
    assert file_handlers
    assert file_handlers[0].baseFilename.endswith("logs/logs.txt")
