# Event Payment Feature Plan

## Overview

This document outlines the implementation plan for adding payment tracking to the musical band event management system.

## Current State

- Events have a status field (PENDING, CONFIRMED, CANCELLED, COMPLETED, PAYMENT_PENDING)
- Events have a `price` field (added via migration)
- Events are created by client users
- No payment history/tracking table exists

## User Requirements Summary

1. **Client creates event** → Status = PENDING (no payment yet)
2. **Admin sets final price** → Defines the total cost of the event
3. **Client makes payments** → Can make one or more ADVANCE payments
4. **Remaining payment** → Client pays remaining balance (TOTAL - ADVANCE)
5. **Partial payment** → Event can be CONFIRMED with partial payments (no need to pay entire amount)
6. **Full payment** → When fully paid, event status changes to COMPLETED
7. **Minimum advance** → 30% of final_price required for ADVANCE payments
8. **Payment deadline** → ADVANCE payments must be at least 1 day before event
9. **Auto-complete** → Events past end_datetime + fully paid → COMPLETED
10. **Payment pending** → Events past end_datetime + not fully paid → PAYMENT_PENDING
11. **Admin cancel** → Admin can manually cancel event

## Proposed Table Design

Based on your proposed table, here's an enhanced version:

```sql
CREATE TABLE public.event_payments (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    event_id bigint NOT NULL REFERENCES public.events(id),
    user_id bigint NOT NULL REFERENCES public.users(id),
    payment_date timestamp DEFAULT now() NOT NULL,
    amount numeric NOT NULL,
    payment_type text NOT NULL CHECK (payment_type IN ('ADVANCE', 'TOTAL', 'REMAINING')),
    notes text,
    created_at timestamp DEFAULT now() NOT NULL
);
```

### Recommended Changes from Your Proposal:
1. **Added CHECK constraint** on payment_type to ensure only valid values
2. **Added notes field** for payment notes (receipt references, etc.)
3. **Added created_at** for audit tracking

## Payment Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                  PAYMENT WORKFLOW                        │
└─────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐
  │ Client Creates  │
  │     Event       │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Status: PENDING │
  │ final_price:    │
  │     NULL        │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────────────┐
  │ Admin Sets Final Price  │
  └────────┬────────────────┘
           │
           ▼
    ┌─────────────┐
    │ final_price │
    │    set?    │
    └─────┬───────┘
     No  │  Yes
     ▼   │    ▼
    ┌────┴──────────┐     ┌────────────────────────┐
    │ Client waits   │     │  Client Can Make Payment │
    │  for admin   │     └───────────┬────────────┘
    └─────────────┘                │
                                      │
                     ┌────────────────┬────────────────┬──────────────┐
                     │               │              │             │
                     ▼               ▼              ▼            ▼
               ┌──────────┐ ┌──────────┐ ┌──────────┐
               │  ADVANCE │ │  TOTAL  │ │ REMAINING│
               │ Payment  │ │ Payment  │ │ Payment  │
               └────┬─────┘ └────┬─────┘ └────┬─────┘
                    │            │           │
                    └─────┬──────┴─────┬────┘
                         │           │
                         ▼           ▼
                    ┌────────────────────┐
                    │ Status: CONFIRMED  │
                    └────────┬───────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │ Check if fully paid │
                    └────────┬───────────┘
                             │
              ┌────────────┴────────────┐
              │                       │
              ▼                       ▼
        ┌──────────────┐    ┌──────────────────┐
        │ Fully paid  │    │ Partially paid   │
        └─────┬──────┘    └────────┬─────────┘
              │                     │
              ▼                     ▼
        ┌──────────────┐    ┌────────────────┐
        │Status:COMPLETED│    │ Event proceeds │
        └──────────────┘    │ as CONFIRMED   │
                             └────────────────┘

───────────────────────────────────────────────────────────────────────────────
STATUS FLOW SUMMARY:
───────────────────────────────────────────────────────────────────────────────
  - PENDING + Any payment ──► CONFIRMED
  - CONFIRMED + Fully paid ──► COMPLETED  
  - CONFIRMED + Partial ────► CONFIRMED (stays)
