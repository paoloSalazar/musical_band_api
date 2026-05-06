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
from datetime import datetime
from decimal import Decimal
from schemas.event import EventCreate, EventUpdate, EventResponse, EventStatusEnum, EventCreator, PaginatedEventResponse
from models.event import Event, EventStatus
import data.event as data
import data.user as user_data
from exceptions import NotFoundError, DatabaseError, ConflictError

logger = logging.getLogger(__name__)


def check_event_conflict(
    start_datetime: datetime,
    end_datetime: datetime,
    is_all_day: bool,
    user_id: int,
    exclude_event_id: int | None = None
) -> bool:
    """
    Check if there's a conflicting event for the given time range.
    
    Args:
        start_datetime: Start datetime of the new event.
        end_datetime: End datetime of the new event.
        is_all_day: Whether the event is all-day.
        user_id: ID of the user creating the event.
        exclude_event_id: Optional event ID to exclude from conflict check (for updates).
    
    Returns:
        True if there's a conflict, False otherwise.
    
    Raises:
        ConflictError: If there's a conflicting event.
    """
    # Get events on the same date(s)
    start_date = start_datetime.strftime("%Y-%m-%d")
    end_date = end_datetime.strftime("%Y-%m-%d")
    
    # First check: any all-day event on this date (regardless of user)
    # All-day events block any other event on that date
    all_day_events = data.get_events_in_date_range(start_date, end_date, user_id=None)
    for event in all_day_events:
        if exclude_event_id and event.id == exclude_event_id:
            continue
        if event.is_all_day:
            raise ConflictError(
                f"Event conflicts with existing event '{event.name}' on {start_date}"
            )
    
    # Second check: for all-day events, also check for partial events on same date
    # All-day events block partial events on that date
    if is_all_day:
        # Get all events on this date (no user filter for all-day events)
        partial_events = data.get_events_in_date_range(start_date, end_date, user_id=None)
        for event in partial_events:
            if exclude_event_id and event.id == exclude_event_id:
                continue
            if not event.is_all_day:
                raise ConflictError(
                    f"Event conflicts with existing event '{event.name}' on {start_date}"
                )
    else:
        # Third check: for partial day events, check conflicts with same user's events
        existing_events = data.get_events_in_date_range(start_date, end_date, user_id)
        for event in existing_events:
            if exclude_event_id and event.id == exclude_event_id:
                continue
            
            # All-day events conflict with partial day events on same date
            if event.is_all_day:
                raise ConflictError(
                    f"Event conflicts with existing event '{event.name}' on {start_date}"
                )
            
            # For partial day events, check time overlap
            new_start = start_datetime if start_datetime.tzinfo is None else start_datetime.replace(tzinfo=None)
            new_end = end_datetime if end_datetime.tzinfo is None else end_datetime.replace(tzinfo=None)
            existing_start = event.start_datetime if event.start_datetime.tzinfo is None else event.start_datetime.replace(tzinfo=None)
            existing_end = event.end_datetime if event.end_datetime.tzinfo is None else event.end_datetime.replace(tzinfo=None)
            
            if new_start < existing_end and new_end > existing_start:
                raise ConflictError(
                    f"Event conflicts with existing event '{event.name}' "
                    f"({event.start_datetime.strftime('%H:%M')} - {event.end_datetime.strftime('%H:%M')}) "
                    f"on {start_date}"
                )
    
    return False


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
        # Use JOIN query to get event with user in single query
        event = data.get_one_with_user(event_id)
        if event is None:
            logger.warning(f"Event with id {event_id} not found")
            raise NotFoundError(f"Event with id {event_id} not found")
        
        # Map EventStatus to EventStatusEnum
        status = EventStatusEnum(event.status.value)
        
        # Get user info from loaded relationship
        creator = None
        if event.user:
            creator = EventCreator(
                user_id=event.user.id,
                name=event.user.name,
                lastname=event.user.lastname,
                email=event.user.email,
                phone_number=event.user.phone_number
            )
        
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
            created_by=creator,
            price=float(event.price) if event.price else None
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
        # Use JOIN query to get all events with users in single query
        events = data.get_all_with_users()
        result = []
        for event in events:
            status = EventStatusEnum(event.status.value)
            
            # Get user info from loaded relationship
            creator = None
            if event.user:
                creator = EventCreator(
                    user_id=event.user.id,
                    name=event.user.name,
                    lastname=event.user.lastname,
                    email=event.user.email,
                    phone_number=event.user.phone_number
                )
            
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
                created_by=creator,
                price=float(event.price) if event.price else None
            ))
        return result
    except DatabaseError:
        logger.error("Database error in get_all")
        raise


