# Docker Environment Plan for Musical Band API

## Overview

Create a Docker environment with two containers connected via a shared network:
1. PostgreSQL database container with initial data restored
2. FastAPI application container

## Current State

- Project uses FastAPI with SQLAlchemy and Alembic for migrations
- Existing `db_conf/docker-compose.yml` has PostgreSQL + MailHog setup
- `scripts/sync_database.py` orchestrates: clear → migrate → restore workflow
- `scripts/backup_data_20260629_InitialState.sql` contains initial data

## Architecture

```
+------------------+         +------------------+
|  db_container    |         |  api_container   |
|  (PostgreSQL)    |<------->|  (FastAPI)       |
|  musical_band_db   |  network|  uvicorn server  |
+------------------+         +------------------+
         |                              |
         v                              v
   postgres_data                     app code
   volume                       requirements.txt
```

## Directory Structure (Docker-related files)

```
musical_band_api/
├── build/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   └── backup_data_20260629_InitialState.sql
├── static/
│   └── watermark.png       # For PDF watermark
├── templates/
│   ├── receipt.html
│   └── contract.html
├── .env.docker             # Template file (NOT COMMITTED)
└── .gitignore              # Added .env.docker to ignore
```

**Note:** Log files are persisted in Docker's `app_logs` volume, accessible via `docker exec` or volume inspection.

**Note:** `.env.docker` is placed at root level for easy access by docker-compose when running from root.

## Container 1: Database (PostgreSQL)

### Image
- `postgres:15-alpine` (already used in existing setup)

### Configuration
- **Environment Variables from `.env` (via env_file):**
  - `POSTGRES_USER` (from .env)
  - `POSTGRES_PASSWORD` (from .env)
  - `POSTGRES_DB` (from .env)
- **Create `.env.docker`** template with placeholders for sensitive values

### Initialization Strategy
**Important:** The backup SQL contains only INSERT statements (data), not CREATE TABLE. The sync_database.py workflow handles this:
1. `clear_database.py` - drops existing tables
2. `alembic upgrade head` - creates schema via migrations
3. `restore_data.py` - inserts data from backup

For Docker, recommend creating a dedicated init service:

```yaml
  db-init:
    build:
      context: ..
      dockerfile: build/Dockerfile
    depends_on:
      db:
        condition: service_healthy
    command: ["python", "scripts/sync_database.py", "scripts/backup_data_20260629_InitialState.sql", "--force"]
    env_file:
      - ../.env.docker
    environment:
      DATABASE_URL: postgresql+pg8000://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    networks:
      - musical_band_network
    volumes:
      - ..:/app
    restart: "no"
```

This init service runs once to set up the database, then exits.

### Volume
- `postgres_data:/var/lib/postgresql/data` (persistent data)

## Container 2: FastAPI Application

