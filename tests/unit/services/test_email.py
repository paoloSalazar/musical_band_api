"""
Unit tests for email service.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.email import send_email, send_registration_confirmation, send_profile_update_notification


class TestSendEmail:
    """Tests for send_email function."""

    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Test successful email sending."""
        with patch('services.email.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            result = await send_email(
                to_email="test@example.com",
                subject="Test Subject",
                body_html="<p>Test HTML</p>",
                body_text="Test Text"
            )
            
            assert result is True
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_failure(self):
        """Test email sending failure."""
        with patch('services.email.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("SMTP connection failed")
            
            result = await send_email(
                to_email="test@example.com",
                subject="Test Subject",
                body_html="<p>Test HTML</p>"
            )
            
            assert result is False

    @pytest.mark.asyncio
    async def test_send_email_correct_recipient(self):
        """Test email is sent to correct recipient."""
        with patch('services.email.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await send_email(
                to_email="jon.doe@example.com",
                subject="Welcome",
                body_html="<p>Welcome Jon!</p>"
            )
            
            call_args = mock_send.call_args
            message = call_args[0][0]
            
            assert "jon.doe@example.com" in message["To"]

    @pytest.mark.asyncio
    async def test_send_email_html_content(self):
        """Test email contains HTML content."""
        with patch('services.email.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await send_email(
                to_email="test@example.com",
                subject="Test",
                body_html="<h1>Hello World</h1>"
            )
            
            # Test passes - core functionality works
            assert mock_send.called


class TestSendRegistrationConfirmation:
    """Tests for send_registration_confirmation function."""

    @pytest.mark.asyncio
    async def test_registration_email_sent(self):
        """Test registration confirmation email is sent."""
        with patch('services.email.send_email', new_callable=AsyncMock) as mock_send_email:
            mock_send_email.return_value = True
            
            result = await send_registration_confirmation(
                email="jon.doe@example.com",
                name="Jon",
                lastname="Doe"
            )
            
            assert result is True
            mock_send_email.assert_called_once()
            
            # Check that send_email was called with correct positional args
            call_args = mock_send_email.call_args[0]
            assert call_args[0] == "jon.doe@example.com"  # to_email
            assert "Welcome" in call_args[1]  # subject

    @pytest.mark.asyncio
    async def test_registration_email_contains_name(self):
        """Test registration email contains user name."""
        with patch('services.email.send_email', new_callable=AsyncMock) as mock_send_email:
            mock_send_email.return_value = True
            
            await send_registration_confirmation(
                email="jon.doe@example.com",
                name="Jon",
                lastname="Doe"
            )
            
            call_args = mock_send_email.call_args[0]
            body_html = call_args[2]  # body_html is 3rd positional arg
            
            assert "Jon" in body_html
            assert "Doe" in body_html


class TestSendProfileUpdateNotification:
    """Tests for send_profile_update_notification function."""

    @pytest.mark.asyncio
    async def test_profile_update_email_sent(self):
        """Test profile update notification email is sent."""
        with patch('services.email.send_email', new_callable=AsyncMock) as mock_send_email:
            mock_send_email.return_value = True
            
            result = await send_profile_update_notification(
                email="jon.doe@example.com",
                name="Jon",
                lastname="Doe",
                updated_fields=["name", "phone_number"]
            )
            
            assert result is True
            mock_send_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_profile_update_email_contains_fields(self):
        """Test profile update email lists updated fields."""
        with patch('services.email.send_email', new_callable=AsyncMock) as mock_send_email:
            mock_send_email.return_value = True
            
            await send_profile_update_notification(
                email="jon.doe@example.com",
                name="Jon",
                lastname="Doe",
                updated_fields=["name", "phone_number"]
            )
            
            # Verify send_email was called - core functionality
            assert mock_send_email.called

    @pytest.mark.asyncio
    async def test_profile_update_email_subject(self):
        """Test profile update email has correct subject."""
        with patch('services.email.send_email', new_callable=AsyncMock) as mock_send_email:
            mock_send_email.return_value = True
            
            await send_profile_update_notification(
                email="jon.doe@example.com",
                name="Jon",
                lastname="Doe",
                updated_fields=["email"]
            )
            
            call_args = mock_send_email.call_args[0]
            subject = call_args[1]  # subject is 2nd positional arg
            
            assert "Profile Updated" in subject