def get_paginated(
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
    search: str | None = None,
    user_id: int | None = None,
    start_after: datetime | None = None,
    end_before: datetime | None = None,
    sort_by: str = "created_at",
    order: str = "desc"
) -> PaginatedEventResponse:
    """
    Retrieve paginated and filtered events from the database.

    Args:
        page: Page number (1-indexed).
        limit: Number of items per page.
        status: Filter by event status.
        search: Search term for name and place fields.
        user_id: Filter by user ID.
        start_after: Filter events starting after this datetime.
        end_before: Filter events ending before this datetime.
        sort_by: Field to sort by (name, start_datetime, created_at).
        order: Sort order (asc or desc).

    Returns:
        PaginatedEventResponse object.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        # Convert status string to EventStatus enum if provided
        status_enum = None
        if status:
            status_enum = EventStatus(status)
        
        events, total = data.get_paginated(
            page=page,
            limit=limit,
            status=status_enum,
            search=search,
            user_id=user_id,
            start_after=start_after,
            end_before=end_before,
            sort_by=sort_by,
            order=order
        )
        
        result = []
        for event in events:
            event_status = EventStatusEnum(event.status.value)
            
            # Get user info from loaded relationship
            creator = None
            if event.user:
                creator = EventCreator(
                    user_id=event.user.id,
                    name=event.user.name,
                    lastname=event.user.lastname,
                    email=event.user.email,
                    phone_number=event.user.phone_number
                )
            
            result.append(EventResponse(
                id=event.id,
                name=event.name,
                place=event.place,
                description=event.description,
                start_datetime=event.start_datetime,
                end_datetime=event.end_datetime,
                is_all_day=event.is_all_day,
                status=event_status,
                user_id=event.user_id,
                created_by=creator,
                price=float(event.price) if event.price else None
            ))
        
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        
        return PaginatedEventResponse(
            items=result,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    except DatabaseError:
        logger.error("Database error in get_paginated")
        raise


def get_by_month(year: int, month: int, user_id: int | None = None) -> list[EventResponse]:
    """
    Retrieve events for a specific month (calendar view).

    Args:
        year: Year (e.g., 2026).
        month: Month (1-12).
        user_id: Optional user ID to filter events by owner.

    Returns:
        List of EventResponse objects for the specified month.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        events = data.get_events_by_month(year, month, user_id)
        
        result = []
        for event in events:
            event_status = EventStatusEnum(event.status.value)
            
            # Get user info from loaded relationship
            creator = None
            if event.user:
                creator = EventCreator(
                    user_id=event.user.id,
                    name=event.user.name,
                    lastname=event.user.lastname,
                    email=event.user.email,
                    phone_number=event.user.phone_number
                )
            
            result.append(EventResponse(
                id=event.id,
                name=event.name,
                place=event.place,
                description=event.description,
                start_datetime=event.start_datetime,
                end_datetime=event.end_datetime,
                is_all_day=event.is_all_day,
                status=event_status,
                user_id=event.user_id,
                created_by=creator,
                price=float(event.price) if event.price else None
            ))
        
        return result
    except DatabaseError:
        logger.error(f"Database error in get_by_month for {year}-{month}")
        raise


