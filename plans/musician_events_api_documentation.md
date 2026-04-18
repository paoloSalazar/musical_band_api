# Musician Events API Documentation

This document provides comprehensive API documentation for the musician events feature, including endpoint specifications, request/response examples, constraints, and business rules. This is intended for UI project integration.

## Overview

The musician events feature extends the existing event payment system to track individual musicians participating in events, their roles, salaries, payment statuses, and availability. It includes validation to prevent scheduling conflicts.

**Current Implementation Status**: All core features implemented and tested. Recent improvements include performance optimizations, enhanced error handling, and refined access controls for payment endpoints.

## Authentication & Authorization

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### User Roles
- **admin**: Full access to all features
- **musician**: Can manage their own availability and view/manage their own payments
- **auxiliar_musician**: Same as musician role (can manage their own availability and payments)

**Note**: This feature separates read and write permissions:
- **Read access**: Musicians can view assignments and their own data
- **Write access**: Only administrators can create, update, or delete assignments

## API Base URL
```
http://localhost:8000/api
```

---

## 1. Musician Availability Endpoints

### 1.1 Get Musician Availability
**Endpoint:** `GET /musician-availability/{musician_id}`

**Authorization:** Admin, Musician (own only), Auxiliar Musician (own only)

**Description:** Retrieve all future unavailable dates for a specific musician. **Performance optimized** to only return availabilities with dates >= today.

**URL Example:**
```
GET /api/musician-availability/6
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "musician_id": 6,
    "unavailable_date": "2026-04-22",
    "reason": "Holiday trip",
    "created_at": "2026-04-15T10:30:00",
    "updated_at": "2026-04-15T10:30:00"
  },
  {
    "id": 2,
    "musician_id": 6,
    "unavailable_date": "2026-04-23",
    "reason": "Family vacation",
    "created_at": "2026-04-15T10:30:00",
    "updated_at": "2026-04-15T10:30:00"
  }
]
```

**Constraints:**
- **Performance**: Only returns dates >= today (future availability) - filters out past dates at database level
- Musicians can only view their own availability
- Admins can view any musician's availability

**Recent Changes:**
- **Performance Improvement**: Added database-level filtering to exclude past availabilities, improving query performance

**Error Responses:**
- `403 Forbidden`: Unauthorized access
- `500 Internal Server Error`: Database error

### 1.2 Check Musician Availability
**Endpoint:** `GET /musician-availability/check/{musician_id}/{date}`

**Authorization:** Admin, Musician, Auxiliar Musician

**Description:** Check if a musician is available on a specific date.

**URL Example:**
```
GET /api/musician-availability/check/5/2026-04-15
```

**Response (200 OK):**
```json
true
```

**Response Examples:**
- `true`: Musician is available
- `false`: Musician is unavailable

### 1.3 Create Musician Availability
**Endpoint:** `POST /musician-availability`

**Authorization:** Admin, Musician (own only), Auxiliar Musician (own only)

**Description:** Create a new unavailable date entry for a musician.

**URL Example:**
```
POST /api/musician-availability
```

**Request Body:**
```json
{
  "musician_id": 5,
  "unavailable_date": "2026-04-22",
  "reason": "Holiday trip"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "musician_id": 5,
  "unavailable_date": "2026-04-22",
  "reason": "Holiday trip",
  "created_at": "2026-04-15T11:00:00",
  "updated_at": "2026-04-15T11:00:00"
}
```

**Constraints:**
- `unavailable_date` must be >= today
- Musicians can only create availability for themselves
- Cannot create duplicate availability for same musician/date

**Error Responses:**
- `400 Bad Request`: Past date or validation error
- `403 Forbidden`: Unauthorized access
- `409 Conflict`: Availability already exists
- `500 Internal Server Error`: Database error

### 1.4 Create Bulk Musician Availability
**Endpoint:** `POST /musician-availability/bulk`

**Authorization:** Admin, Musician (own only), Auxiliar Musician (own only)

**Description:** Create multiple unavailable date entries for a musician.

**URL Example:**
```
POST /api/musician-availability/bulk
```

**Request Body:**
```json
[
  {
    "musician_id": 5,
    "unavailable_date": "2026-04-23",
    "reason": "Family vacation"
  },
  {
    "musician_id": 5,
    "unavailable_date": "2026-04-24",
    "reason": "Family vacation"
  }
]
```

