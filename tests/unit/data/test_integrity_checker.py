"""
Unit tests for database integrity checker.

Tests follow TDD approach - define expected behavior before implementation.
"""
import pytest
from unittest.mock import MagicMock, patch
from data.integrity_checker import check_integrity_before_deletion, _check_user_integrity, _check_role_integrity, _check_permission_integrity, _check_event_payment_integrity


class TestIntegrityChecker:
    """Tests for integrity checker functions"""

    def test_check_integrity_before_deletion_unknown_entity_type(self):
        """Test that unknown entity types raise ValueError"""
        with pytest.raises(ValueError, match="Unknown entity type: unknown"):
            check_integrity_before_deletion('unknown', 1)

    def test_check_integrity_before_deletion_user_calls_correct_function(self):
        """Test that user entity type calls _check_user_integrity"""
        with patch('data.integrity_checker._check_user_integrity') as mock_check:
            mock_check.return_value = None
            result = check_integrity_before_deletion('user', 1)
            mock_check.assert_called_once_with(1)
            assert result is None

    def test_check_integrity_before_deletion_role_calls_correct_function(self):
        """Test that role entity type calls _check_role_integrity"""
        with patch('data.integrity_checker._check_role_integrity') as mock_check:
            mock_check.return_value = None
            result = check_integrity_before_deletion('role', 'admin')
            mock_check.assert_called_once_with('admin')
            assert result is None

    def test_check_integrity_before_deletion_permission_calls_correct_function(self):
        """Test that permission entity type calls _check_permission_integrity"""
        with patch('data.integrity_checker._check_permission_integrity') as mock_check:
            mock_check.return_value = None
            result = check_integrity_before_deletion('permission', 'read')
            mock_check.assert_called_once_with('read')
            assert result is None

    def test_check_integrity_before_deletion_event_payment_calls_correct_function(self):
        """Test that event_payment entity type calls _check_event_payment_integrity"""
        with patch('data.integrity_checker._check_event_payment_integrity') as mock_check:
            mock_check.return_value = None
            result = check_integrity_before_deletion('event_payment', 1)
            mock_check.assert_called_once_with(1)
            assert result is None

    # TODO: Add more tests for _check_event_payment_integrity once implemented