```

## Payment Types Logic

| Payment Type | Description | When Used |
|-------------|-------------|-----------|
| ADVANCE | Partial payment towards total | Client makes initial/down payment |
| REMAINING | Pays the remaining balance | After advances, pays rest |
| TOTAL | Pays full amount at once | Client pays everything in one go |

## Implementation Tasks

### Phase 1: Database & Models
- [x] Add `final_price` column to events table (already done)
- [ ] Create `EventPayment` model
- [ ] Create Alembic migration

### Phase 2: Data Layer
- [ ] Create `data/event_payment.py` with CRUD operations
- [ ] Add helper functions:
  - `get_payments_by_event(event_id)`
  - `get_total_paid(event_id)`
  - `get_pending_balance(event_id)`

### Phase 3: Schemas
- [ ] Create `schemas/event_payment.py`:
  - `EventPaymentBase`
  - `EventPaymentCreate`
  - `EventPaymentResponse`
  - `EventPaymentType` enum

### Phase 4: Service Layer
- [ ] Create `services/event_payment.py`:
  - `create_payment(event_id, user_id, amount, payment_type)`
  - `get_event_payment_summary(event_id)` - returns paid, pending, total

### Phase 5: API Endpoints
- [ ] Create `web/event_payment.py`:
  - `POST /api/events/{event_id}/payments` - Add payment
  - `GET /api/events/{event_id}/payments` - List payments
  - `GET /api/events/{event_id}/payments/summary` - Payment summary

### Phase 6: Event Integration
- [x] Update `Event` model to include final_price field (already done)
- [x] Add endpoint for admin to set final price: `PATCH /api/events/{event_id}/price` (already done)
- [ ] Add logic to auto-confirm event when any payment is made
- [ ] Add logic to auto-complete event when fully paid
- [ ] Add admin endpoint to cancel event: `PATCH /api/events/{event_id}/cancel`
- [ ] Add scheduled task to auto-complete events past their end_datetime

### Phase 6b: Scheduled Tasks (NEW)
- [ ] Create daily cron job to update event status:
  ```python
  # Update CONFIRMED events to COMPLETED:
  # BOTH conditions must be met:
  # 1. Event is fully paid (total_paid >= final_price)
  # 2. Event end_datetime has passed (end_datetime < NOW())
  UPDATE events 
  SET status = 'COMPLETED' 
  WHERE status = 'CONFIRMED' 
    AND end_datetime < NOW()
    AND (SELECT SUM(amount) FROM event_payments WHERE event_id = events.id) >= events.final_price;
  ```
- [ ] Also set PAYMENT_PENDING for events past end_datetime that aren't fully paid:
  ```python
  UPDATE events 
  SET status = 'PAYMENT_PENDING' 
  WHERE status = 'CONFIRMED' 
    AND end_datetime < NOW()
    AND (SELECT SUM(amount) FROM event_payments WHERE event_id = events.id) < events.final_price;
  ```
- [ ] Run daily at midnight or after midnight
- [ ] Add cron job option (OS task):
  - **Option A - OS Cron (recommended):**
    - Linux/Mac: `crontab -e` → `0 0 * * * /path/to/python /path/to/task.py`
    - Windows: Task Scheduler
    - Pros: Simple, separate from database
  - **Option B - Database pg_cron:**
    - PostgreSQL extension for scheduled jobs
    - `SELECT cron.schedule('update-events', '0 0 * * *', $UPDATE events...$);`
    - Pros: Runs inside database, no external dependencies
  - **Option C - Python Celery/ APScheduler:**
    - Use Celery beat or APScheduler in Python app
    - Pros: App-controlled, good for complex scheduling
  - **Recommendation:** Option A (OS cron) for simplicity

### Phase 7: Testing
- [ ] Unit tests for data layer
- [ ] Unit tests for service layer
- [ ] Unit tests for API endpoints

## Access Control

| Action | Client | Admin |
|--------|--------|-------|
| Create event | ✓ | ✓ |
| Set final price | - | ✓ |
| Cancel event | - | ✓ |
| View own event payments | ✓ | ✓ |
| View all payments | - | ✓ |
| Add payment | ✓ (own events) | ✓ (all events) |

## Validation Rules

1. Payment amount must be positive
2. Total payments cannot exceed final_price (for ADVANCE + REMAINING)
3. Cannot add payments to events without final_price set
4. Payment_type VALIDATE:
   - ADVANCE: can be used multiple times
   - REMAINING: only when advances exist
   - TOTAL: only when no previous payments

## Status Flow Update

| Current Status | Condition | New Status |
|-------------|-----------|-----------|
| PENDING | Any payment | CONFIRMED |
| PENDING | None | PENDING |
| CONFIRMED | Fully paid AND end_datetime exceeded | COMPLETED |
| CONFIRMED | Partially paid | CONFIRMED |
| CONFIRMED | Fully paid but event not yet ended | CONFIRMED (stays) |
| Any | Not fully paid even after end_datetime | CANCELLED (optional) |

## Requirements Confirmed

### 1. Auto-complete on event date
- **Yes**, once the event date is exceeded, status should automatically change to COMPLETED
- Need a scheduled task or database trigger to check and update events daily
- Implementation: Daily cron job that sets `status = COMPLETED` where `end_datetime < now()` and `status = CONFIRMED`

### 2. Minimum advance payment
- **Yes**, 30% minimum advance payment is required
- Client cannot make ADVANCE payment below 30% of final_price
- Validation rule: `amount >= (final_price * 0.30)`

### 3. Payment deadline
- **Yes**, advance payments must be received at least 1 day before the event
- Implementation: Check `start_datetime > NOW() + 1 day` when processing ADVANCE payments
- Reject ADVANCE payments if event is within 24 hours

### 4. Refunds
- **No** refunds required for the moment
- This can be added later if needed

### 5. Payment processor tracking
Q: Should we track who processed the payment (admin vs client-initiated)?

A: The payment records already include `user_id` which identifies who made the payment. This tracks:
- Client-initiated: `user_id` = the client who owns the event
- Admin processing: `user_id` = the admin who processed the payment on behalf of client

No additional tracking needed - the `user_id` field serves this purpose.

## Updated Validation Rules

1. Payment amount must be positive
2. **ADVANCE payment minimum: 30% of final_price**
3. **ADVANCE payment deadline: must be at least 1 day before event start**
4. Total payments cannot exceed final_price
5. Cannot add payments to events without final_price set
6. Payment_type VALIDATE:
   - ADVANCE: can be used multiple times (min 30% each time)
   - REMAINING: only when advances exist
   - TOTAL: only when no previous payments

## Cron Job Implementation Options

### Option A: OS Cron (Recommended)
```bash
# Linux/Mac
0 0 * * * /path/to/venv/python /path/to/scripts/update_event_status.py
```
- Python script for Windows Task Scheduler

### Option B: pg_cron
```sql
SELECT cron.schedule('job', '0 0 * * *', $UPDATE events...$);
```

### Option C: APScheduler
```python
from apscheduler.schedulers.blocking import BlockingScheduler
```

### Summary
| Option | Pros | Cons |
|--------|------|------|
| A - OS Cron | Simple | Requires OS access |
| B - pg_cron | In-database | Needs extension |
| C - APScheduler | Flexible | More dependencies |

**Recommendation:** Option A (OS Cron)
