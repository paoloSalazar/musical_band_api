"""
Service layer for EventMusician entities.

Provides business logic for event musician assignment management in the Musical Band API.

Functions:
    - get_by_event: Get musicians assigned to an event
    - get_by_musician: Get events a musician is assigned to
    - assign_musician: Assign musician to event with validation
    - update_assignment: Update musician assignment
    - remove_musician: Remove musician from event
    - get_musicians_summary: Get summary of musicians for event
"""

import logging
from decimal import Decimal
from services.event_musician import data
from data import event as event_data
from data import user as user_data
from data.musician_availability import check_availability as musician_availability_data
from models.event_musician import EventMusician
from exceptions import (
    NotFoundError,
    DatabaseError,
    ConflictError,
    UnauthorizedError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def get_by_event(event_id: int, current_user: dict) -> list[EventMusician]:
    """
    Retrieve all musician assignments for a specific event.

    Args:
        event_id: The ID of the event.
        current_user: The current user dict.

    Returns:
        List of EventMusician objects for the event.

    Raises:
        NotFoundError: If event doesn't exist.
        UnauthorizedError: If user doesn't have permission.
        DatabaseError: If database operation fails.
    """
    try:
        event = event_data.get_one(event_id)
    except DatabaseError:
        raise NotFoundError(f"Event with id {event_id} not found")

    if not _can_manage_event_musicians(event, current_user):
        raise UnauthorizedError("You can only manage musicians for your own events")

    try:
        return data.get_by_event(event_id)
    except DatabaseError as e:
        logger.error(f"Failed to get musicians for event {event_id}")
        raise e


def get_by_musician(musician_id: int, current_user: dict) -> list[EventMusician]:
    """
    Retrieve all event assignments for a specific musician.

    Args:
        musician_id: The ID of the musician.
        current_user: The current user dict.

    Returns:
        List of EventMusician objects for the musician.

    Raises:
        UnauthorizedError: If user doesn't have permission.
        DatabaseError: If database operation fails.
    """
    if not _can_view_musician_assignments(musician_id, current_user):
        raise UnauthorizedError("You can only view your own event assignments")

    try:
        return data.get_by_musician(musician_id)
    except DatabaseError as e:
        logger.error(f"Failed to get assignments for musician {musician_id}")
        raise e


def assign_musician(assignment_data, current_user: dict) -> EventMusician:
    """
    Assign a musician to an event with validation.

    Args:
        assignment_data: EventMusicianCreate schema.
        current_user: The current user dict.

    Returns:
        The created EventMusician object.

    Raises:
        NotFoundError: If event or musician doesn't exist.
        UnauthorizedError: If user doesn't have permission.
        ConflictError: If musician already assigned or unavailable.
        DatabaseError: If database operation fails.
    """
    try:
        event = event_data.get_one(assignment_data.event_id)
    except DatabaseError:
        raise NotFoundError(f"Event with id {assignment_data.event_id} not found")

    if not _can_manage_event_musicians(event, current_user):
        raise UnauthorizedError("You can only manage musicians for your own events")

    try:
        user_data.get_one_by_id(assignment_data.musician_id)
    except DatabaseError:
        raise NotFoundError(f"Musician with id {assignment_data.musician_id} not found")

    # Check if already assigned
    if data.is_assigned_to_event(assignment_data.event_id, assignment_data.musician_id):
        raise ConflictError("Musician is already assigned to this event")

    # Check availability on event date
    event_date = event.start_datetime.date()
    if not musician_availability_data.check_availability(assignment_data.musician_id, event_date):
        raise ConflictError("Musician is not available on the event date")

    # Create the assignment
    musician = EventMusician(
        event_id=assignment_data.event_id,
        musician_id=assignment_data.musician_id,
        role=assignment_data.role,
        salary=assignment_data.salary,
        payment_status=assignment_data.payment_status.value
    )

    try:
        return data.create(musician)
    except DatabaseError as e:
        logger.error(f"Failed to assign musician {assignment_data.musician_id} to event {assignment_data.event_id}")
        raise e


def update_assignment(assignment_id: int, update_data, current_user: dict) -> EventMusician | None:
    """
    Update an existing musician assignment.

    Args:
        assignment_id: The ID of the assignment.
        update_data: EventMusicianUpdate schema.
        current_user: The current user dict.

    Returns:
        The updated EventMusician object, or None if not found.

    Raises:
        NotFoundError: If assignment doesn't exist.
        UnauthorizedError: If user doesn't have permission.
        DatabaseError: If database operation fails.
    """
    try:
        assignment = data.get_by_id(assignment_id)
    except DatabaseError:
        raise NotFoundError(f"Event musician assignment with id {assignment_id} not found")

    if not assignment:
        raise NotFoundError(f"Event musician assignment with id {assignment_id} not found")

    try:
        event = event_data.get_one(assignment.event_id)
    except DatabaseError:
        raise NotFoundError(f"Event with id {assignment.event_id} not found")

    if not _can_manage_event_musicians(event, current_user):
        raise UnauthorizedError("You can only manage musicians for your own events")

    updates = update_data.model_dump(exclude_unset=True)
    if updates:
        try:
            return data.update(assignment, updates)
        except DatabaseError as e:
            logger.error(f"Failed to update assignment {assignment_id}")
            raise e
    return assignment


def remove_musician(assignment_id: int, current_user: dict) -> bool:
    """
    Remove a musician from an event.

    Args:
        assignment_id: The ID of the assignment.
        current_user: The current user dict.

    Returns:
        True if removed, False if not found.

    Raises:
        NotFoundError: If assignment doesn't exist.
        UnauthorizedError: If user doesn't have permission.
        DatabaseError: If database operation fails.
    """
    try:
        assignment = data.get_by_id(assignment_id)
    except DatabaseError:
        raise NotFoundError(f"Event musician assignment with id {assignment_id} not found")

    if not assignment:
        raise NotFoundError(f"Event musician assignment with id {assignment_id} not found")

    try:
        event = event_data.get_one(assignment.event_id)
    except DatabaseError:
        raise NotFoundError(f"Event with id {assignment.event_id} not found")

    if not _can_manage_event_musicians(event, current_user):
        raise UnauthorizedError("You can only manage musicians for your own events")

    try:
        return data.delete(assignment_id)
    except DatabaseError as e:
        logger.error(f"Failed to remove musician assignment {assignment_id}")
        raise e


def get_musicians_summary(event_id: int, current_user: dict) -> dict:
    """
    Get summary of musicians assigned to an event.

    Args:
        event_id: The ID of the event.
        current_user: The current user dict.

    Returns:
        Dict with total_musicians, total_salary, etc.

    Raises:
        NotFoundError: If event doesn't exist.
        UnauthorizedError: If user doesn't have permission.
        DatabaseError: If database operation fails.
    """
    try:
        event = event_data.get_one(event_id)
    except DatabaseError:
        raise NotFoundError(f"Event with id {event_id} not found")

    if not _can_manage_event_musicians(event, current_user):
        raise UnauthorizedError("You can only manage musicians for your own events")

    try:
        musicians = data.get_by_event(event_id)
    except DatabaseError as e:
        logger.error(f"Failed to get musicians summary for event {event_id}")
        raise e

    total_musicians = len(musicians)
    total_salary = sum((m.salary for m in musicians), Decimal("0.00"))

    return {
        "total_musicians": total_musicians,
        "total_salary": total_salary,
        "musicians": musicians
    }


def _can_manage_event_musicians(event, current_user: dict) -> bool:
    """Check if user can manage musicians for the event."""
    return current_user.get('role') == 'admin' or event.user_id == current_user.get('id')


def _can_view_musician_assignments(musician_id: int, current_user: dict) -> bool:
    """Check if user can view musician assignments."""
    return (current_user.get('role') in ['admin', 'musician', 'auxiliar_musician'] and
            (current_user.get('role') == 'admin' or musician_id == current_user.get('id')))