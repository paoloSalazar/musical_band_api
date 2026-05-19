"""Tests for event endpoints in web layer (TDD for musician filtering)."""

from unittest.mock import MagicMock, patch
from datetime import datetime
import web.event as event_web


class TestEventWebMusicianFiltering:
    """TDD tests for role-based filtering in web layer"""

    @patch('web.event.event_service.get_paginated')
    def test_get_all_passes_role_from_current_user(self, mock_service):
        """GET / should extract role/user_id from token and pass to service"""
        mock_service.return_value = MagicMock(items=[], total=0, page=1, limit=20, total_pages=0)

        # Simulate current_user payload from get_current_user
        current_user = {"sub": "musician@example.com", "role": "musician", "user_id": 5}

        # Call the endpoint function directly
        result = event_web.get_all(
            current_user=current_user,
            page=1, limit=20,
            status=None, search=None, user_id=None,
            start_after=None, end_before=None,
            sort_by="created_at", order="desc"
        )

        mock_service.assert_called_once_with(
            page=1, limit=20, status=None, search=None, user_id=None,
            start_after=None, end_before=None, sort_by="created_at", order="desc",
            current_user_role="musician", current_user_id=5
        )

    @patch('web.event.event_service.get_by_month')
    def test_get_calendar_passes_role_from_current_user(self, mock_service):
        """Calendar endpoint must also forward musician role"""
        mock_service.return_value = []

        current_user = {"sub": "aux@example.com", "role": "auxiliar_musician", "user_id": 7}

        event_web.get_calendar(
            current_user=current_user,
            year=2026, month=5,
            user_id=None
        )

        mock_service.assert_called_once_with(
            2026, 5, None,
            current_user_role="auxiliar_musician", current_user_id=7
        )