**Response (201 Created):**
```json
[
  {
    "id": 4,
    "musician_id": 5,
    "unavailable_date": "2026-04-23",
    "reason": "Family vacation",
    "created_at": "2026-04-15T11:15:00",
    "updated_at": "2026-04-15T11:15:00"
  },
  {
    "id": 5,
    "musician_id": 5,
    "unavailable_date": "2026-04-24",
    "reason": "Family vacation",
    "created_at": "2026-04-15T11:15:00",
    "updated_at": "2026-04-15T11:15:00"
  }
]
```

**Constraints:**
- All entries must be for the same musician
- All dates must be >= today
- No duplicate dates allowed

### 1.5 Update Musician Availability
**Endpoint:** `PATCH /musician-availability/{availability_id}`

**Authorization:** Admin, Musician (own only), Auxiliar Musician (own only)

**Description:** Update an existing availability entry.

**URL Example:**
```
PATCH /api/musician-availability/1
```

**Request Body:**
```json
{
  "unavailable_date": "2026-04-19",
  "reason": "Rescheduled vacation"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "musician_id": 5,
  "unavailable_date": "2026-04-19",
  "reason": "Rescheduled vacation",
  "created_at": "2026-04-15T10:30:00",
  "updated_at": "2026-04-15T11:30:00"
}
```

**Constraints:**
- Updated date must be >= today
- Cannot create conflicts with existing availability

### 1.6 Delete Musician Availability
**Endpoint:** `DELETE /musician-availability/{availability_id}`

**Authorization:** Admin, Musician (own only), Auxiliar Musician (own only)

**Description:** Delete an availability entry.

**URL Example:**
```
DELETE /api/musician-availability/1
```

**Response (200 OK):**
```json
{
  "message": "Availability deleted successfully"
}
```

### 1.7 Delete Musician Availability by Date
**Endpoint:** `DELETE /musician-availability/{musician_id}/{date}`

**Authorization:** Admin, Musician (own only), Auxiliar Musician (own only)

**Description:** Delete availability for a specific musician and date.

**URL Example:**
```
DELETE /api/musician-availability/5/2026-04-18
```

**Response (200 OK):**
```json
{
  "message": "Availability deleted successfully"
}
```

### 1.8 Get All Unavailable Musicians (Admin Only)
**Endpoint:** `GET /admin/musician-availability/date/{date}`

**Authorization:** Admin only

**Description:** Get all musicians unavailable on a specific date.

**URL Example:**
```
GET /api/admin/musician-availability/date/2026-04-21
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "musician_id": 6,
    "unavailable_date": "2026-04-21",
    "reason": "Holiday trip",
    "created_at": "2026-04-15T10:30:00",
    "updated_at": "2026-04-15T10:30:00",
    "musician": {
      "id": 6,
      "name": "John",
      "lastname": "Doe"
    }
  }
]
```

---

## 2. Event Musician Endpoints

### 2.1 Get Musicians Assigned to Event
**Endpoint:** `GET /events/{event_id}/musicians`

**Authorization:** Admin, Musician, Auxiliar Musician

**Description:** Get all musicians assigned to a specific event. Includes musician name and lastname fields for UI convenience. Musicians can view assignments but cannot modify them.

**URL Example:**
```
GET /api/events/3/musicians
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "event_id": 3,
    "musician_id": 5,
    "role": "Pianist",
    "salary": 400.00,
    "payment_status": "PENDING",
    "musician_name": "John",
    "musician_lastname": "Doe",
    "created_at": "2026-04-10T09:00:00",
    "updated_at": "2026-04-10T09:00:00"
  },
  {
    "id": 2,
    "event_id": 3,
    "musician_id": 6,
    "role": "Guitarist",
    "salary": 500.00,
    "payment_status": "PARTIAL",
    "musician_name": "Jane",
    "musician_lastname": "Smith",
    "created_at": "2026-04-10T09:15:00",
    "updated_at": "2026-04-10T09:15:00"
  }
]
```

**Constraints:**
- **Read operations** (GET): Available to admin, musician, and auxiliar_musician roles
- **Write operations** (POST, PATCH, DELETE): Restricted to admin role only
- Musicians can view assignments and their own data but cannot create/modify assignments

