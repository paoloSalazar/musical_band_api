# Database Integrity Fix Plan - Complete Database Schema

## 🎯 Overview

Comprehensive database integrity fixes across ALL tables and relationships in the Musical Band API database. Issues are prioritized from High to Low criticality, covering events, users, roles, permissions, and all related entities.

---

## 🚨 HIGH PRIORITY ISSUES

### Issue 0: Complete Database Schema Coverage
#### 🎯 Problem Statement
This document was originally focused only on musician_events relationships but needs to cover ALL database tables for complete integrity.

#### 📊 **Tables Covered in Original Plan:**
- ✅ events
- ✅ event_payments
- ✅ event_musicians
- ✅ musician_event_payments

#### 📊 **Tables MISSING from Original Plan:**
- ❌ users
- ❌ user_roles
- ❌ permissions
- ❌ user_details
- ❌ musician_availability

#### Required State ✅
- Complete coverage of all database tables
- Consistent integrity constraints across entire schema
- Unified approach to referential integrity

---

## 🚨 CRITICAL PRIORITY ISSUES (Users & Roles)

### Issue A: User Deletion Cascade Prevention

#### 🎯 Problem Statement
User deletion could leave orphaned records across multiple related tables, causing data inconsistency and broken relationships.

#### Current State ❌
- Users have relationships to: events, event_payments, event_musicians, musician_event_payments, user_details, musician_availability
- No database-level cascade prevention configured
- User deletion possible when related records exist

#### Required State ✅
- User deletion blocked when dependent records exist
- Clear error messages for all relationship types
- Application-level validation before deletion attempts

#### 🛠️ Implementation Plan

##### Phase 1: Analyze User Relationships
###### Tasks:
1. **Audit all foreign keys pointing to users table:**
   ```sql
   SELECT tc.table_name, tc.constraint_name, kcu.column_name
   FROM information_schema.table_constraints tc
   JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
   WHERE tc.constraint_type = 'FOREIGN KEY'
   AND tc.table_schema = 'public'
   AND kcu.table_name != 'users'
   AND kcu.referenced_table_name = 'users';
   ```

2. **Document relationship impact** for each dependent table

##### Phase 2: Configure Foreign Key Constraints
###### Tasks:
1. **Update FK constraints to use RESTRICT instead of CASCADE**
2. **Ensure application integrity checker handles all relationships**

### Issue B: Role-Based Access Control Integrity

#### 🎯 Problem Statement
Role and permission deletions could break user access control and leave orphaned relationships.

#### Current State ❌
- Users assigned to roles (users.role_id → user_roles.id)
- Roles assigned to permissions (role_permissions)
- No cascade prevention for role/permission deletions

#### Required State ✅
- Role deletion blocked if users are assigned
- Permission deletion blocked if roles are assigned
- Clear dependency messages

#### 🛠️ Implementation Plan

##### Phase 1: Role Deletion Constraints
###### Tasks:
1. **Ensure FK from users to user_roles uses RESTRICT**
2. **Application validation** prevents role deletion when users assigned

##### Phase 2: Permission Deletion Constraints
###### Tasks:
1. **Ensure FK constraints prevent orphaned role_permissions**
2. **Application validation** for permission deletion

---

## 🚨 HIGH PRIORITY ISSUES (Original Musician Events)

### Issue 1: Orphaned Payment Records (Musician Event Payments)

#### 🎯 Problem Statement
Critical database referential integrity issue: orphaned payment records exist in `musician_event_payments` table after `event_musician` records are deleted. This violates business rules and can lead to inconsistent financial data.

#### Current State ❌
- `musician_event_payments` has FKs to `events.id` and `users.id`
- **NO relationship** to `event_musicians` table
- Payments can exist for musician-event combinations that were never assigned
- Deleting assignments leaves orphaned payment records
- No constraint prevents invalid payment creation

#### Required State ✅
- Payments must reference valid musician-event assignments
- No orphaned payment records
- Database-level enforcement of business rules
- Prevention of invalid payment creation

#### 🛠️ Implementation Plan: Composite Foreign Key

##### Phase 1: Data Analysis & Audit
###### Tasks:
1. **Audit existing data for orphaned records**
   ```sql
   SELECT p.* FROM musician_event_payments p
   LEFT JOIN event_musicians em ON p.event_id = em.event_id AND p.musician_id = em.musician_id
   WHERE em.id IS NULL;
   ```

2. **Count affected records**
   ```sql
   SELECT COUNT(*) as orphaned_payments FROM musician_event_payments p
   LEFT JOIN event_musicians em ON p.event_id = em.event_id AND p.musician_id = em.musician_id
   WHERE em.id IS NULL;
   ```

