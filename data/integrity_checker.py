"""
Database Integrity Checker

Centralized integrity checking for database deletions.
Provides comprehensive validation before deletion operations to prevent
constraint violations and ensure data consistency.
"""

import logging
from typing import Optional
from config.database import SessionLocal
from models.user import User
from models.user_role import UserRole
from models.permission import Permission
from models.event import Event
from models.event_payment import EventPayment
from models.musician_event_payment import MusicianEventPayment
from models.event_musician import EventMusician
from models.musician_availability import MusicianAvailability
from models.user_detail import UserDetail

logger = logging.getLogger(__name__)


def check_integrity_before_deletion(entity_type: str, entity_id: int | str) -> Optional[str]:
    """
    Check all integrity constraints for an entity before deletion.

    Args:
        entity_type: Type of entity ('user', 'role', 'permission', 'event_payment', etc.)
        entity_id: Primary key or unique identifier of the entity

    Returns:
        Error message string if deletion would violate constraints, None if safe to delete

    Raises:
        ValueError: If entity_type is unknown
    """
    if entity_type == 'user':
        return _check_user_integrity(entity_id)
    elif entity_type == 'role':
        return _check_role_integrity(entity_id)
    elif entity_type == 'permission':
        return _check_permission_integrity(entity_id)
    elif entity_type == 'event_payment':
        return _check_event_payment_integrity(entity_id)
    elif entity_type == 'event':
        return _check_event_integrity(entity_id)
    elif entity_type == 'event_musician':
        return _check_event_musician_integrity(entity_id)
    elif entity_type == 'musician_event_payment':
        return _check_musician_event_payment_integrity(entity_id)
    else:
        raise ValueError(f"Unknown entity type: {entity_type}")


def _check_user_integrity(user_id: int) -> Optional[str]:
    """
    Check if a user can be safely deleted.

    Checks all relationships that could prevent user deletion:
    - Events created by user
    - Event payments made by user
    - Musician event payments received by user
    - Event musician assignments
    - Musician availability records
    - User details

    Args:
        user_id: The user's ID

    Returns:
        Error message if deletion would violate constraints, None if safe
    """
    db = SessionLocal()
    try:
        # Check events created by this user
        events_count = db.query(Event).filter(Event.user_id == user_id).count()
        if events_count > 0:
            if events_count == 1:
                return "This user cannot be deleted because they have created 1 event. Please reassign or delete this event first."
            else:
                return f"This user cannot be deleted because they have created {events_count} events. Please reassign or delete these events first."

        # Check event payments made by this user
        event_payments_count = db.query(EventPayment).filter(EventPayment.user_id == user_id).count()
        if event_payments_count > 0:
            if event_payments_count == 1:
                return "This user cannot be deleted because they have 1 event payment record. Please remove this payment record first."
            else:
                return f"This user cannot be deleted because they have {event_payments_count} event payment records. Please remove these payment records first."

        # Check musician event payments received by this user
        musician_payments_count = db.query(MusicianEventPayment).filter(MusicianEventPayment.musician_id == user_id).count()
        if musician_payments_count > 0:
            if musician_payments_count == 1:
                return "This user cannot be deleted because they have 1 musician payment record. Please remove this payment record first."
            else:
                return f"This user cannot be deleted because they have {musician_payments_count} musician payment records. Please remove these payment records first."

        # Check event musician assignments
        assignments_count = db.query(EventMusician).filter(EventMusician.musician_id == user_id).count()
        if assignments_count > 0:
            if assignments_count == 1:
                return "This user cannot be deleted because they have 1 musician assignment to an event. Please remove this assignment first."
            else:
                return f"This user cannot be deleted because they have {assignments_count} musician assignments to events. Please remove these assignments first."

        # Check musician availability records
        availability_count = db.query(MusicianAvailability).filter(MusicianAvailability.musician_id == user_id).count()
        if availability_count > 0:
            if availability_count == 1:
                return "This user cannot be deleted because they have 1 availability record. Please remove this availability record first."
            else:
                return f"This user cannot be deleted because they have {availability_count} availability records. Please remove these availability records first."

        # Check user details
        details_count = db.query(UserDetail).filter(UserDetail.user_id == user_id).count()
        if details_count > 0:
            if details_count == 1:
                return "This user cannot be deleted because they have 1 additional detail record. Please remove this detail record first."
            else:
                return f"This user cannot be deleted because they have {details_count} additional detail records. Please remove these detail records first."

        return None  # Safe to delete

    except Exception as e:
        logger.error(f"Error checking user integrity for user_id {user_id}: {e}")
        # If we can't check integrity, err on the side of caution
        return "Unable to verify user integrity. Please contact an administrator."
    finally:
        db.close()


