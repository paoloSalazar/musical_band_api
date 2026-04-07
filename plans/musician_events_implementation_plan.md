# Detailed Implementation Plan for Musician Events Feature

## Overview
This plan outlines a comprehensive implementation of the musician events feature, extending the existing event payment system to track individual musicians participating in events, their roles, salaries, payment statuses, and availability. The feature includes validation to prevent scheduling conflicts with musician unavailability. The implementation follows the established project patterns and architecture.

## Project Architecture Context
- **Models Layer**: SQLAlchemy models in `models/`
- **Schemas Layer**: Pydantic validation in `schemas/`
- **Web Layer**: FastAPI endpoints in `web/`
- **Services Layer**: Business logic in `services/`
- **Data Layer**: Database operations in `data/`
- **Tests**: TDD approach with unit tests in `tests/unit/`
- **Auth**: JWT-based with role-based permissions

## Phase 1: Musician Availability Feature
### Sub-Phase 1.1: Testing Models
#### Tasks:
1. Write unit tests for MusicianAvailability model: `tests/unit/models/test_musician_availability.py`
   - Test model instantiation, relationships, validations

#### Estimated Time: 0.25 days
#### Dependencies: None

### Sub-Phase 1.2: Models
#### Tasks:
1. Create `models/musician_availability.py`:
   - MusicianAvailability model
   - Table Definition:
     - id: Integer, Primary Key, Auto Increment
     - musician_id: Integer, Foreign Key to users.id, Not Null
     - unavailable_date: Date, Not Null
     - reason: String(255), Nullable
     - created_at: DateTime, Not Null, Default CURRENT_TIMESTAMP
     - updated_at: DateTime, Not Null, Default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   - Relationships: Many-to-One with User (musician_id -> User.id)
   - Validation for date fields (unavailable_date >= today)

2. Update `models/__init__.py` to import new models

3. Update `conftest.py` to register new models with SQLAlchemy

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 1.1 complete

### Sub-Phase 1.3: Database Schema Updates
#### Tasks:
1. Generate Alembic migrations using `alembic revision --autogenerate`

2. Review the generated migrations for accuracy

3. Run migrations and verify schema integrity

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 1.2 complete

### Sub-Phase 1.4: Testing Schemas
#### Tasks:
1. Write unit tests for schemas: `tests/unit/schemas/test_musician_availability.py`
   - Test schema validations, serialization

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 1.2 complete

### Sub-Phase 1.5: Schemas
#### Tasks:
1. Create `schemas/musician_availability.py`:
   - MusicianAvailabilityBase, MusicianAvailabilityCreate, MusicianAvailabilityUpdate, MusicianAvailabilityResponse
   - Date validation for unavailable_date (cannot be in the past)
   - Optional reason field

2. Create composite schemas:
   - MusicianAvailabilitySummaryResponse (for availability queries)

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 1.4 complete

### Sub-Phase 1.6: Testing Data Layer
#### Tasks:
1. Write unit tests for data layer: `tests/unit/data/test_musician_availability.py`
   - Test CRUD operations, queries

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 1.5 complete

### Sub-Phase 1.7: Data Layer
#### Tasks:
1. Create `data/musician_availability.py`:
   - CRUD functions for musician availability
   - Functions to get availability by musician, check date conflicts
   - Bulk insert/update for multiple dates
   - Query functions for availability checking

#### Estimated Time: 1 day
#### Dependencies: Sub-Phase 1.6 complete

### Sub-Phase 1.8: Testing Services Layer
#### Tasks:
1. Write unit tests for services: `tests/unit/services/test_musician_availability.py`
   - Test business logic functions

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 1.7 complete

### Sub-Phase 1.9: Services Layer
#### Tasks:
1. Create `services/musician_availability.py`:
   - Business logic for availability management
   - Functions to validate availability conflicts
   - Authorization rules: Only musicians can set their own availability; admins can view all

#### Estimated Time: 1 day
#### Dependencies: Sub-Phase 1.8 complete

### Sub-Phase 1.10: Testing Web Layer
#### Tasks:
1. Write unit tests for web layer: `tests/unit/web/test_musician_availability.py`
   - Test API endpoints, auth, and authorization rules

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 1.9 complete