3. **Document business impact** - Which events/musicians affected

###### Estimated Time: 0.5 days
###### Dependencies: None

##### Phase 2: Database Migration Preparation
###### Tasks:
1. **Create Alembic migration script**
   ```bash
   alembic revision -m "add_composite_fk_musician_event_payments"
   ```

2. **Migration content:**
   ```python
   def upgrade():
       # Add composite foreign key constraint
       op.create_foreign_key(
           'fk_musician_event_assignment',
           'musician_event_payments', 'event_musicians',
           ['event_id', 'musician_id'], ['event_id', 'musician_id'],
           ondelete='RESTRICT'
       )

   def downgrade():
       op.drop_constraint('fk_musician_event_assignment', 'musician_event_payments')
   ```

3. **Test migration on development database**
   - Backup dev database
   - Run migration
   - Verify constraint works

###### Estimated Time: 0.5 days
###### Dependencies: Phase 1 complete

##### Phase 3: Data Cleanup (if needed)
###### Tasks:
1. **If orphaned records found:**
   - Document all orphaned payments with business context
   - Get approval for deletion or reassignment
   - Create cleanup script with transaction rollback capability

2. **If no orphaned records:**
   - Skip to Phase 4

###### Estimated Time: 0.25-1 day (depending on cleanup complexity)
###### Dependencies: Phase 1 complete

##### Phase 4: Application Logic Update
###### Location: `services/musician_event_payment.py`

###### Tasks:
1. **Add redundant application-level validation** (defense in depth)
   ```python
   # Before creating payment, verify assignment exists
   assignment = assignment_data.get_by_event_and_musician(
       payment_data_input.event_id,
       payment_data_input.musician_id
   )
   if not assignment:
       raise ValidationError(
           f"Cannot create payment: musician {payment_data_input.musician_id} "
           f"is not assigned to event {payment_data_input.event_id}"
       )
   ```

2. **Update existing validation tests** to cover this scenario

###### Estimated Time: 0.25 days
###### Dependencies: Phase 2 complete

##### Phase 5: Testing & Validation
###### Tasks:
1. **Unit tests for constraint behavior**
   - Test payment creation fails when assignment doesn't exist
   - Test assignment deletion fails when payments exist
   - Test valid payment creation still works

2. **Integration tests**
   - Full payment workflow with assignment validation
   - Error scenarios with proper error messages

3. **Database constraint tests**
   - Direct SQL attempts to violate constraint
   - Application-level constraint handling

###### Estimated Time: 0.5 days
###### Dependencies: Phase 4 complete

##### Phase 6: Deployment & Monitoring
###### Tasks:
1. **Staging deployment**
   - Deploy migration to staging
   - Run full test suite
   - Verify constraint enforcement

2. **Production deployment**
   - Schedule maintenance window
   - Backup production database
   - Deploy migration with rollback plan
   - Monitor application logs for constraint violations

3. **Post-deployment monitoring**
   - Alert on any constraint violation attempts
   - Monitor payment creation success rates
   - Track any application errors related to constraints

###### Estimated Time: 0.5 days
###### Dependencies: Phase 5 complete

##### 🎯 Constraint Behavior
- **ON DELETE: RESTRICT** - Cannot delete assignment if payments exist
- **ON INSERT/UPDATE: CASCADE** - Prevents orphaned payment records

##### 🚨 Error Handling
- **Application**: "Cannot create payment: musician {id} is not assigned to event {id}"
- **Database**: FOREIGN KEY constraint "fk_musician_event_assignment" violated

---

## ⚠️ MEDIUM PRIORITY ISSUES

### Issue 2: Missing Unique Constraints on Event Assignments

#### 🎯 Problem Statement
No constraint prevents multiple assignments of the same musician to the same event, leading to data duplication and inconsistent payment tracking.

#### Current State ❌
- No unique constraint on (event_id, musician_id) in event_musicians table
- Multiple assignments possible for same musician-event combination
- Potential for duplicate salary and payment records

#### Required State ✅
- One assignment per musician per event
- Database-level enforcement of uniqueness
- Clear error messages for duplicate assignment attempts

#### 🛠️ Implementation Plan

##### Phase 1: Data Analysis
###### Tasks:
1. **Check for existing duplicates**
   ```sql
   SELECT event_id, musician_id, COUNT(*) as count
   FROM event_musicians
   GROUP BY event_id, musician_id
   HAVING COUNT(*) > 1;
   ```