### 2.2 Assign Musician to Event
**Endpoint:** `POST /events/{event_id}/musicians`

**Authorization:** Admin only

**Description:** Assign a musician to an event with role and salary.

**URL Example:**
```
POST /api/events/3/musicians
```

**Request Body:**
```json
{
  "event_id": 3,
  "musician_id": 5,
  "role": "Pianist",
  "salary": 400.00
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "event_id": 3,
  "musician_id": 5,
  "role": "Pianist",
  "salary": 400.00,
  "payment_status": "PENDING",
  "created_at": "2026-04-15T12:00:00",
  "updated_at": "2026-04-15T12:00:00"
}
```

**Constraints:**
- Musician must be available on event date (no conflicts)
- Musician cannot be double-assigned to same event
- Salary must be positive decimal
- **Admin-only operation**: Only administrators can assign musicians to events

**Business Rules:**
- Validates musician availability conflicts
- Prevents duplicate assignments

**Error Responses:**
- `400 Bad Request`: Validation error
- `403 Forbidden`: Unauthorized access
- `409 Conflict`: Musician unavailable or already assigned
- `500 Internal Server Error`: Database error

### 2.3 Update Musician Assignment
**Endpoint:** `PATCH /events/{event_id}/musicians/{musician_id}`

**Authorization:** Admin only

**Description:** Update a musician's role and/or salary for an event.

**URL Example:**
```
PATCH /api/events/6/musicians/5
```

**Request Body:**
```json
{
  "role": "Solo Guitarist",
  "salary": 600.00
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "event_id": 6,
  "musician_id": 5,
  "role": "Solo Guitarist",
  "salary": 600.00,
  "payment_status": "PARTIAL",
  "created_at": "2026-04-10T09:00:00",
  "updated_at": "2026-04-15T12:30:00"
}
```

### 2.4 Remove Musician from Event
**Endpoint:** `DELETE /events/{event_id}/musicians/{musician_id}`

**Authorization:** Admin only

**Description:** Remove a musician assignment from an event.

**URL Example:**
```
DELETE /api/events/6/musicians/5
```

**Response (200 OK):**
```json
{
  "message": "Musician removed from event successfully"
}
```

### 2.5 Get Musicians Summary for Event
**Endpoint:** `GET /events/{event_id}/musicians/summary`

**Authorization:** Admin, Musician, Auxiliar Musician

**Description:** Get cost summary of all musicians assigned to an event. Includes individual musician details with names for UI display.

**URL Example:**
```
GET /api/events/6/musicians/summary
```

**Response (200 OK):**
```json
{
  "event_id": 6,
  "total_musicians": 3,
  "total_cost": 1500.00,
  "musicians": [
    {
      "musician_id": 5,
      "musician_name": "John",
      "musician_lastname": "Doe",
      "role": "Guitarist",
      "salary": 500.00,
      "payment_status": "PENDING"
    },
    {
      "musician_id": 6,
      "musician_name": "Jane",
      "musician_lastname": "Smith",
      "role": "Pianist",
      "salary": 600.00,
      "payment_status": "COMPLETED"
    },
    {
      "musician_id": 7,
      "musician_name": "Bob",
      "musician_lastname": "Johnson",
      "role": "Drummer",
      "salary": 400.00,
      "payment_status": "PARTIAL"
    }
  ]
}
```

### 2.6 Get Musician Assignments
**Endpoint:** `GET /events/musicians/{musician_id}/assignments`

**Authorization:** Admin, Musician (own assignments only), Auxiliar Musician (own assignments only)

**Description:** Get all event assignments for a specific musician. Includes musician name fields for consistency.

**URL Example:**
```
GET /api/events/musicians/5/assignments
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "event_id": 1,
    "musician_id": 5,
    "role": "Lead Guitarist",
    "salary": 1500.00,
    "payment_status": "PENDING",
    "musician_name": "John",
    "musician_lastname": "Doe",
    "created_at": "2026-04-11T06:41:09",
    "updated_at": "2026-04-11T06:41:09"
  },
  {
    "id": 2,
    "event_id": 3,
    "musician_id": 5,
    "role": "Pianist",
    "salary": 400.00,
    "payment_status": "COMPLETED",
    "musician_name": "John",
    "musician_lastname": "Doe",
    "created_at": "2026-04-10T09:00:00",
    "updated_at": "2026-04-10T09:00:00"
  }
]
```

