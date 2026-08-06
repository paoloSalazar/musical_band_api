# Musician Payment Summary Endpoints Implementation Plan

## Overview
This plan outlines the implementation of two new API endpoints to provide payment summary information:
1. Musician payment summary per event
2. Event billing summary

These endpoints will provide detailed financial information for event management and reporting purposes.

## Endpoints to Implement

### 1. Musician Payment Summary Per Event
**Endpoint:** `GET /api/events/{event_id}/musicians/payment-summary`
**Description:** Retrieve payment summary for all musicians assigned to a specific event
**Response:** List of objects containing:
- `musician_name`: Full name of the musician
- `salary`: Musician's salary for the event
- `payment_done`: Total amount paid to musician
- `remaining_payment`: Remaining amount to be paid to musician

### 2. Event Billing Summary
**Endpoint:** `GET /api/events/{event_id}/billing-summary`
**Description:** Retrieve billing summary for a specific event
**Response:** Object containing:
- `event_name`: Name of the event
- `payment_done`: Total amount paid for the event
- `remaining_payment`: Remaining amount to be paid
- `payment_done_to_musicians`: Total amount paid to musicians

## Implementation Details

### Database Layer
Add new function to `data/musician_event_payment.py`:
- `get_total_paid_by_event_for_musicians(event_id)`: Calculates total amount paid to all musicians for a specific event

### Service Layer
Add new functions to `services/musician_event_payment.py`:
- `get_musician_payment_summary_for_event(event_id, current_user)`: Returns payment summary for all musicians in an event
- `get_event_billing_summary(event_id, current_user)`: Returns billing summary for an event

### API Layer
Add new endpoints to `web/musician_event_payment.py`:
- `GET /api/events/{event_id}/musicians/payment-summary` with proper authorization and response modeling
- `GET /api/events/{event_id}/billing-summary` with proper authorization and response modeling

### Schema Updates
Add new response schemas to `schemas/musician_event_payment.py`:
- `MusicianEventSummaryResponse`: For individual musician payment data
- `EventBillingSummaryResponse`: For event-wide billing data

## Authorization
- **Musician Payment Summary Per Endpoint**: Requires admin user only.
- **Event Billing Summary**: Requires authentication (valid JWT token) and authorization: user must be either an admin user OR the owner/creator of the event.

## Data Flow
1. API endpoint receives request with event_id and authenticated user
2. Service layer validates user authorization based on the endpoint:
   - For Musician Payment Summary Per Event: user must be admin.
   - For Event Billing Summary: user must be admin or event owner.
3. Service layer retrieves necessary data from data layer:
    - Musician assignments for the event
    - Payment totals for each musician
    - Event final price (for billing summary)
    - Total payments to musicians (for billing summary)
4. Service layer constructs response objects
5. API layer returns formatted JSON response

## Error Handling
Both endpoints will handle:
- 401 Unauthorized: Missing or invalid authentication
- 403 Forbidden: User not authorized to access event data
- 404 Not Found: Event does not exist
- 400 Bad Request: Missing required data (e.g., event price not set)
- 500 Internal Server Error: Unexpected database or system errors

## Testing Requirements
Unit tests should be added for:
- Service layer functions (authorization, data retrieval, calculation accuracy)
- API endpoint functions (routing, authorization, response formatting)
- Edge cases (no musicians assigned, no payments made, etc.)

## Dependencies
This implementation depends on:
- Existing event musician assignment functionality (`event_musician` table)
- Existing musician event payment functionality (`musician_event_payment` table)
- Existing event pricing functionality (`events.price` column)
- Existing user model for musician name construction

## Estimated Effort
- Database layer: 0.5 days
- Service layer: 1 day
- API layer: 0.5 days
- Schema updates: 0.25 days
- Testing: 0.5 days
- Total: Approximately 2.75 days

## Notes
- Musician name will be constructed from `name`, `lastname`, and `second_lastname` fields in the user model
- All monetary values will use Decimal precision for accuracy
- Remaining payment calculations will never return negative values (minimum 0)
- Implementation follows existing code patterns and architectural guidelines