def _check_role_integrity(role_identifier: int | str) -> Optional[str]:
    """
    Check if a role can be safely deleted.

    Checks all relationships that could prevent role deletion:
    - Users assigned to this role
    - Permissions assigned to this role

    Args:
        role_identifier: Role ID (int) or role name (str)

    Returns:
        Error message if deletion would violate constraints, None if safe
    """
    db = SessionLocal()
    try:
        # Get role by ID or name
        if isinstance(role_identifier, int):
            role = db.query(UserRole).filter(UserRole.id == role_identifier).first()
        else:
            role = db.query(UserRole).filter(UserRole.name == role_identifier).first()

        if not role:
            return None  # Role doesn't exist, but that's handled elsewhere

        # Check users assigned to this role
        users_count = db.query(User).filter(User.role_id == role.id).count()
        if users_count > 0:
            if users_count == 1:
                return "This role cannot be deleted because 1 user is assigned to it. Please reassign this user to another role first."
            else:
                return f"This role cannot be deleted because {users_count} users are assigned to it. Please reassign these users to another role first."

        # Check permissions assigned to this role
        if role.permissions:
            permissions_count = len(role.permissions)
            if permissions_count == 1:
                perm_name = role.permissions[0].name
                return f"This role cannot be deleted because it has 1 permission assigned ('{perm_name}'). Please remove this permission from the role first."
            else:
                perm_names = [p.name for p in role.permissions]
                perm_str = "', '".join(perm_names)
                return f"This role cannot be deleted because it has {permissions_count} permissions assigned ('{perm_str}'). Please remove these permissions from the role first."

        return None  # Safe to delete

    except Exception as e:
        logger.error(f"Error checking role integrity for role '{role_identifier}': {e}")
        # If we can't check integrity, err on the side of caution
        return "Unable to verify role integrity. Please contact an administrator."
    finally:
        db.close()


def _check_permission_integrity(permission_identifier: int | str) -> Optional[str]:
    """
    Check if a permission can be safely deleted.

    Checks all relationships that could prevent permission deletion:
    - Roles that have this permission assigned

    Args:
        permission_identifier: Permission ID (int) or permission name (str)

    Returns:
        Error message if deletion would violate constraints, None if safe
    """
    db = SessionLocal()
    try:
        # Get permission by ID or name
        if isinstance(permission_identifier, int):
            permission = db.query(Permission).filter(Permission.id == permission_identifier).first()
        else:
            permission = db.query(Permission).filter(Permission.name == permission_identifier).first()

        if not permission:
            return None  # Permission doesn't exist, but that's handled elsewhere

        # Check roles that have this permission assigned
        if permission.roles:
            roles_count = len(permission.roles)
            if roles_count == 1:
                role_name = permission.roles[0].name
                return f"This permission cannot be deleted because it is assigned to 1 role ('{role_name}'). Please remove this permission from the role first."
            else:
                role_names = [r.name for r in permission.roles]
                role_str = "', '".join(role_names)
                return f"This permission cannot be deleted because it is assigned to {roles_count} roles ('{role_str}'). Please remove this permission from these roles first."

        return None  # Safe to delete

    except Exception as e:
        logger.error(f"Error checking permission integrity for permission '{permission_identifier}': {e}")
        # If we can't check integrity, err on the side of caution
        return "Unable to verify permission integrity. Please contact an administrator."
    finally:
        db.close()


def _check_event_payment_integrity(payment_id: int) -> Optional[str]:
    """
    Check if an event payment can be safely deleted.

    EventPayment is a leaf entity with no relationships that would prevent deletion.
    All payments can be safely deleted as they don't have dependent records.

    Args:
        payment_id: The payment's ID

    Returns:
        None (always safe to delete)
    """
    # EventPayment is a leaf entity - no relationships prevent deletion
    # Future: Could add business logic checks (e.g., payment status, age, etc.)
    return None


