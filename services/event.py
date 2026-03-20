"""
Service layer for Event business logic.

Provides business logic operations for event management,
including validation and data transformation.

Functions:
    - get_one: Get event by ID
    - get_all: Get all events
    - create: Create a new event
    - modify: Update an existing event
    - delete: Delete an event
"""

import logging
from schemas.event import EventCreate, EventUpdate, EventResponse, EventStatusEnum
from models.event import Event, EventStatus
import data.event as data
from exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


def get_one(event_id: int) -> EventResponse:
    """
    Retrieve an event by its ID.

    Args:
        event_id: The ID of the event to retrieve.

    Returns:
        EventResponse object.

    Raises:
        NotFoundError: If event is not found.
        DatabaseError: If database operation fails.
    """
    try:
        event = data.get_one(event_id)
        if event is None:
            logger.warning(f"Event with id {event_id} not found")
            raise NotFoundError(f"Event with id {event_id} not found")
        
        # Map EventStatus to EventStatusEnum
        status = EventStatusEnum(event.status.value)
        
        return EventResponse(
            id=event.id,
            name=event.name,
            place=event.place,
            description=event.description,
            start_datetime=event.start_datetime,
            end_datetime=event.end_datetime,
            is_all_day=event.is_all_day,
            status=status,
            user_id=event.user_id,
            created_at=event.created_at,
            updated_at=event.updated_at
        )
    except NotFoundError:
        raise
    except DatabaseError:
        logger.error(f"Database error in get_one for event {event_id}")
        raise


def get_all() -> list[EventResponse]:
    """
    Retrieve all events from the database.

    Returns:
        List of EventResponse objects.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        events = data.get_all()
        result = []
        for event in events:
            status = EventStatusEnum(event.status.value)
            result.append(EventResponse(
                id=event.id,
                name=event.name,
                place=event.place,
                description=event.description,
                start_datetime=event.start_datetime,
                end_datetime=event.end_datetime,
                is_all_day=event.is_all_day,
                status=status,
                user_id=event.user_id,
                created_at=event.created_at,
                updated_at=event.updated_at
            ))
        return result
    except DatabaseError:
        logger.error("Database error in get_all")
        raise


def create(event_create: EventCreate) -> EventResponse:
    """
    Create a new event in the database.

    Args:
        event_create: EventCreate schema with event data.

    Returns:
        Created EventResponse object.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        event = Event(
            name=event_create.name,
            place=event_create.place,
            description=event_create.description,
            start_datetime=event_create.start_datetime,
            end_datetime=event_create.end_datetime,
            is_all_day=event_create.is_all_day,
            user_id=event_create.user_id,
            status=EventStatus.PENDING
        )
        
        created_event = data.create(event)
        logger.info(f"Created event with id {created_event.id}")
        
        status = EventStatusEnum(created_event.status.value)
        
        return EventResponse(
            id=created_event.id,
            name=created_event.name,
            place=created_event.place,
            description=created_event.description,
            start_datetime=created_event.start_datetime,
            end_datetime=created_event.end_datetime,
            is_all_day=created_event.is_all_day,
            status=status,
            user_id=created_event.user_id,
            created_at=created_event.created_at,
            updated_at=created_event.updated_at
        )
    except DatabaseError:
        logger.error("Database error in create")
        raise


def modify(event_id: int, event_update: EventUpdate) -> EventResponse:
    """
    Update an existing event.

    Args:
        event_id: The ID of the event to update.
        event_update: EventUpdate schema with fields to update.

    Returns:
        Updated EventResponse object.

    Raises:
        NotFoundError: If event is not found.
        DatabaseError: If database operation fails.
    """
    try:
        existing_event = data.get_one(event_id)
        if existing_event is None:
            logger.warning(f"Event with id {event_id} not found")
            raise NotFoundError(f"Event with id {event_id} not found")

        # Update only provided fields
        if event_update.name is not None:
            existing_event.name = event_update.name
        if event_update.place is not None:
            existing_event.place = event_update.place
        if event_update.description is not None:
            existing_event.description = event_update.description
        if event_update.start_datetime is not None:
            existing_event.start_datetime = event_update.start_datetime
        if event_update.end_datetime is not None:
            existing_event.end_datetime = event_update.end_datetime
        if event_update.is_all_day is not None:
            existing_event.is_all_day = event_update.is_all_day

        modified_event = data.modify(existing_event)
        if modified_event:
            logger.info(f"Modified event with id {event_id}")
            status = EventStatusEnum(modified_event.status.value)
            return EventResponse(
                id=modified_event.id,
                name=modified_event.name,
                place=modified_event.place,
                description=modified_event.description,
                start_datetime=modified_event.start_datetime,
                end_datetime=modified_event.end_datetime,
                is_all_day=modified_event.is_all_day,
                status=status,
                user_id=modified_event.user_id,
                created_at=modified_event.created_at,
                updated_at=modified_event.updated_at
            )
        else:
            raise NotFoundError(f"Event with id {event_id} not found")
    except NotFoundError:
        raise
    except DatabaseError:
        logger.error(f"Database error in modify for event {event_id}")
        raise


def delete(event_id: int) -> bool:
    """
    Delete an event from the database.

    Args:
        event_id: The ID of the event to delete.

    Returns:
        True if event was deleted.

    Raises:
        NotFoundError: If event is not found.
        DatabaseError: If database operation fails.
    """
    try:
        existing_event = data.get_one(event_id)
        if existing_event is None:
            logger.warning(f"Event with id {event_id} not found for deletion")
            raise NotFoundError(f"Event with id {event_id} not found")

        result = data.delete(event_id)
        if result:
            logger.info(f"Deleted event with id {event_id}")
            return True
        else:
            raise NotFoundError(f"Event with id {event_id} not found")
    except NotFoundError:
        raise
    except DatabaseError:
        logger.error(f"Database error in delete for event {event_id}")
        raise


def change_status(event_id: int, new_status: EventStatusEnum) -> EventResponse:
    """
    Change an event's status.

    Args:
        event_id: The ID of the event.
        new_status: The new status to set.

    Returns:
        Updated EventResponse object.

    Raises:
        NotFoundError: If event is not found.
        DatabaseError: If database operation fails.
    """
    try:
        existing_event = data.get_one(event_id)
        if existing_event is None:
            logger.warning(f"Event with id {event_id} not found")
            raise NotFoundError(f"Event with id {event_id} not found")

        # Convert EventStatusEnum to EventStatus
        status_value = EventStatus(new_status.value)
        existing_event.status = status_value

        modified_event = data.modify(existing_event)
        if modified_event:
            logger.info(f"Changed status of event {event_id} to {new_status}")
            status = EventStatusEnum(modified_event.status.value)
            return EventResponse(
                id=modified_event.id,
                name=modified_event.name,
                place=modified_event.place,
                description=modified_event.description,
                start_datetime=modified_event.start_datetime,
                end_datetime=modified_event.end_datetime,
                is_all_day=modified_event.is_all_day,
                status=status,
                user_id=modified_event.user_id,
                created_at=modified_event.created_at,
                updated_at=modified_event.updated_at
            )
        else:
            raise NotFoundError(f"Event with id {event_id} not found")
    except NotFoundError:
        raise
    except DatabaseError:
        logger.error(f"Database error in change_status for event {event_id}")
        raise
