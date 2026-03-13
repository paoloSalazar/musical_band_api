"""
Email service for sending notifications.
"""
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.email_config import get_email_config

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str = ""
) -> bool:
    """
    Send an email to the specified recipient.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body_html: HTML body content
        body_text: Plain text body (fallback)
    
    Returns:
        True if email was sent successfully
    """
    config = get_email_config()
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{config.smtp_from_name} <{config.smtp_from_email}>"
    message["To"] = to_email
    
    # Add plain text part
    if body_text:
        text_part = MIMEText(body_text, "plain")
        message.attach(text_part)
    
    # Add HTML part
    html_part = MIMEText(body_html, "html")
    message.attach(html_part)
    
    try:
        await aiosmtplib.send(
            message,
            hostname=config.smtp_host,
            port=config.smtp_port,
            username=config.smtp_user,
            password=config.smtp_password,
            use_tls=config.use_tls,
        )
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def send_registration_confirmation(
    email: str,
    name: str,
    lastname: str
) -> bool:
    """Send registration confirmation email."""
    subject = "Welcome to Musical Band API - Registration Confirmed"
    
    body_html = f"""
    <html>
    <body>
        <h1>Welcome, {name} {lastname}!</h1>
        <p>Your account has been successfully created.</p>
        <p>You can now log in to the Musical Band API using your email: <strong>{email}</strong></p>
        <p>If you have any questions, please contact support.</p>
        <br>
        <p>Best regards,<br>The Musical Band API Team</p>
    </body>
    </html>
    """
    
    body_text = f"""
    Welcome, {name} {lastname}!
    
    Your account has been successfully created.
    You can now log in to the Musical Band API using your email: {email}
    
    If you have any questions, please contact support.
    
    Best regards,
    The Musical Band API Team
    """
    
    return await send_email(email, subject, body_html, body_text)


async def send_profile_update_notification(
    email: str,
    name: str,
    lastname: str,
    updated_fields: list[str]
) -> bool:
    """Send profile update notification email."""
    subject = "Musical Band API - Profile Updated"
    
    fields_list = ", ".join(updated_fields)
    
    body_html = f"""
    <html>
    <body>
        <h1>Profile Updated</h1>
        <p>Hello {name} {lastname},</p>
        <p>Your profile has been successfully updated.</p>
        <p>The following fields were modified: <strong>{fields_list}</strong></p>
        <p>If you did not make this change, please contact support immediately.</p>
        <br>
        <p>Best regards,<br>The Musical Band API Team</p>
    </body>
    </html>
    """
    
    body_text = f"""
    Profile Updated
    
    Hello {name} {lastname},
    
    Your profile has been successfully updated.
    The following fields were modified: {fields_list}
    
    If you did not make this change, please contact support immediately.
    
    Best regards,
    The Musical Band API Team
    """
    
    return await send_email(email, subject, body_html, body_text)