2. **Document impact** of any duplicates found

##### Phase 2: Migration
###### Tasks:
1. **Create migration to add unique constraint**
   ```python
   def upgrade():
       op.create_unique_constraint(
           'uq_event_musician_assignment',
           'event_musicians',
           ['event_id', 'musician_id']
       )
   ```

##### Phase 3: Cleanup (if duplicates found)
###### Tasks:
1. **Resolve duplicates** - determine which record to keep
2. **Data migration** to clean duplicates before constraint

##### Phase 4: Application Updates
###### Location: `services/event_musician.py`
###### Tasks:
1. **Add explicit check** before assignment creation
2. **Update error handling** for constraint violations

### Issue 3: Cascade Delete Behavior for Events

#### 🎯 Problem Statement
Event deletion could leave orphaned records in related tables (event_musicians, musician_event_payments, event_payments).

#### Current State ❌
- No explicit cascade configuration (defaults to no cascade)
- Event deletion possible when related records exist
- Potential for orphaned records

#### Required State ✅
- Event deletion blocked when related records exist
- Clear error messages
- Application handles cleanup logic

#### 🛠️ Implementation Plan

##### Phase 1: Review Current FKs
###### Tasks:
1. **Audit all foreign keys** pointing to events table
2. **Document cascade behavior** for each relationship

##### Phase 2: Configure Restrict Behavior
###### Tasks:
1. **Update FK constraints** to use RESTRICT instead of CASCADE
2. **Ensure application logic** handles deletion properly

### Issue 4: Availability Conflict Prevention

#### 🎯 Problem Statement
Musicians can be assigned to events when marked as unavailable, leading to scheduling conflicts.

#### Current State ❌
- Application checks availability during assignment
- No database-level constraint prevents conflicts
- Availability data can be modified after assignment

#### Required State ✅
- Database-level validation of availability
- Prevention of conflicting assignments
- Clear error messages for availability conflicts

#### 🛠️ Implementation Plan

##### Phase 1: Review Current Logic
###### Location: `services/event_musician.py`
###### Tasks:
1. **Document existing availability checks**
2. **Identify gaps** in validation

##### Phase 2: Strengthen Validation
###### Tasks:
1. **Add trigger or constraint** to validate availability
2. **Consider business rules** for availability checking

---

## 📋 LOW PRIORITY ISSUES

### Issue 5: Datetime Validation Constraints

#### 🎯 Problem Statement
No database-level constraint ensures event end_datetime is after start_datetime.

#### Current State ❌
- Only application-level validation exists
- Database allows invalid datetime ranges

#### Required State ✅
- Database-level check constraint
- Prevention of invalid event scheduling

#### 🛠️ Implementation Plan

##### Phase 1: Migration
###### Tasks:
1. **Add check constraint**
   ```sql
   ALTER TABLE events ADD CONSTRAINT chk_event_dates
   CHECK (end_datetime > start_datetime);
   ```

### Issue 6: Payment Amount Business Rules

#### 🎯 Problem Statement
No enforcement that total event payments match event price or that musician payments don't exceed salaries.

#### Current State ❌
- Application-level validation exists
- Database allows overpayments

#### Required State ✅
- Database triggers for business rule validation
- Consistent payment amount enforcement

### Issue 7: Payment Status Enum Consistency

#### 🎯 Problem Statement
payment_status in event_musicians stored as VARCHAR instead of proper enum type.

#### Current State ❌
- String validation in application
- Potential for invalid status values in database

#### Required State ✅
- Proper enum type in database
- Consistent status value enforcement

### Issue 8: Event Creation in the Past (Database-Level Validation)

#### 🎯 Problem Statement
Users can create events with start_datetime in the past, which should be prevented at database level for data integrity.

#### Current State ❌
- No database constraint prevents past event creation
- Only application-level validation (currently missing)
- Invalid events can be inserted directly into database

#### Required State ✅
- Database-level check constraint prevents past events
- Consistent validation regardless of application logic
- Clear error messages for constraint violations

#### 🛠️ Implementation Plan

##### Phase 1: Constraint Design & Testing
###### Tasks:
1. **Design check constraint** for events table:
   ```sql
   ALTER TABLE events ADD CONSTRAINT chk_event_not_in_past
   CHECK (start_datetime >= CURRENT_TIMESTAMP);
   ```
   *Note: This uses transaction start time, which may allow events slightly in the past if transaction starts near creation time. For stricter enforcement, consider application-level validation.*

2. **Test constraint behavior** on development database
   - Attempt to insert past events
   - Verify constraint blocks invalid inserts
   - Test edge cases (events at exact current time)