### Sub-Phase 1.11: Web Layer
#### Tasks:
1. Create `web/musician_availability.py`:
   - POST `/api/musicians/{musician_id}/availability` - Add unavailable date(s) (only for musician roles, own availability)
   - GET `/api/musicians/{musician_id}/availability` - Get musician availability (own or admin)
   - DELETE `/api/musicians/{musician_id}/availability/{date}` - Remove unavailable date (own or admin)
   - GET `/api/musicians/availability?date={date}` - Check availability for all musicians on date (admin only)

2. Update `main.py` to include new routers

3. Add authentication/authorization checks:
   - Musicians can manage their own availability; only musician roles can set unavailability
   - Users can see only their own unavailable dates; admins can see all
   - Require appropriate permissions (e.g., "musician-availability:manage")

#### Estimated Time: 1 day
#### Dependencies: Sub-Phase 1.10 complete

### Sub-Phase 1.12: Integration Testing
#### Tasks:
1. Write and run integration tests for availability feature
   - Full availability management workflows
   - Authorization rules: musicians set own availability, visibility restrictions
   - End-to-end scenarios

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 1.11 complete

## Phase 2: Event Musician Feature
### Sub-Phase 2.1: Testing Models
#### Tasks:
1. Write unit tests for EventMusician model: `tests/unit/models/test_event_musician.py`
   - Test model instantiation, relationships, validations

#### Estimated Time: 0.25 days
#### Dependencies: Phase 1 complete

### Sub-Phase 2.2: Models
#### Tasks:
1. Create `models/event_musician.py`:
   - EventMusician model with SQLAlchemy fields matching the schema
   - Table Definition:
     - id: Integer, Primary Key, Auto Increment
     - event_id: Integer, Foreign Key to events.id, Not Null
     - musician_id: Integer, Foreign Key to users.id, Not Null
     - role: String(100), Nullable
     - salary: Decimal(10,2), Not Null
     - payment_status: Enum('PENDING', 'COMPLETED', 'PARTIAL'), Not Null, Default 'PENDING'
     - created_at: DateTime, Not Null, Default CURRENT_TIMESTAMP
     - updated_at: DateTime, Not Null, Default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   - Relationships: Many-to-One with Event (event_id -> Event.id), Many-to-One with User (musician_id -> User.id)
   - Enum for payment_status (PENDING, COMPLETED, PARTIAL)
   - Type hints and validation (salary > 0)

2. Update `models/__init__.py` to import new models

3. Update `conftest.py` to register new models with SQLAlchemy

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 2.1 complete

### Sub-Phase 2.3: Database Schema Updates
#### Tasks:
1. Generate Alembic migrations using `alembic revision --autogenerate`

2. Review the generated migrations for accuracy

3. Run migrations and verify schema integrity

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 2.2 complete

### Sub-Phase 2.4: Testing Schemas
#### Tasks:
1. Write unit tests for schemas: `tests/unit/schemas/test_event_musician.py`
   - Test schema validations, serialization

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 2.2 complete

### Sub-Phase 2.5: Schemas
#### Tasks:
1. Create `schemas/event_musician.py`:
   - EventMusicianBase, EventMusicianCreate, EventMusicianUpdate, EventMusicianResponse
   - Validation for salary (positive decimal), role (optional string)
   - PaymentStatus enum matching model

2. Create composite schemas:
   - EventWithMusiciansResponse (extend existing EventResponse)
   - MusicianSummaryResponse (for listing musicians per event)

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 2.4 complete

### Sub-Phase 2.6: Testing Data Layer
#### Tasks:
1. Write unit tests for data layer: `tests/unit/data/test_event_musician.py`
   - Test CRUD operations, queries

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 2.5 complete

### Sub-Phase 2.7: Data Layer
#### Tasks:
1. Create `data/event_musician.py`:
   - CRUD functions: create, get_by_event, get_by_musician, update, delete
   - Functions to check if musician is assigned to event
   - Bulk operations for event musician management

#### Estimated Time: 1 day
#### Dependencies: Sub-Phase 2.6 complete

