# Musical Band API

A FastAPI project to handle musical band administration using layered architecture.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up PostgreSQL database:
   - Start the database with Docker Compose: `cd db_conf && docker-compose up -d`
   - Or set up manually and configure `DATABASE_URL` in `.env`

3. Run the application:
   ```bash
   python main.py
   ```

## API Endpoints

- `GET /api/user-roles/` - Get all user roles
- `GET /api/user-roles/{name}` - Get user role by name
- `POST /api/user-roles/` - Create a new user role
- `PATCH /api/user-roles/` - Modify an existing user role
- `PUT /api/user-roles/` - Replace an existing user role
- `DELETE /api/user-roles/{name}` - Delete a user role

## Architecture

- **model/**: Pydantic models
- **data/**: Database access layer
- **service/**: Business logic
- **web/**: API routes
