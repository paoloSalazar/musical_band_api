"""
Email configuration module.
Loads SMTP settings from environment variables.
"""
import os
from functools import lru_cache
from pydantic import BaseModel


class EmailConfig(BaseModel):
    """Email configuration settings."""
    smtp_host: str
    smtp_port: int
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_name: str
    smtp_from_email: str
    use_tls: bool = False


@lru_cache()
def get_email_config() -> EmailConfig:
    """Get email configuration from environment variables."""
    return EmailConfig(
        smtp_host=os.getenv("SMTP_HOST", "localhost"),
        smtp_port=int(os.getenv("SMTP_PORT", "1025")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_from_name=os.getenv("SMTP_FROM_NAME", "Musical Band API"),
        smtp_from_email=os.getenv("SMTP_FROM_EMAIL", "noreply@musicalband.local"),
    )
