import logging

import pytest

from utils.custom_formatter import ContextAwareFormatter
from utils.logging_context import reset_user_context, set_user_context


@pytest.fixture(autouse=True)
def _reset_context():
    """Ensure each test starts from a clean (default) context."""
    reset_user_context()
    yield
    reset_user_context()


def _make_record(msg: str = "test message") -> logging.LogRecord:
    return logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg=msg,
        args=None,
        exc_info=None,
    )


def test_log_format_constant():
    """The formatter exposes the target format string as a class constant."""
    assert ContextAwareFormatter.LOG_FORMAT == (
        "%(asctime)s - %(name)s - %(levelname)s - %(user_name)s - "
        "%(user_role)s - %(message)s"
    )
    assert "%(user_name)s" in ContextAwareFormatter.LOG_FORMAT
    assert "%(user_role)s" in ContextAwareFormatter.LOG_FORMAT


def test_format_includes_user_context():
    """Formatter injects the current user_name and user_role into the output."""
    set_user_context("admin@example.com", "admin")
    formatter = ContextAwareFormatter(ContextAwareFormatter.LOG_FORMAT)
    output = formatter.format(_make_record("hello"))

    assert "admin@example.com" in output
    assert "admin" in output
    assert "hello" in output


def test_format_uses_defaults_when_anonymous():
    """With an empty context, the formatter falls back to anonymous/None."""
    formatter = ContextAwareFormatter(ContextAwareFormatter.LOG_FORMAT)
    output = formatter.format(_make_record("some log line"))

    assert "anonymous" in output
    assert "None" in output
    assert "some log line" in output


def test_format_reflects_context_change_per_record():
    """Context changes are reflected on subsequent format calls."""
    formatter = ContextAwareFormatter(ContextAwareFormatter.LOG_FORMAT)

    set_user_context("admin@example.com", "admin")
    first = formatter.format(_make_record("msg-one"))
    assert "admin@example.com" in first

    reset_user_context()
    second = formatter.format(_make_record("msg-two"))
    assert "anonymous" in second
    assert "admin@example.com" not in second