### Image
- Python 3.11-slim (or match project's Python version)

### Dependencies
- Install from `requirements.txt`
- Copy project source code

### Configuration
- **Environment Variables from `.env.docker` (via env_file):**
  - `DATABASE_URL` (constructed from POSTGRES_USER/PASSWORD/DB)
  - `JWT_SECRET_KEY`
  - `JWT_ALGORITHM`
  - `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
  - `SMTP_HOST=mailhog` (overridden for container)
  - `SMTP_PORT`
  - `GROUP_NAME`

### Entry Point
```
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Docker Compose Structure

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: musical_band_db
    env_file:
      - ../.env.docker  # At root level
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - musical_band_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  db-init:
    build:
      context: ..
      dockerfile: build/Dockerfile
    depends_on:
      db:
        condition: service_healthy
    command: ["python", "scripts/sync_database.py", "scripts/backup_data_20260629_InitialState.sql", "--force"]
    env_file:
      - ../.env.docker
    environment:
      DATABASE_URL: postgresql+pg8000://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    networks:
      - musical_band_network
    volumes:
      - ..:/app
    restart: "no"

  api:
    build:
      context: ..
      dockerfile: build/Dockerfile
    container_name: musical_band_api
    depends_on:
      db-init:
        condition: service_completed_successfully
    env_file:
      - ../.env.docker
    environment:
      DATABASE_URL: postgresql+pg8000://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      SMTP_HOST: mailhog
    ports:
      - "8000:8000"
    volumes:
      - app_logs:/app/logs  # Named volume for log persistence
    networks:
      - musical_band_network

  mailhog:
    image: mailhog/mailhog
    container_name: mailhog
    ports:
      - "1025:1025"
      - "8025:8025"
    networks:
      - musical_band_network

volumes:
  postgres_data:
  app_logs:

networks:
  musical_band_network:
    driver: bridge
```

## Files to Create

1. **build/Dockerfile**
   - Base image: `python:3.11-slim`
   - Install system dependencies for WeasyPrint (PDF generation):
     - `libpango-1.0-0`, `libpangoft2-1.0-0`, `libpangocairo-1.0-0` (for Pango text rendering)
     - `libffi-dev`, `shared-mime-info`, `gdk-pixbuf`, `cairo` (for WeasyPrint)
     - `postgresql-client`, `libpq-dev` (for psql and psycopg)
   - Install Python dependencies: `pip install -r requirements.txt`
   - Set working directory: `/app`
   - Copy source code from parent directory

2. **.env.docker** (at project root - NOT in build folder)
   - Template derived from `dot_env_example` plus POSTGRES credentials
   - **DO NOT COMMIT** - add to `.gitignore`

3. **build/docker-compose.yml**
   - Full docker-compose configuration with relative paths to parent
   - Run from `build/` directory: `docker-compose up -d`

## Implementation Steps

1. **Create .env.docker template** (at project root)
    - Copy from `dot_env_example`
    - Add POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB (use values from `db_conf/.env` - already updated with `musician` / `P@ssW0rD88!`)

2. **Create build/Dockerfile**
    - Base image: `python:3.11-slim`
    - Install apt packages for WeasyPrint:
      ```
      libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0
      libffi-dev shared-mime-info gdk-pixbuf libcogl23
      postgresql-client postgresql libpq-dev
      ```
    - Install Python packages: `pip install -r requirements.txt`
    - Set working directory: `/app`
    - Copy source code

3. **Create build/docker-compose.yml**
   - Reference parent directory (`..`) for build context and source files
   - Use `../.env.docker` for sensitive values
   - Configure network and dependencies

4. **Update .gitignore**
    - Add `.env.docker` to prevent committing secrets (note: `.env` is already ignored)

5. **Test Deploy**
    - Fill in values in `.env.docker`
    - Run from `build/` directory: `docker-compose up -d`
    - Or run from root: `docker-compose -f build/docker-compose.yml up -d`

## Notes

- The backup SQL contains INSERT statements only (no schema) - requires migrations first
- `db-init` service runs the sync_database.py workflow to set up schema and data
- `db-init` exits after completion (`restart: "no"`), then API starts
- API container depends on `db-init` completing successfully
- For re-initialization: `docker-compose -f build/docker-compose.yml down -v` to remove volumes (or run from build/ directory)
- MailHog is included for email testing (ports 1025/8025)
- Credentials are NOT hardcoded - read from `.env.docker` via `env_file`
- `.env.docker` should be in `.gitignore` - use as template only
- `app_logs` named volume persists logs across container restarts (view via `docker exec` or volume inspect)
- WeasyPrint requires Pango/Cairo system libs - included in Dockerfile dependencies
- `static/` and `templates/` directories are available in container for PDF generation
- **Note:** Backup data was dumped as `paolo` owner - this doesn't affect data import; connection user is `musician`

## Dockerfile Notes

- The Dockerfile creates `/app/logs` directory for WeasyPrint/PDF and logging
- `app_logs` named volume persists logs at Docker level (view via `docker exec -it musical_band_api cat /app/logs/logs.txt`)
- WeasyPrint requires Pango and Cairo libraries - install these system packages for PDF generation to work

## Security Consideration

- Create `.env.docker` as a template file
- Add actual `.env.docker` values to `.gitignore`
- Consider using Docker secrets or environment variables for production

## Prerequisites

- No host directories needed for logs - using named volume `app_logs`

## .env.docker Template Example

```env
# PostgreSQL Configuration (for Docker)
POSTGRES_USER=musician
POSTGRES_PASSWORD=P@ssW0rD88!
POSTGRES_DB=musical_band_db

# Application Configuration
GROUP_NAME=Musical Band

# JWT Configuration
JWT_SECRET_KEY=change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (MailHog - Development)
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_NAME=Musical Band
SMTP_FROM_EMAIL=noreply@musicalband.local
```