def create(event_create: EventCreate) -> EventResponse:
    """
    Create a new event in the database.

    Args:
        event_create: EventCreate schema with event data.

    Returns:
        Created EventResponse object.

    Raises:
        ConflictError: If there's a conflicting event.
        DatabaseError: If database operation fails.
    """
    try:
        # Validate event dates
        if event_create.start_datetime >= event_create.end_datetime:
            raise ConflictError("End datetime must be after start datetime")

        # Validate event is not in the past
        if event_create.start_datetime < datetime.now():
            raise ConflictError("Cannot create events in the past")

        # Check for conflicting events
        if event_create.user_id is not None:
            check_event_conflict(
                start_datetime=event_create.start_datetime,
                end_datetime=event_create.end_datetime,
                is_all_day=event_create.is_all_day,
                user_id=event_create.user_id
            )
        
        event = Event(
            name=event_create.name,
            place=event_create.place,
            description=event_create.description,
            start_datetime=event_create.start_datetime,
            end_datetime=event_create.end_datetime,
            is_all_day=event_create.is_all_day,
            user_id=event_create.user_id,
            status=EventStatus.PENDING,
            price=Decimal(str(event_create.price)) if event_create.price is not None else Decimal("0.00")
        )
        
        created_event = data.create(event)
        logger.info(f"Created event with id {created_event.id}")
        
        status = EventStatusEnum(created_event.status.value)
        
        # Get user info
        creator = None
        if created_event.user_id:
            user = user_data.get_one_by_id(created_event.user_id)
            if user:
                creator = EventCreator(
                    user_id=user.id,
                    name=user.name,
                    lastname=user.lastname,
                    email=user.email,
                    phone_number=user.phone_number
                )
        
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
            created_by=creator,
            price=float(created_event.price) if created_event.price else None
        )
    except ConflictError:
        raise
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
        ConflictError: If there's a conflicting event.
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
        
        # Check for conflicts if datetime or is_all_day is being updated
        new_start = event_update.start_datetime if event_update.start_datetime is not None else existing_event.start_datetime
        new_end = event_update.end_datetime if event_update.end_datetime is not None else existing_event.end_datetime
        new_is_all_day = event_update.is_all_day if event_update.is_all_day is not None else existing_event.is_all_day
        
        # Validate event dates
        if new_start >= new_end:
            raise ConflictError("End datetime must be after start datetime")
        
        # Check for conflicting events (excluding the current event)
        check_event_conflict(
            start_datetime=new_start,
            end_datetime=new_end,
            is_all_day=new_is_all_day,
            user_id=existing_event.user_id,
            exclude_event_id=event_id
        )
        
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
            # Get user info
            creator = None
            if modified_event.user_id:
                user = user_data.get_one_by_id(modified_event.user_id)
                if user:
                    creator = EventCreator(
                        user_id=user.id,
                        name=user.name,
                        lastname=user.lastname,
                        email=user.email
                    )
            
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
                created_by=creator,
                price=float(modified_event.price) if modified_event.price else None
            )
        else:
            raise NotFoundError(f"Event with id {event_id} not found")
    except NotFoundError:
        raise
    except ConflictError:
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
            # Get user info
            creator = None
            if modified_event.user_id:
                user = user_data.get_one_by_id(modified_event.user_id)
                if user:
                    creator = EventCreator(
                        user_id=user.id,
                        name=user.name,
                        lastname=user.lastname,
                        email=user.email
                    )
            
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
                created_by=creator,
                price=float(modified_event.price) if modified_event.price else None
            )
        else:
            raise NotFoundError(f"Event with id {event_id} not found")
    except NotFoundError:
        raise
    except DatabaseError:
        logger.error(f"Database error in change_status for event {event_id}")
        raise


def set_price(event_id: int, price: Decimal) -> EventResponse:
    """
    Set the price of an event.

    Args:
        event_id: The ID of the event.
        price: The new price to set.

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

        modified_event = data.set_price(event_id, price)
        if modified_event:
            logger.info(f"Set price {price} on event {event_id}")
            status = EventStatusEnum(modified_event.status.value)
            # Get user info
            creator = None
            if modified_event.user_id:
                user = user_data.get_one_by_id(modified_event.user_id)
                if user:
                    creator = EventCreator(
                        user_id=user.id,
                        name=user.name,
                        lastname=user.lastname,
                        email=user.email
                    )
            
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
                created_by=creator,
                price=float(modified_event.price) if modified_event.price else None
            )
        else:
            raise NotFoundError(f"Event with id {event_id} not found")
    except NotFoundError:
        raise
    except DatabaseError:
        logger.error(f"Database error in set_price for event {event_id}")
        raise


def get_price(event_id: int) -> Decimal | None:
    """
    Get the price of an event.

    Args:
        event_id: The ID of the event.

    Returns:
        The price as Decimal, or None if not set.

    Raises:
        NotFoundError: If event is not found.
        DatabaseError: If database operation fails.
    """
    try:
        existing_event = data.get_one(event_id)
        if existing_event is None:
            logger.warning(f"Event with id {event_id} not found")
            raise NotFoundError(f"Event with id {event_id} not found")

        price = data.get_price(event_id)
        return price
    except NotFoundError:
        raise
    except DatabaseError:
        logger.error(f"Database error in get_price for event {event_id}")
        raise