### Sub-Phase 2.8: Testing Services Layer
#### Tasks:
1. Write unit tests for services: `tests/unit/services/test_event_musician.py`
   - Test business logic functions, including availability validation

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 2.7 complete, Phase 1 complete

### Sub-Phase 2.9: Services Layer
#### Tasks:
1. Create `services/event_musician.py`:
   - Business logic for musician assignment
   - Availability conflict validation during assignment

#### Estimated Time: 1 day
#### Dependencies: Sub-Phase 2.8 complete

### Sub-Phase 2.10: Testing Web Layer
#### Tasks:
1. Write unit tests for web layer: `tests/unit/web/test_event_musician.py`
   - Test API endpoints, auth

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 2.9 complete

### Sub-Phase 2.11: Web Layer
#### Tasks:
1. Create `web/event_musician.py`:
   - POST `/api/events/{event_id}/musicians` - Assign musician (with availability validation)
   - GET `/api/events/{event_id}/musicians` - List musicians for event
   - PATCH `/api/events/{event_id}/musicians/{musician_id}` - Update role/salary
   - DELETE `/api/events/{event_id}/musicians/{musician_id}` - Remove musician
   - GET `/api/events/{event_id}/musicians/summary` - Musician costs summary

2. Update `main.py` to include new routers

3. Add authentication/authorization checks:
   - Require appropriate permissions (e.g., "events:manage-musicians")
   - Validate user can only manage events they own or have admin access

#### Estimated Time: 1 day
#### Dependencies: Sub-Phase 2.10 complete

### Sub-Phase 2.12: Integration Testing
#### Tasks:
1. Write and run integration tests for event musician feature
   - Full musician assignment workflows with availability validation
   - End-to-end scenarios

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 2.11 complete

## Phase 3: Musician Event Payment Feature
### Sub-Phase 3.1: Testing Models
#### Tasks:
1. Write unit tests for MusicianEventPayment model: `tests/unit/models/test_musician_event_payment.py`
   - Test model instantiation, relationships, validations

#### Estimated Time: 0.25 days
#### Dependencies: Phase 2 complete

### Sub-Phase 3.2: Models
#### Tasks:
1. Create `models/musician_event_payment.py`:
   - MusicianEventPayment model
   - Table Definition:
     - id: Integer, Primary Key, Auto Increment
     - event_id: Integer, Foreign Key to events.id, Not Null
     - musician_id: Integer, Foreign Key to users.id, Not Null
     - payment_type: Enum('ADVANCE', 'REMAINING', 'TOTAL'), Not Null
     - amount: Decimal(10,2), Not Null
     - payment_date: DateTime, Not Null
     - notes: String(500), Nullable
     - created_at: DateTime, Not Null, Default CURRENT_TIMESTAMP
     - updated_at: DateTime, Not Null, Default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   - PaymentType enum (ADVANCE, REMAINING, TOTAL) - reuse existing if possible
   - Relationships: Many-to-One with Event (event_id -> Event.id), Many-to-One with User (musician_id -> User.id)
   - Timestamps

2. Update `models/__init__.py` to import new models

3. Update `conftest.py` to register new models with SQLAlchemy

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 3.1 complete

### Sub-Phase 3.3: Database Schema Updates
#### Tasks:
1. Generate Alembic migrations using `alembic revision --autogenerate`

2. Review the generated migrations for accuracy

3. Run migrations and verify schema integrity

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 3.2 complete

### Sub-Phase 3.4: Testing Schemas
#### Tasks:
1. Write unit tests for schemas: `tests/unit/schemas/test_musician_event_payment.py`
   - Test schema validations, serialization

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 3.2 complete

### Sub-Phase 3.5: Schemas
#### Tasks:
1. Create `schemas/musician_event_payment.py`:
   - MusicianEventPaymentBase, MusicianEventPaymentCreate, MusicianEventPaymentResponse
   - PaymentType enum (reuse from existing event_payment if compatible)
   - Amount validation

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 3.4 complete

### Sub-Phase 3.6: Testing Data Layer
#### Tasks:
1. Write unit tests for data layer: `tests/unit/data/test_musician_event_payment.py`
   - Test CRUD operations, queries

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 3.5 complete

