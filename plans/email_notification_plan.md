# Email Notification System Plan

## Overview
This plan outlines the steps to implement an email notification system using Docker containers for sending confirmation emails when users register or update their profiles.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI App                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ User Service│  │ Email Module│  │ Email Config           │  │
│  │             │──│             │──│ (SMTP settings)        │  │
│  │ - create()  │  │ - send()    │  │ - host, port, user    │  │
│  │ - modify()  │  │ - templates │  │ - from_address        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
            │                                  │
            ▼                                  ▼
┌─────────────────────┐            ┌─────────────────────────┐
│   PostgreSQL DB     │            │     MailHog (Docker)    │
│                     │            │                         │
│   - users table    │            │   - SMTP: 1025           │
│                     │            │   - Web UI: 8025        │
└─────────────────────┘            └─────────────────────────┘
```

## Step-by-Step Implementation Plan

### Step 1: Set up MailHog in Docker

MailHog is a development email server that catches emails locally. It provides:
- SMTP server on port 1025
- Web UI on port 8025 to view caught emails
- No actual email delivery (perfect for development/testing)

Create or update `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: postgres_db
    restart: always
    env_file:
      - .env
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mailhog:
    image: mailhog/mailhog
    container_name: mailhog
    ports:
      - "1025:1025"  # SMTP server
      - "8025:8025"  # Web UI
    environment:
      - MH_HOSTNAME=mailhog
    restart: unless_stopped

volumes:
  postgres_data:
```

### Step 2: Add Email Configuration

Update `.env` file with SMTP settings:

```env
# Database
DATABASE_URL=postgresql+pg8000://paolo:PaoloSid6189*@localhost:5432/musical_band_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Email Configuration (MailHog - Development)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_NAME=Musical Band API
SMTP_FROM_EMAIL=noreply@musicalband.local
```

### Step 3: Create Email Configuration Module

Create `config/email_config.py`:

```python
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
```

### Step 4: Create Email Service Module

Create `services/email.py`:

```python
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


# Email template functions
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
```

### Step 5: Update Requirements

Add email dependencies to `requirements.txt`:

```
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
aiosmtplib==3.0.1
pyyaml==6.0.1
pg8000==1.31.2
pytest==8.0.0
httpx==0.26.0
```

### Step 6: Integrate Email into User Service

Modify `services/user.py` to send emails after registration and profile updates:

1. Import the email service:
```python
from services.email import send_registration_confirmation, send_profile_update_notification
```

2. In `create()` function (after user creation):
```python
# Send registration confirmation email (non-blocking)
try:
    await send_registration_confirmation(
        email=user_create.email,
        name=user_create.name,
        lastname=user_create.lastname
    )
except Exception as e:
    logger.warning(f"Failed to send registration email: {str(e)}")
    # Don't fail user creation if email fails
```

3. In `modify_by_id()` function (after profile update):
```python
# Determine which fields were updated
updated_fields = []
if user_update.name is not None and user_update.name != existing_user.name:
    updated_fields.append("name")
if user_update.lastname is not None and user_update.lastname != existing_user.lastname:
    updated_fields.append("lastname")
if user_update.phone_number is not None:
    updated_fields.append("phone_number")

# Send profile update notification
if updated_fields:
    try:
        await send_profile_update_notification(
            email=existing_user.email,
            name=modified_db_user.name,
            lastname=modified_db_user.lastname,
            updated_fields=updated_fields
        )
    except Exception as e:
        logger.warning(f"Failed to send profile update email: {str(e)}")
```

### Step 7: Run Docker Containers

```bash
# Start all containers (database + mailhog)
cd db_conf
docker-compose up -d

# Or from project root
docker-compose -f db_conf/docker-compose.yml up -d

# View MailHog web interface
# Open http://localhost:8025 in browser
```

### Step 8: Test the Flow

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Register a new user:
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jon",
    "lastname": "Doe",
    "email": "jon.doe@example.com",
    "password": "securepassword123",
    "role_id": 1
  }'
```

3. Check MailHog web interface at http://localhost:8025 to see the confirmation email

## Production Considerations

For production deployment, consider:

1. **Use a real email service**:
   - Mailgun (mailgun.com)
   - SendGrid (sendgrid.com)
   - AWS SES (aws.amazon.com/ses)

2. **Update docker-compose for production**:
   ```yaml
   services:
     app:
       build: .
       # ... existing config
       environment:
         - SMTP_HOST=smtp.mailgun.org
         - SMTP_PORT=587
         - SMTP_USER=postmaster@yourdomain.mailgun.org
         - SMTP_PASSWORD=your-api-key
         - SMTP_FROM_NAME=Musical Band API
         - SMTP_FROM_EMAIL=noreply@yourdomain.com
   ```

3. **Add email validation**:
   - Validate email format on registration
   - Add email verification flow with confirmation tokens

4. **Add email templates**:
   - Store templates in separate files
   - Support internationalization (i18n)

5. **Add retry logic**:
   - Implement exponential backoff for failed emails
   - Queue emails for retry

## Summary

| Component | Description |
|-----------|-------------|
| MailHog | Development SMTP server (Docker) |
| config/email_config.py | SMTP configuration loader |
| services/email.py | Email sending service + templates |
| services/user.py | Integration with user operations |
| .env | SMTP environment variables |

This plan provides a complete email notification system that will send confirmation emails to `jon.doe@example.com` when they register or update their profile.
