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

### Authorization Constraints Implementation
#### Overview:
Implemented specific role-based access control for musician availability endpoints as per business requirements.

#### Authorization Rules:
1. **Role Access Control**:
   - Only users with roles `musician`, `auxiliar_musician`, or `admin` can access musician availability endpoints
   - Other roles (e.g., `user`) are blocked at the FastAPI dependency level with 403 Forbidden

2. **Data Ownership Rules**:
   - **Admin users**: Can view and manage ALL musicians' availabilities regardless of ownership
   - **Musician and auxiliar_musician users**: Can only view and manage their OWN availabilities
   - Ownership is validated by matching `current_user.id` with `musician_id` in requests

3. **Admin-Only Endpoints**:
   - `GET /api/admin/musician-availability/date/{date}` requires admin role
   - Returns availability data for all musicians on the specified date

#### Implementation Details:
- **Web Layer**: Added `RoleChecker(allowed_roles=["musician", "auxiliar_musician", "admin"])` to all regular endpoints
- **Service Layer**: Updated authorization logic to treat `auxiliar_musician` role identically to `musician` role for ownership checks
- **Error Handling**: Clear error messages for unauthorized access attempts
- **Testing**: Comprehensive test coverage for all authorization scenarios

#### Security Impact:
- Prevents unauthorized users from accessing sensitive musician scheduling data
- Ensures musicians can only manage their own availability
- Maintains admin oversight capabilities for system management
- Blocks access at the API level before reaching business logic

### Monthly Availability Endpoint Implementation
#### Overview
This sub-phase adds an endpoint to retrieve musician availability dates by month, enabling calendar views and scheduling interfaces to display unavailable dates for a given musician.

#### Tasks:
1. **Update Data Layer** (`data/musician_availability.py`):
   - Add `get_musician_availability_by_month(musician_id, year, month)` function
   - Query unavailable dates within the specified month range
   - Return list of dates for calendar integration

2. **Update Service Layer** (`services/musician_availability.py`):
   - Add business logic for monthly availability retrieval
   - Include authorization checks (own availability or admin access)
   - Format dates appropriately for API response

3. **Update Web Layer** (`web/musician_availability.py`):
   - Add `GET /api/musicians/{musician_id}/availability/month/{year}/{month}` endpoint
   - Validate year/month parameters (valid ranges, future dates)
   - Return availability data with proper HTTP status codes

4. **Update Schemas** (`schemas/musician_availability.py`):
   - Add `MusicianAvailabilityMonthlyResponse` schema
   - Include month/year metadata and list of unavailable dates

5. **Add Tests**:
   - Unit tests for data/service layer functions
   - Integration tests for the new endpoint
   - Test authorization rules and parameter validation

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

### Sub-Phase 3.13: Payment Validation Improvements
#### Overview
This sub-phase addresses missing validations for musician payments to ensure proper business logic and data integrity.

#### Current State
✅ **Already implemented:**
- Check if musician is assigned to event (via `event_musician` table)
- Validate individual payment amount doesn't exceed musician's salary

✅ **Successfully implemented validations:**
- **Cumulative payment validation**: Total payments for musician-event don't exceed salary
- **Payment type business logic validation**: Proper rules for ADVANCE, REMAINING, TOTAL payments
- **Payment status updates**: Automatic updates to `event_musician` table
- **TOTAL payment equality**: TOTAL payments must equal full salary amount
- **ADVANCE payment limit**: ADVANCE payments cannot exceed 50% of salary

#### Tasks Completed:
1. **✅ Add Cumulative Payment Validation** in `services/musician_event_payment.py`:
   - Calculate total existing payments for musician-event combination
   - Validate that new payment + existing payments don't exceed salary
   - Uses existing data layer function: `get_total_paid_by_musician_for_event(event_id, musician_id)`

2. **✅ Add Payment Type Business Logic Validation**:
   - **ADVANCE**: ≤ 50% of salary AND ≤ remaining salary after existing payments
   - **REMAINING**: ≤ remaining salary after existing advances
   - **TOTAL**: Must = full salary amount AND no previous partial payments exist
   - Comprehensive validation logic with specific error messages

3. **✅ Update Payment Status in EventMusician Table**:
   - Automatic `payment_status` updates based on total paid vs salary
   - **PENDING**: 0 payments made
   - **PARTIAL**: Some payments but < full salary
   - **COMPLETED**: Total paid ≥ full salary
   - Added data layer function: `update_payment_status(event_id, musician_id, status)`

4. **✅ Update Data Layer Functions**:
   - `data/musician_event_payment.py`: Used existing functions for payment calculations
   - `data/event_musician.py`: Added `update_payment_status()` function

5. **✅ Update Tests** in `tests/unit/services/test_musician_event_payment.py`:
   - Added 5 comprehensive test cases covering all validation scenarios
   - Tests for cumulative validation, 50% advance limit, TOTAL payment rules, and status updates
   - Updated existing tests to match new validation logic
   - All 16 service tests + 12 schema tests passing