##### Phase 2: Migration Implementation
###### Tasks:
1. **Create Alembic migration**
   ```bash
   alembic revision -m "add_event_past_validation_constraint"
   ```

2. **Migration content:**
   ```python
   def upgrade():
       op.create_check_constraint(
           'chk_event_not_in_past',
           'events',
           'start_datetime >= CURRENT_TIMESTAMP'
       )

   def downgrade():
       op.drop_constraint('chk_event_not_in_past', 'events')
   ```

3. **Handle existing data** (if any past events exist)
   - Check for existing past events
   - Clean up or document if found

##### Phase 3: Application Coordination
###### Tasks:
1. **Update application validation** to match database constraint
2. **Error handling** for constraint violations in application logs
3. **Update tests** to expect database-level errors

##### Phase 4: Testing & Deployment
###### Tasks:
1. **Unit tests** for constraint behavior
2. **Integration tests** with application error handling
3. **Staging deployment** and verification
4. **Production deployment** with monitoring

---

## 📊 Overall Risk Assessment

### **Critical Risk 🚨 Addressed:**
- **Complete Data Integrity** - All tables covered with appropriate constraints
- **User Management Integrity** - Role/permission relationships protected
- **Financial Data Protection** - Payment constraints prevent corruption

### **High Risk ✅ Addressed:**
- **Data corruption** - Composite FK prevents orphaned payments
- **Financial inconsistency** - Business rules enforced at database level
- **Access Control Integrity** - User/role/permission relationships protected

### **Medium Risk ⚠️ Mitigated:**
- **Data duplication** - Unique constraints prevent duplicates
- **Orphaned records** - Restrict delete behavior across all tables
- **Scheduling conflicts** - Availability validation
- **Relationship Integrity** - All FK relationships properly constrained

### **Low Risk ✅ Acceptable:**
- **Invalid dates** - Check constraints for datetime validation
- **Past events** - Database constraints prevent invalid scheduling
- **Payment inconsistencies** - Business rule triggers
- **Status validation** - Enum types for consistency
- **Data Type Validation** - Appropriate constraints on all columns

---

## ⏱️ Consolidated Timeline Summary

| Priority | Issue Category | Issue | Est. Time | Dependencies |
|----------|----------------|-------|-----------|--------------|
| **CRITICAL** | User Management | User Deletion Constraints | 1-1.5 days | None |
| **CRITICAL** | Access Control | Role/Permission Integrity | 1-1.5 days | None |
| **HIGH** | Musician Events | Orphaned Payment Records | 2.25-3 days | After Critical |
| **MEDIUM** | Data Quality | Unique Constraints | 0.5-1 day | After High |
| **MEDIUM** | Referential Integrity | Cascade Delete Behavior | 0.5 days | After High |
| **MEDIUM** | Business Logic | Availability Validation | 0.5 days | After High |
| **LOW** | Data Validation | Datetime Validation | 0.25 days | After Medium |
| **LOW** | Data Validation | Event Past Validation | 0.5 days | After Medium |
| **LOW** | Business Logic | Payment Rules | 0.5 days | After Medium |
| **LOW** | Data Types | Status Enum Consistency | 0.25 days | After Medium |
| **Total** | | | **6.75-10 days** | |

---

## 🚀 Business Impact

This comprehensive database integrity overhaul ensures:
- **Complete Data Integrity** across ALL database tables and relationships
- **Financial Accuracy** with payment constraints and business rules
- **Access Control Security** with protected user/role/permission relationships
- **Operational Reliability** with scheduling and availability validation
- **Regulatory Compliance** with audit trails and data consistency
- **System Stability** with database-level enforcement and application validation
- **Data Quality Assurance** with constraints preventing corruption and inconsistencies

---

## 📋 Implementation Strategy

### Phase 1: Critical Infrastructure (Users & Access Control)
- User deletion constraints
- Role/permission integrity
- **Est. Time: 2-3 days**

### Phase 2: Core Business Logic (Musician Events)
- Orphaned payment records fix
- Composite foreign key implementation
- **Est. Time: 2.25-3 days**

### Phase 3: Data Quality & Validation
- Unique constraints, cascade behavior, availability validation
- **Est. Time: 1.5-2.5 days**

### Phase 4: Advanced Features
- Datetime validation, payment business rules, enum consistency
- **Est. Time: 1-1.5 days**

---

**Ready for comprehensive phased implementation covering entire database schema.**</content>
<parameter name="filePath">plans/database_integrity_fix_plan.md