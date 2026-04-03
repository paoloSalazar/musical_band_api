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

## Phase 1: Database Schema Updates
### Tasks:
1. Create Alembic migration for `event_musicians` table:
   ```sql
   CREATE TABLE public.event_musicians (
       id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
       event_id bigint NOT NULL REFERENCES public.events(id),
       musician_id bigint NOT NULL REFERENCES public.users(id),
       role text,
       payment_status text DEFAULT 'PENDING',
       salary numeric NOT NULL,
       created_at timestamp with time zone DEFAULT now() NOT NULL,
       updated_at timestamp with time zone DEFAULT now() NOT NULL
   );
   ```
   - Add unique constraint on (event_id, musician_id) to prevent duplicates
   - Add indexes on event_id and musician_id for performance

2. Create Alembic migration for `musician_event_payments` table:
   ```sql
   CREATE TABLE public.musician_event_payments (
       id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
       event_id bigint NOT NULL REFERENCES public.events(id),
       user_id bigint NOT NULL REFERENCES public.users(id),
       payment_date timestamp with time zone DEFAULT now() NOT NULL,
       amount numeric NOT NULL,
       payment_type text NOT NULL,
       created_at timestamp with time zone DEFAULT now() NOT NULL,
       updated_at timestamp with time zone DEFAULT now() NOT NULL
   );
   ```
   - Add foreign key constraints
   - Add indexes for performance

3. Create Alembic migration for `musician_availability` table:
   ```sql
   CREATE TABLE public.musician_availability (
       id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
       musician_id bigint NOT NULL REFERENCES public.users(id),
       unavailable_date date NOT NULL,
       reason text,
       created_at timestamp with time zone DEFAULT now() NOT NULL,
       updated_at timestamp with time zone DEFAULT now() NOT NULL
   );
   ```
   - Add unique constraint on (musician_id, unavailable_date) to prevent duplicate dates
   - Add index on musician_id for performance
   - Add index on unavailable_date for availability queries

4. Update existing `event_payment` table if needed (add musician-specific fields if extending)

5. Run migrations and verify schema integrity

### Estimated Time: 2-3 days
### Dependencies: None

## Phase 2: Model Updates
### Tasks:
1. Create `models/event_musician.py`:
   - EventMusician model with SQLAlchemy fields matching database schema
   - Relationships: Many-to-One with Event and User
   - Enum for payment_status (PENDING, COMPLETED, etc.)
   - Type hints and validation

2. Create `models/musician_event_payment.py`:
   - MusicianEventPayment model
   - PaymentType enum (ADVANCE, REMAINING, TOTAL) - reuse existing if possible
   - Relationships with Event and User
   - Timestamps

3. Create `models/musician_availability.py`:
   - MusicianAvailability model
   - Fields: id, musician_id, unavailable_date, reason, created_at, updated_at
   - Relationships: Many-to-One with User
   - Validation for date fields

4. Update `models/__init__.py` to import new models

5. Update `conftest.py` to register new models with SQLAlchemy

### Estimated Time: 1-2 days
### Dependencies: Phase 1 complete

## Phase 3: Schema Updates
### Tasks:
1. Create `schemas/event_musician.py`:
   - EventMusicianBase, EventMusicianCreate, EventMusicianUpdate, EventMusicianResponse
   - Validation for salary (positive decimal), role (optional string)
   - PaymentStatus enum matching model

2. Create `schemas/musician_event_payment.py`:
   - MusicianEventPaymentBase, MusicianEventPaymentCreate, MusicianEventPaymentResponse
   - PaymentType enum (reuse from existing event_payment if compatible)
   - Amount validation

3. Create `schemas/musician_availability.py`:
   - MusicianAvailabilityBase, MusicianAvailabilityCreate, MusicianAvailabilityUpdate, MusicianAvailabilityResponse
   - Date validation for unavailable_date (cannot be in the past)
   - Optional reason field

4. Create composite schemas:
   - EventWithMusiciansResponse (extend existing EventResponse)
   - MusicianSummaryResponse (for listing musicians per event)
   - MusicianAvailabilitySummaryResponse (for availability queries)

### Estimated Time: 1 day
### Dependencies: Phase 2 complete

## Phase 4: Data Layer Implementation
### Tasks:
1. Create `data/event_musician.py`:
   - CRUD functions: create, get_by_event, get_by_musician, update, delete
   - Functions to check if musician is assigned to event
   - Bulk operations for event musician management

2. Create `data/musician_event_payment.py`:
   - CRUD functions for musician payments
   - Functions to get payments by event/musician, calculate totals
   - Payment status update functions

3. Create `data/musician_availability.py`:
   - CRUD functions for musician availability
   - Functions to get availability by musician, check date conflicts
   - Bulk insert/update for multiple dates
   - Query functions for availability checking

4. Update existing `data/event_payment.py` if needed to handle musician-specific logic

### Estimated Time: 2-3 days
### Dependencies: Phase 2, Phase 3 complete