---

## 3. Musician Event Payment Endpoints

### 3.1 Add Payment to Musician
**Endpoint:** `POST /events/{event_id}/musicians/{musician_id}/payments`

**Authorization:** Admin, Musician, Auxiliar Musician

**Description:** Add a payment to a specific musician for an event.

**URL Example:**
```
POST /api/events/3/musicians/5/payments
```

**Request Body:**
```json
{
  "event_id": 3,
  "musician_id": 5,
  "amount": 300.00,
  "payment_type": "ADVANCE",
  "payment_date": "2026-04-15T10:00:00",
  "notes": "Advance payment for guitarist"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "event_id": 3,
  "musician_id": 5,
  "amount": 300.00,
  "payment_type": "ADVANCE",
  "payment_date": "2026-04-15T10:00:00",
  "notes": "Advance payment for guitarist",
  "created_at": "2026-04-15T10:00:00",
  "updated_at": "2026-04-15T10:00:00"
}
```

**Payment Types & Rules:**

| Type | Description | Timing | Amount Limits |
|------|-------------|--------|---------------|
| **ADVANCE** | Partial payment before event | Before event start | ≤ 50% of salary |
| **REMAINING** | Balance payment after event | On/after event end | ≤ remaining salary |
| **TOTAL** | Full payment | On/after event end | = full salary amount |

**Constraints:**
- Musician must be assigned to the event
- Payment amount must be positive
- Payment timing must match business rules above
- Cannot exceed cumulative salary limits
- TOTAL payments require no prior partial payments

**Error Responses:**
- `400 Bad Request`: Validation error (timing, amount limits)
- `403 Forbidden`: Unauthorized access
- `404 Not Found`: Event or musician not found
- `409 Conflict`: Business rule violation

### 3.2 Get Payments for Musician in Event
**Endpoint:** `GET /events/{event_id}/musicians/{musician_id}/payments`

**Authorization:** Admin, Musician (own payments only), Auxiliar Musician (own payments only)

**Description:** Get all payments for a specific musician in an event. **Access restricted** to only musician-related roles.

**URL Example:**
```
GET /api/events/3/musicians/5/payments
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "event_id": 3,
    "musician_id": 5,
    "amount": 300.00,
    "payment_type": "ADVANCE",
    "payment_date": "2026-04-15T10:00:00",
    "notes": "Advance payment for guitarist",
    "created_at": "2026-04-15T10:00:00",
    "updated_at": "2026-04-15T10:00:00"
  },
  {
    "id": 2,
    "event_id": 3,
    "musician_id": 5,
    "amount": 700.00,
    "payment_type": "REMAINING",
    "payment_date": "2026-04-16T22:00:00",
    "notes": "Remaining balance payment",
    "created_at": "2026-04-16T22:00:00",
    "updated_at": "2026-04-16T22:00:00"
  }
]
```

**Constraints:**
- **Access Control**: Only users with roles `admin`, `musician`, or `auxiliar_musician` can access
- Musicians can only view their own payments (musician_id must match current user)
- Admins can view all payments

**Recent Changes:**
- **Security Improvement**: Restricted access from regular `user` role to only musician-related roles
- **Authorization Logic**: Added ownership validation for musicians accessing their own payment data

### 3.3 Get Payment Summary for Musician in Event
**Endpoint:** `GET /events/{event_id}/musicians/{musician_id}/payments/summary`

**Authorization:** Admin, Musician (own payments only), Auxiliar Musician (own payments only)

**Description:** Get payment summary for a musician in a specific event. **Access restricted** to only musician-related roles.

**URL Example:**
```
GET /api/events/3/musicians/5/payments/summary
```

**Response (200 OK):**
```json
{
  "musician_id": 5,
  "total_paid": 1000.00,
  "payment_count": 2
}
```

**Constraints:**
- **Access Control**: Only users with roles `admin`, `musician`, or `auxiliar_musician` can access
- Musicians can only view their own payment summaries (musician_id must match current user)
- Admins can view all payment summaries

**Recent Changes:**
- **Security Improvement**: Restricted access from regular `user` role to only musician-related roles
- **Authorization Logic**: Added ownership validation for musicians accessing their own payment data

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `400 Bad Request`: Validation errors, business rule violations
- `403 Forbidden`: Authorization failures
- `404 Not Found`: Resource not found
- `409 Conflict`: Business conflicts (availability, duplicates)
- `422 Unprocessable Entity`: Schema validation errors
- `500 Internal Server Error`: Server/database errors