### Sub-Phase 3.7: Data Layer
#### Tasks:
1. Create `data/musician_event_payment.py`:
   - CRUD functions for musician payments
   - Functions to get payments by event/musician, calculate totals
   - Payment status update functions

2. Update existing `data/event_payment.py` if needed to handle musician-specific logic

#### Estimated Time: 1 day
#### Dependencies: Sub-Phase 3.6 complete

### Sub-Phase 3.8: Testing Services Layer
#### Tasks:
1. Write unit tests for services: `tests/unit/services/test_musician_event_payment.py`
   - Test business logic functions

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 3.7 complete

### Sub-Phase 3.9: Services Layer
#### Tasks:
1. Create `services/musician_event_payment.py`:
   - Business logic for payment management
   - Payment calculation and status updates

#### Estimated Time: 1 day
#### Dependencies: Sub-Phase 3.8 complete

### Sub-Phase 3.10: Testing Web Layer
#### Tasks:
1. Write unit tests for web layer: `tests/unit/web/test_musician_event_payment.py`
   - Test API endpoints, auth

#### Estimated Time: 0.25 days
#### Dependencies: Sub-Phase 3.9 complete

### Sub-Phase 3.11: Web Layer
#### Tasks:
1. Create `web/musician_event_payment.py`:
   - POST `/api/events/{event_id}/musicians/{musician_id}/payments` - Add payment
   - GET `/api/events/{event_id}/musicians/{musician_id}/payments` - List payments
   - GET `/api/events/{event_id}/musicians/{musician_id}/payments/summary` - Payment summary

2. Update `web/event_payment.py`:
   - Modify summary endpoint to include musician payment breakdown

3. Update `main.py` to include new routers

4. Add authentication/authorization checks:
   - Require appropriate permissions (e.g., "musician-payments:manage")

#### Estimated Time: 1 day
#### Dependencies: Sub-Phase 3.10 complete

### Sub-Phase 3.12: Integration Testing
#### Tasks:
1. Write and run integration tests for musician event payment feature
   - Full payment tracking workflows
   - End-to-end scenarios

#### Estimated Time: 0.5 days
#### Dependencies: Sub-Phase 3.11 complete

## Phase 4: Integration and Deployment
### Tasks:
1. Update user role system:
   - Ensure "musician" role exists in seed data
   - Update role permissions to include musician management and availability

2. Update permission system:
   - Add permissions like "musicians:read", "musicians:write", "musician-payments:manage", "musician-availability:manage"

3. Update documentation:
   - Add new endpoints to `endpoints.rest`
   - Update API docs in `docs/API_ENDPOINTS.md`
   - Document availability conflict validation rules

4. Frontend integration considerations:
   - Event management UI should display musician assignments and availability
   - Payment interfaces should show breakdown by musician
   - Calendar views should indicate musician availability

5. Run full test suite and linting

6. Deploy to staging and test end-to-end workflows:
   - Musician assignment with availability checks
   - Availability management
   - Payment tracking

7. Monitor and fix any issues post-deployment

### Estimated Time: 2-3 days
### Dependencies: All phases complete

## Risk Mitigation
- **Database**: Backup before migrations, test migrations on dev environment
- **Backward Compatibility**: Ensure existing event payment functionality unaffected
- **Performance**: Add appropriate indexes, monitor query performance
- **Security**: Validate all input, ensure proper authorization
- **Data Integrity**: Use transactions for multi-table operations

## Success Criteria
- Musicians can be assigned to events with roles and salaries, with availability conflict validation
- Musician availability can be tracked and managed
- Payment tracking per musician works correctly
- Event payment summaries include musician breakdowns
- Assignment validation prevents conflicts with unavailable dates
- All existing functionality remains intact
- Comprehensive test coverage (>90%)
- API documentation updated
- Performance meets requirements

## Timeline Summary
- **Phase 1**: 6 days (Musician Availability)
- **Phase 2**: 6 days (Event Musician)
- **Phase 3**: 6 days (Musician Event Payment)
- **Phase 4**: 2-3 days (Integration)
- **Total**: 20-21 days (depending on team size and complexity)

## Team Requirements
- Backend Developer: 1-2 developers
- Database Administrator: For migration reviews
- QA Engineer: For testing and validation
- DevOps: For deployment support