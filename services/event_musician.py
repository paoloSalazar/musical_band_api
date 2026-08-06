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
import data.event_musician as data
from data import event as event_data
from data import user as user_data
import data.musician_availability as musician_availability_data
from models.event_musician import EventMusician
from schemas.event_musician import EventMusicianResponse
from exceptions import (
    NotFoundError,
    DatabaseError,
    ConflictError,
    UnauthorizedError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def get_by_event(event_id: int, current_user: dict) -> list[EventMusicianResponse]:
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
        musicians = data.get_by_event(event_id)
        return [
            EventMusicianResponse(
                id=musician.id,
                event_id=musician.event_id,
                musician_id=musician.musician_id,
                role=musician.role,
                salary=musician.salary,
                payment_status=musician.payment_status,
                musician_name=musician.musician.name if musician.musician else None,
                musician_lastname=musician.musician.lastname if musician.musician else None,
                created_at=musician.created_at,
                updated_at=musician.updated_at
            )
            for musician in musicians
        ]
    except DatabaseError as e:
        logger.error(f"Failed to get musicians for event {event_id}")
        raise e


def get_by_musician(musician_id: int, current_user: dict) -> list[EventMusicianResponse]:
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
        assignments = data.get_by_musician(musician_id)
        return [
            EventMusicianResponse(
                id=assignment.id,
                event_id=assignment.event_id,
                musician_id=assignment.musician_id,
                role=assignment.role,
                salary=assignment.salary,
                payment_status=assignment.payment_status,
                musician_name=assignment.musician.name if assignment.musician else None,
                musician_lastname=assignment.musician.lastname if assignment.musician else None,
                created_at=assignment.created_at,
                updated_at=assignment.updated_at
            )
            for assignment in assignments
        ]
    except DatabaseError as e:
        logger.error(f"Failed to get assignments for musician {musician_id}")
        raise e


def assign_musician(assignment_data, current_user: dict) -> EventMusicianResponse:
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
        musician = user_data.get_one_by_id(assignment_data.musician_id)
    except DatabaseError:
        raise NotFoundError(f"Musician with id {assignment_data.musician_id} not found")

    # Validate that the user has performer role (musician, auxiliar_musician or helper)
    if musician.role.name not in ['musician', 'auxiliar_musician', 'helper']:
        raise ValidationError("Only users with musician, auxiliar_musician or helper roles can be assigned to events")

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
        created_musician = data.create(musician)
        return EventMusicianResponse(
            id=created_musician.id,
            event_id=created_musician.event_id,
            musician_id=created_musician.musician_id,
            role=created_musician.role,
            salary=created_musician.salary,
            payment_status=created_musician.payment_status,
            musician_name=created_musician.musician.name if created_musician.musician else None,
            musician_lastname=created_musician.musician.lastname if created_musician.musician else None,
            created_at=created_musician.created_at,
            updated_at=created_musician.updated_at
        )
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


def update_assignment_by_event_musician(event_id: int, musician_id: int, update_data, current_user: dict) -> EventMusicianResponse | None:
    """
    Update a musician assignment by event and musician IDs.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.
        update_data: EventMusicianUpdate schema.
        current_user: The current user dict.

    Returns:
        The updated EventMusician object, or None if not found.

    Raises:
        NotFoundError: If assignment or event doesn't exist.
        UnauthorizedError: If user doesn't have permission.
        DatabaseError: If database operation fails.
    """
    try:
        event = event_data.get_one(event_id)
    except DatabaseError:
        raise NotFoundError(f"Event with id {event_id} not found")

    if not _can_manage_event_musicians(event, current_user):
        raise UnauthorizedError("You can only manage musicians for your own events")

    assignment = data.get_by_event_and_musician(event_id, musician_id)
    if not assignment:
        raise NotFoundError(f"Musician {musician_id} is not assigned to event {event_id}")

    updates = update_data.model_dump(exclude_unset=True)
    if updates:
        try:
            updated_assignment = data.update(assignment, updates)
            if updated_assignment:
                return EventMusicianResponse(
                    id=updated_assignment.id,
                    event_id=updated_assignment.event_id,
                    musician_id=updated_assignment.musician_id,
                    role=updated_assignment.role,
                    salary=updated_assignment.salary,
                    payment_status=updated_assignment.payment_status,
                    musician_name=updated_assignment.musician.name if updated_assignment.musician else None,
                    musician_lastname=updated_assignment.musician.lastname if updated_assignment.musician else None,
                    created_at=updated_assignment.created_at,
                    updated_at=updated_assignment.updated_at
                )
            return None
        except DatabaseError as e:
            logger.error(f"Failed to update assignment for event {event_id} and musician {musician_id}")
            raise e
    # Return the assignment as is if no updates
    return EventMusicianResponse(
        id=assignment.id,
        event_id=assignment.event_id,
        musician_id=assignment.musician_id,
        role=assignment.role,
        salary=assignment.salary,
        payment_status=assignment.payment_status,
        musician_name=assignment.musician.name if assignment.musician else None,
        musician_lastname=assignment.musician.lastname if assignment.musician else None,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at
    )


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
    except ConflictError as e:
        raise e
    except DatabaseError as e:
        logger.error(f"Failed to remove musician assignment {assignment_id}")
        raise e


def remove_musician_by_event_musician(event_id: int, musician_id: int, current_user: dict) -> bool:
    """
    Remove a musician from an event by event and musician IDs.

    Args:
        event_id: The ID of the event.
        musician_id: The ID of the musician.
        current_user: The current user dict.

    Returns:
        True if removed, False if not found.

    Raises:
        NotFoundError: If assignment or event doesn't exist.
        UnauthorizedError: If user doesn't have permission.
        DatabaseError: If database operation fails.
    """
    try:
        event = event_data.get_one(event_id)
    except DatabaseError:
        raise NotFoundError(f"Event with id {event_id} not found")

    if not _can_manage_event_musicians(event, current_user):
        raise UnauthorizedError("You can only manage musicians for your own events")

    assignment = data.get_by_event_and_musician(event_id, musician_id)
    if not assignment:
        raise NotFoundError(f"Musician {musician_id} is not assigned to event {event_id}")

    try:
        return data.delete(assignment.id)
    except ConflictError as e:
        raise e
    except DatabaseError as e:
        logger.error(f"Failed to remove musician {musician_id} from event {event_id}")
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
    ### consider to fix, permissions checker 
    return current_user.get('role') == 'admin' or event.user_id == current_user.get('id') or current_user.get('role') in ['musician', 'auxiliar_musician', 'helper']


def _can_view_musician_assignments(musician_id: int, current_user: dict) -> bool:
    """Check if user can view musician assignments."""
    return (current_user.get('role') in ['admin', 'musician', 'auxiliar_musician', 'helper'] and
            (current_user.get('role') == 'admin' or musician_id == current_user.get('id')))