## Phase 5: Services Layer Implementation
### Tasks:
1. Create `services/event_musician.py`:
   - assign_musician_to_event(): Validate user has musician role, check conflicts, validate availability
   - update_musician_role(): Change role/salary for assigned musician
   - remove_musician_from_event(): Handle payment implications
   - get_musicians_for_event(): List with payment summaries
   - validate_musician_assignment(): Business rules (musician role required, availability check)

2. Create `services/musician_availability.py`:
   - add_unavailable_date(): Add musician unavailability
   - remove_unavailable_date(): Remove specific unavailable date
   - get_musician_availability(): Get all unavailable dates for a musician
   - check_availability_conflict(): Check if musician is available on a specific date
   - bulk_update_availability(): Handle multiple dates

3. Create `services/musician_event_payment.py`:
   - create_musician_payment(): Validation against musician salary
   - get_musician_payment_summary(): Total paid vs salary
   - update_payment_status(): Mark payments as completed
   - validate_payment_amount(): Ensure doesn't exceed musician's salary balance
   - calculate_remaining_salary(): For partial payments

4. Update `services/event_payment.py`:
   - Integrate musician payment totals into event payment summaries
   - Add validation to ensure event payments cover musician salaries

### Estimated Time: 3-4 days
### Dependencies: Phase 4 complete

## Phase 6: Web Layer Implementation
### Tasks:
1. Create `web/event_musician.py`:
   - POST `/api/events/{event_id}/musicians` - Assign musician (with availability validation)
   - GET `/api/events/{event_id}/musicians` - List musicians for event
   - PATCH `/api/events/{event_id}/musicians/{musician_id}` - Update role/salary
   - DELETE `/api/events/{event_id}/musicians/{musician_id}` - Remove musician
   - GET `/api/events/{event_id}/musicians/summary` - Musician costs summary

2. Create `web/musician_availability.py`:
   - POST `/api/musicians/{musician_id}/availability` - Add unavailable date(s)
   - GET `/api/musicians/{musician_id}/availability` - Get musician availability
   - DELETE `/api/musicians/{musician_id}/availability/{date}` - Remove unavailable date
   - GET `/api/musicians/availability?date={date}` - Check availability for all musicians on date

3. Create `web/musician_event_payment.py`:
   - POST `/api/events/{event_id}/musicians/{musician_id}/payments` - Add payment
   - GET `/api/events/{event_id}/musicians/{musician_id}/payments` - List payments
   - GET `/api/events/{event_id}/musicians/{musician_id}/payments/summary` - Payment summary

4. Update `web/event_payment.py`:
   - Modify summary endpoint to include musician payment breakdown

5. Update `main.py` to include new routers

6. Add authentication/authorization checks:
   - Require appropriate permissions (e.g., "events:manage-musicians", "musicians:manage-availability")
   - Validate user can only manage events they own or have admin access
   - Musicians can manage their own availability

### Estimated Time: 4-5 days
### Dependencies: Phase 5 complete

## Phase 7: Testing Implementation
### Tasks:
1. Unit tests for models:
   - `tests/unit/models/test_event_musician.py`
   - `tests/unit/models/test_musician_event_payment.py`
   - `tests/unit/models/test_musician_availability.py`

2. Unit tests for schemas:
   - `tests/unit/schemas/test_event_musician.py`
   - `tests/unit/schemas/test_musician_event_payment.py`
   - `tests/unit/schemas/test_musician_availability.py`

3. Unit tests for data layer:
   - `tests/unit/data/test_event_musician.py`
   - `tests/unit/data/test_musician_event_payment.py`
   - `tests/unit/data/test_musician_availability.py`

4. Unit tests for services:
   - `tests/unit/services/test_event_musician.py`
   - `tests/unit/services/test_musician_event_payment.py`
   - `tests/unit/services/test_musician_availability.py`

5. Unit tests for web layer:
   - `tests/unit/web/test_event_musician.py`
   - `tests/unit/web/test_musician_event_payment.py`
   - `tests/unit/web/test_musician_availability.py`

6. Integration tests:
   - Full musician assignment and payment workflow
   - Availability conflict validation during assignment
   - Edge cases: duplicate assignments, payment validations, past date availability

### Estimated Time: 4-5 days
### Dependencies: All previous phases complete

## Phase 8: Integration and Deployment
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
### Dependencies: Phase 7 complete

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
- **Phase 1**: 2-3 days (Database)
- **Phase 2**: 1-2 days (Models)
- **Phase 3**: 1 day (Schemas)
- **Phase 4**: 2-3 days (Data Layer)
- **Phase 5**: 3-4 days (Services)
- **Phase 6**: 4-5 days (Web Layer)
- **Phase 7**: 4-5 days (Testing)
- **Phase 8**: 2-3 days (Integration)
- **Total**: 19-26 days (depending on team size and complexity)

## Team Requirements
- Backend Developer: 1-2 developers
- Database Administrator: For migration reviews
- QA Engineer: For testing and validation
- DevOps: For deployment support