6. **✅ Update API Documentation** in `endpoints.rest`:
   - Added validation rules and limits to payment examples
   - Clear notes about 50% advance limit and TOTAL payment requirements

#### Implementation Results:
✅ **All validations successfully implemented using TDD approach**
✅ **28 total tests passing** (16 service + 12 schema tests)
✅ **Zero breaking changes** - only restricts invalid operations
✅ **Comprehensive error messages** with specific amounts and context
✅ **Automatic payment status tracking** for better visibility

#### Key Business Rules Enforced:
| Payment Type | Validation Rules |
|-------------|------------------|
| **ADVANCE** | ≤ 50% of salary AND ≤ remaining salary |
| **REMAINING** | ≤ remaining salary after advances |
| **TOTAL** | = full salary AND no existing partial payments |
| **All Types** | Positive amounts, musician assigned, cumulative limits |

#### Error Message Examples:
- `"ADVANCE payment cannot exceed 50% of salary. Maximum advance: 500.00, Requested amount: 600.00, Salary: 1000.00"`
- `"TOTAL payment must equal the full salary amount. Expected: 1000.00, Got: 800.00"`
- `"REMAINING payment would exceed remaining salary. Already paid: 500.00, Payment amount: 600.00, Salary: 1000.00"`

#### Risk Assessment:
- **Breaking changes**: None - adding validations only restricts invalid operations
- **Performance**: Minimal impact - additional DB queries are optimized
- **Backward compatibility**: Maintained - existing valid payments still work
- **Data integrity**: Enhanced - prevents overpayments and invalid payment combinations

#### Actual Time Spent: 1 day (completed)
#### Dependencies: Sub-Phase 3.11 complete

### Sub-Phase 3.14: Date-Based Payment Timing Validations
#### Overview
This sub-phase implements date-based restrictions for payment timing to ensure payments are made at appropriate stages of the event lifecycle.

#### Business Requirements

| Payment Type | Timing Rules | Business Logic |
|-------------|--------------|----------------|
| **ADVANCE** | ❌ **Before** event start date only | Help musicians with upfront costs/preparation |
| **REMAINING** | ✅ **On/after** event end date only | Payment after work is completed |
| **TOTAL** | ✅ **On/after** event end date only | Full settlement after event completion |

#### Current State
❌ **Missing validations:**
- ADVANCE payments allowed anytime before event
- TOTAL/REMAINING payments allowed anytime after event start

#### Tasks:
1. **Add Date-Based Validation Logic** in `services/musician_event_payment.py`:
   - Fetch event start_datetime and end_datetime
   - Compare current time against event dates
   - Apply different rules for ADVANCE vs TOTAL/REMAINING payments
   - Provide clear error messages with specific dates

2. **Payment Type Timing Rules**:
   - **ADVANCE**: `current_time < event.start_datetime`
   - **REMAINING/TOTAL**: `current_time >= event.end_datetime`
   - All times compared in UTC timezone

3. **Add Comprehensive Test Cases** in `tests/unit/services/test_musician_event_payment.py`:
   - `test_create_musician_payment_advance_after_event_start` - Should fail
   - `test_create_musician_payment_advance_before_event_start` - Should succeed
   - `test_create_musician_payment_remaining_before_event_end` - Should fail
   - `test_create_musician_payment_remaining_after_event_end` - Should succeed
   - `test_create_musician_payment_total_before_event_end` - Should fail
   - `test_create_musician_payment_total_after_event_end` - Should succeed
   - `test_create_musician_payment_total_on_event_end_date` - Should succeed

4. **Update API Documentation** in `endpoints.rest`:
   - Add timing restrictions to payment examples
   - Update comments to clarify date requirements
   - Include notes about payment windows

5. **Integration Testing**:
   - End-to-end scenarios with event date manipulation
   - Edge cases around exact start/end times
   - Timezone handling verification

#### Error Message Examples:
- **ADVANCE Too Late:**
  ```
  "ADVANCE payments can only be made before event start date.
  Event starts: 2026-05-01T20:00:00+00:00, Current time: 2026-05-01T21:00:00+00:00"
  ```

- **REMAINING/TOTAL Too Early:**
  ```
  "REMAINING payments can only be made on or after event end date.
  Event ends: 2026-05-02T02:00:00+00:00, Current time: 2026-05-01T22:00:00+00:00"
  ```

#### Implementation Order:
1. Add date validation logic to service layer
2. Write comprehensive test cases
3. Update API documentation
4. Integration testing

#### Risk Assessment:
- **Breaking changes**: Low - only adds restrictions on payment timing
- **Existing payments**: Unaffected - only validates new payment creation
- **Business impact**: May require process changes for payment scheduling
- **Performance**: Minimal - reuses existing event data fetch

#### Estimated Time: 1.75 days
#### Dependencies: Sub-Phase 3.13 complete

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