def _check_event_integrity(event_id: int) -> Optional[str]:
    """
    Check if an event can be safely deleted.

    Checks all relationships that could prevent event deletion:
    - Event payments made for this event
    - Musician assignments to this event
    - Musician payments for this event

    Args:
        event_id: The event's ID

    Returns:
        Error message if deletion would violate constraints, None if safe
    """
    db = SessionLocal()
    try:
        # Check event payments
        event_payments_count = db.query(EventPayment).filter(EventPayment.event_id == event_id).count()
        if event_payments_count > 0:
            if event_payments_count == 1:
                return "This event cannot be deleted because it has 1 payment record. Please remove this payment record first."
            else:
                return f"This event cannot be deleted because it has {event_payments_count} payment records. Please remove these payment records first."

        # Check musician assignments
        assignments_count = db.query(EventMusician).filter(EventMusician.event_id == event_id).count()
        if assignments_count > 0:
            if assignments_count == 1:
                return "This event cannot be deleted because it has 1 musician assigned. Please remove this assignment first."
            else:
                return f"This event cannot be deleted because it has {assignments_count} musicians assigned. Please remove these assignments first."

        # Check musician payments
        musician_payments_count = db.query(MusicianEventPayment).filter(MusicianEventPayment.event_id == event_id).count()
        if musician_payments_count > 0:
            if musician_payments_count == 1:
                return "This event cannot be deleted because it has 1 musician payment record. Please remove this payment record first."
            else:
                return f"This event cannot be deleted because it has {musician_payments_count} musician payment records. Please remove these payment records first."

        return None  # Safe to delete

    except Exception as e:
        logger.error(f"Error checking event integrity for event_id {event_id}: {e}")
        # If we can't check integrity, err on the side of caution
        return "Unable to verify event integrity. Please contact an administrator."
    finally:
        db.close()


def _check_event_musician_integrity(assignment_id: int) -> Optional[str]:
    """
    Check if an event musician assignment can be safely deleted.

    Checks all relationships that could prevent assignment deletion:
    - Payments made to this musician for this event

    Args:
        assignment_id: The assignment's ID

    Returns:
        Error message if deletion would violate constraints, None if safe
    """
    db = SessionLocal()
    try:
        # Get the assignment to find event_id and musician_id
        assignment = db.query(EventMusician).filter(EventMusician.id == assignment_id).first()
        if not assignment:
            return None  # Assignment doesn't exist, but that's handled elsewhere

        # Check if there are any payments for this specific event-musician combination
        payments_count = db.query(MusicianEventPayment).filter(
            MusicianEventPayment.event_id == assignment.event_id,
            MusicianEventPayment.musician_id == assignment.musician_id
        ).count()

        if payments_count > 0:
            if payments_count == 1:
                return "This musician assignment cannot be deleted because there is 1 payment record for this musician and event. Please remove the payment record first."
            else:
                return f"This musician assignment cannot be deleted because there are {payments_count} payment records for this musician and event. Please remove all payment records first."

        return None  # Safe to delete

    except Exception as e:
        logger.error(f"Error checking event musician integrity for assignment_id {assignment_id}: {e}")
        # If we can't check integrity, err on the side of caution
        return "Unable to verify musician assignment integrity. Please contact an administrator."
    finally:
        db.close()


def _check_musician_event_payment_integrity(payment_id: int) -> Optional[str]:
    """
    Check if a musician event payment can be safely deleted.

    MusicianEventPayment is a leaf entity with proper composite foreign key constraints
    ensuring it can only exist if there's a corresponding EventMusician assignment.
    Since assignment integrity is checked separately, payments can generally be deleted.

    Args:
        payment_id: The payment's ID

    Returns:
        None (always safe to delete, but future business rules could be added)
    """
    # MusicianEventPayment is a leaf entity - no other entities depend on it
    # The composite foreign key (event_id, musician_id) ensures referential integrity
    # Future business rules could include:
    # - Cannot delete TOTAL payments (final settlements)
    # - Cannot delete payments older than X days/months
    # - Cannot delete payments with certain statuses
    return None