## Data Types and Validation

### Musician Availability
- `musician_id`: Integer (foreign key to users.id)
- `unavailable_date`: Date (≥ today)
- `reason`: String (optional, max 255 chars)

### Event Musician Assignment
- `event_id`: Integer (foreign key to events.id)
- `musician_id`: Integer (foreign key to users.id)
- `role`: String (optional, max 100 chars)
- `salary`: Decimal (positive, max 10 digits, 2 decimal places)
- `payment_status`: Enum ("PENDING", "PARTIAL", "COMPLETED")
- `musician_name`: String (included in responses for UI convenience)
- `musician_lastname`: String (included in responses for UI convenience)

### Musician Event Payment
- `event_id`: Integer (foreign key to events.id)
- `musician_id`: Integer (foreign key to users.id)
- `amount`: Decimal (positive, max 10 digits, 2 decimal places)
- `payment_type`: Enum ("ADVANCE", "REMAINING", "TOTAL")
- `payment_date`: DateTime (defaults to current time)
- `notes`: String (optional, max 500 chars)

## Recent Improvements & Changes

### Latest Updates (2026-04-17)

1. **Performance Optimization - Availability Filtering**
   - **Endpoint**: `GET /musician-availability/{musician_id}`
   - **Change**: Added database-level filtering to return only future availabilities (unavailable_date >= today)
   - **Impact**: Improved query performance by excluding past dates
   - **Files**: `data/musician_availability.py`, `services/musician_availability.py`

2. **Enhanced Error Handling - Date Validation**
   - **Change**: Moved date validation from Pydantic schema to service layer
   - **Benefit**: Provides consistent, detailed logging for validation errors
   - **Impact**: Better error tracking and debugging capabilities
   - **Files**: `services/musician_availability.py`, `schemas/musician_availability.py`

3. **Security Enhancement - Hierarchical Access Control**
   - **Read Endpoints**: `GET /events/{event_id}/musicians`, `GET /events/{event_id}/musicians/summary`
   - **Change**: Allow admin, musician, and auxiliar_musician roles to view assignments
   - **Write Endpoints**: `POST/PATCH/DELETE /events/{event_id}/musicians`
   - **Change**: Restricted to admin role only for creating/modifying assignments
   - **Removed**: Client/user roles from all endpoints
   - **Impact**: Musicians can view but only admins can manage assignments
   - **Files**: `web/event_musician.py`, `web/musician_event_payment.py`, `services/musician_event_payment.py`

## Business Rules Summary

1. **Availability Management**: Musicians can only set future unavailable dates
2. **Conflict Prevention**: Cannot assign musicians to events on their unavailable dates
3. **Payment Timing**: ADVANCE before event start, REMAINING/TOTAL after event end
4. **Payment Limits**: ADVANCE ≤ 50% salary, REMAINING ≤ remaining balance, TOTAL = full salary
5. **Authorization**: Hierarchical access - musicians can view, admins can manage
6. **Data Integrity**: Prevents overpayments, duplicate assignments, invalid combinations
7. **Performance**: Database-level filtering for availability queries
8. **Security**: All endpoints require musician-related role authentication
9. **UI Convenience**: API responses include musician name fields to reduce additional API calls

## Integration Notes for UI Project

- All endpoints require JWT authentication
- Handle both successful responses and error responses appropriately
- Use appropriate HTTP status codes for UI feedback
- Consider caching availability data for performance
- Implement proper error handling for network failures
- Validate input data on frontend before API calls
- Use pagination for large result sets if implemented in future

## Version History

### v1.1.0 (2026-04-17)
- **Performance**: Added database filtering for future availability queries
- **Error Handling**: Moved date validation to service layer for better logging
- **Security**: Implemented hierarchical access control
  - Read operations: Admin, musician, auxiliar_musician roles
  - Write operations: Admin role only
- **Authorization**: Musicians can view assignments, only admins can manage them

### v1.0.0 (2026-04-16)
- Initial release with full musician events functionality
- Musician availability management
- Event musician assignments with conflict prevention
- Individual musician payment tracking with business rules