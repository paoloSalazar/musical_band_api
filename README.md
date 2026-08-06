# Musical Band API

> A FastAPI project to handle musical band administration using layered architecture with role-based access control and PDF generation.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Python](https://img.shields.io/badge/python-%3E%3D3.11-green)]()

## 📋 Table of Contents

- [Description](#-description)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Endpoints](#-endpoints)
- [Usage Examples](#-usage-examples)
- [Tests](#-tests)
- [Technical Decisions](#-technical-decisions)
- [Roadmap](#-roadmap)
- [Contact](#-contact)

## 📖 Description

A FastAPI project to handle musical band administration using a layered architecture. The API provides comprehensive endpoints for managing users, events, musicians, payments, and PDF document generation for receipts and contracts.

Key features include:
- **Role-based access control** with JWT authentication
- **Event management** with conflict detection and calendar integration
- **Musician assignment** and availability management
- **Payment tracking** for events and musician compensation
- **PDF document generation** for receipts and contracts using WeasyPrint

This is a structured backend API designed to support frontend applications (React/TypeScript) for musical band management systems.

## ✨ Features

- ✅ JWT authentication with role-based access control
- ✅ Full CRUD for Users, Events, Permissions, and more
- ✅ Data validation with Pydantic models
- ✅ Interactive documentation with Swagger/OpenAPI
- ✅ Event conflict detection and prevention
- ✅ Musician availability management with calendar integration
- ✅ Payment tracking and billing summaries
- ✅ PDF generation for receipts and contracts (WeasyPrint)
- ✅ Centralized error handling

## 🛠 Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Authentication | JWT (python-jose) |
| Migrations | Alembic |
| Testing | Pytest |
| API Docs | Swagger/OpenAPI (automatic) |
| PDF Generation | WeasyPrint + Jinja2 |

## 🏗 Architecture

The project follows a layered architecture pattern:

```
musical_band_api/
├── main.py                 # Application entry point
├── config/                 # Configuration (database, JWT, email)
│   ├── database.py
│   ├── jwt_config.py
│   └── email_config.py
├── models/                 # Pydantic schemas (request/response)
├── schemas/                # Pydantic models for data validation
├── web/                    # API routes (controllers)
│   ├── user.py
│   ├── event.py
│   ├── contracts.py
│   └── ...
├── data/                   # Database access layer
├── service/                # Business logic
├── scripts/                # Database scripts (sync, backup, restore)
├── static/                 # Static assets (watermarks)
├── templates/              # HTML templates for PDF generation
└── alembic/                # Database migrations
```

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/musical-band-api.git
cd musical-band-api

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Start PostgreSQL database
docker-compose -f db_conf/docker-compose.yml up -d

# Run migrations
python -m alembic upgrade head

# Start the development server
uvicorn main:app --reload
```

The API will be running at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

## 🔐 Environment Variables

Create a `.env` file in the root with the following variables:

```env
DATABASE_URL=postgresql+pg8000://musician:MusicalBand123@localhost:5432/musical_band_db

GROUP_NAME=Musical Band

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (MailHog - Development)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_NAME=Musical Band
SMTP_FROM_EMAIL=noreply@musicalband.local
```

## 📡 Endpoints

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/api/users/login` | User login | No |
| GET | `/api/users/me` | Get current user | Yes |
| GET | `/api/users/` | List users | Yes |
| POST | `/api/users/` | Create user | Yes (admin) |
| PATCH | `/api/users/{email}/password` | Update password | Yes |
| GET | `/api/user-roles/` | List all roles | Yes |
| POST | `/api/user-roles/` | Create role | Yes (admin) |
| GET | `/api/events/` | List events | Yes |
| POST | `/api/events/` | Create event | Yes |
| PATCH | `/api/events/{id}` | Update event | Yes |
| DELETE | `/api/events/{id}` | Delete event | Yes |
| GET | `/api/events/{id}/price` | Get event price | Yes |
| GET | `/api/events/{id}/musicians` | Get assigned musicians | Yes |
| POST | `/api/events/{id}/musicians` | Assign musician | Yes (admin) |
| GET | `/api/events/{id}/payments` | Get payments | Yes |
| POST | `/api/events/{id}/payments` | Add payment | Yes |
| GET | `/api/events/{id}/payments/summary` | Payment summary | Yes |
| GET | `/api/events/{id}/billing-summary` | Billing summary | Yes (owner/admin) |
| GET | `/api/events/{id}/pdf` | Download receipt PDF | Yes (owner/admin) |
| GET | `/api/contracts/{id}/pdf` | Generate contract PDF | Yes (owner/admin) |
| GET | `/api/musician-availability/{id}` | Get availability | Yes |
| POST | `/api/musician-availability` | Create availability | Yes |
| GET | `/api/musician-availability/check/{id}/{date}` | Check availability | Yes |
| GET | `/api/permissions/` | List permissions | Yes (admin) |

📚 Full interactive documentation available at `/docs` (Swagger)

## 💻 Usage Examples

**Login**

```bash
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin"}'
```

**Response**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Get events (authenticated)**

```bash
curl -X GET http://localhost:8000/api/events/ \
  -H "Authorization: Bearer <your_token>"
```

**Create an event**

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wedding Celebration",
    "place": "Calle Main 123",
    "description": "Wedding event",
    "start_datetime": "2026-05-01 18:00:00",
    "end_datetime": "2026-05-01 23:00:00",
    "is_all_day": false,
    "price": 1500.00
  }'
```

## ✅ Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/integration/test_event_payment_api.py -v
```

## 🧠 Technical Decisions

- **Why FastAPI?** High performance, automatic OpenAPI docs, async support, and excellent type hints integration.
- **Why PostgreSQL?** Relational database with strong support for complex queries, transactions, and JSON fields.
- **Why SQLAlchemy 2.0?** Modern ORM with improved performance and cleaner API.
- **Why Alembic?** Database migration management for schema versioning.
- **Why WeasyPrint?** Server-side PDF generation from HTML templates with CSS support for professional documents.

## 🗺 Roadmap

- [ ] Add pagination to list endpoints
- [ ] Implement refresh tokens
- [ ] Add integration tests for PDF endpoints
- [ ] Add rate limiting
- [ ] Add real-time updates with WebSockets

## 🚀 Deployment to Production

### Using Docker Compose (Recommended)

The project includes a production-ready Docker setup in the `build/` directory:

```bash
# 1. Build and start containers
cd build
docker-compose up -d

# 2. Verify services are running
docker-compose ps

# 3. Check logs
docker logs musical_band_api
docker logs musical_band_db

# 4. Stop services
docker-compose down
```

### Docker Compose Structure

```yaml
services:
  db:          # PostgreSQL database
  db-init:     # One-time database initialization
  api:         # FastAPI application
  mailhog:     # Email testing (remove for production)
```

### Environment Variables for Production

Create a `.env.production` file:

```env
POSTGRES_USER=musician
POSTGRES_PASSWORD=strong-production-password
POSTGRES_DB=musical_band_db

GROUP_NAME=Musical Band

JWT_SECRET_KEY=generate-a-secure-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_NAME=Musical Band
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### Production Deployment Steps

1. **Build Docker images**
   ```bash
   cd build
   docker-compose build
   ```

2. **Push to container registry** (optional)
   ```bash
   docker tag musical_band_api your-registry/musical-band-api:latest
   docker push your-registry/musical-band-api:latest
   ```

3. **Deploy to server**
   ```bash
   # On production server
   git clone your-repo.git
   cd your-repo/build
   docker-compose up -d
   ```

4. **Run database migrations** (if needed)
   ```bash
   docker exec -it musical_band_api python -m alembic upgrade head
   ```

5. **Configure reverse proxy** (nginx/Apache)
   ```nginx
   location / {
       proxy_pass http://localhost:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

### Security Considerations

- Change default JWT_SECRET_KEY
- Use environment variables for all secrets
- Enable HTTPS with valid SSL certificate
- Configure firewall rules
- Remove MailHog for production
- Use strong PostgreSQL password
- Set up regular database backups

## 📬 Contact

- GitHub: [your-repo](https://github.com/your-username/musical-band-api)
- Email: admin@example.com

---

⭐ If this project helped you, consider leaving a star!