"""
Service layer for MusicianAvailability business logic.

Provides business logic operations for musician availability management,
including validation, authorization, and data transformation.

Functions:
    - get_by_musician: Get availability for a musician (with authorization)
    - get_musician_availability_by_month: Get monthly availability for a musician (with authorization)
    - get_all_by_date: Get all musicians unavailable on a date (admin only)
    - create: Create new availability entry (musician only)
    - create_bulk: Create multiple entries (musician only)
    - update: Update availability entry (owner or admin)
    - delete: Delete availability entry (owner or admin)
    - check_availability: Check if musician is available on a date
"""

import logging
from datetime import date
from typing import List, Optional

from schemas.musician_availability import (
    MusicianAvailabilityCreate,
    MusicianAvailabilityUpdate,
    MusicianAvailabilityResponse,
    MusicianAvailabilitySummaryResponse,
    MusicianAvailabilityMonthlyResponse
)
import data.musician_availability as data
import data.user as user_data
from models.musician_availability import MusicianAvailability
from exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ValidationError
)

logger = logging.getLogger(__name__)


def get_by_musician(musician_id: int, current_user: dict) -> List[MusicianAvailabilityResponse]:
    """
    Retrieve all availability entries for a specific musician.

    Authorization:
    - Musicians and auxiliar_musicians can only view their own availability
    - Admins can view anyone's availability

    Args:
        musician_id: The ID of the musician.
        current_user: Current authenticated user dict with 'id', 'role', 'permissions'.

    Returns:
        List of MusicianAvailabilityResponse objects.

    Raises:
        UnauthorizedError: If user lacks permission to view availability.
        DatabaseError: If database operation fails.
    """
    # Authorization check
    current_user_id = current_user.get('id')
    user_role = current_user.get('role')

    if user_role not in ['admin'] and current_user_id != musician_id:
        logger.warning(f"User {current_user_id} with role {user_role} attempted to view availability for musician {musician_id}")
        raise UnauthorizedError("You can only view your own availability")

    try:
        db_availabilities = data.get_by_musician(musician_id)
        availabilities = [
            MusicianAvailabilityResponse.model_validate(av) for av in db_availabilities
        ]
        logger.info(f"Retrieved {len(availabilities)} availability entries for musician {musician_id}")
        return availabilities
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error(f"Service error in get_by_musician for musician {musician_id}")
        raise DatabaseError("Service error")


def get_musician_availability_by_month(musician_id: int, year: int, month: int, current_user: dict) -> MusicianAvailabilityMonthlyResponse:
    """
    Retrieve all unavailable dates for a musician within a specific month.

    Authorization:
    - Musicians and auxiliar_musicians can only view their own availability
    - Admins can view anyone's availability

    Args:
        musician_id: The ID of the musician.
        year: The year to query.
        month: The month to query (1-12).
        current_user: Current authenticated user dict with 'id', 'role', 'permissions'.

    Returns:
        MusicianAvailabilityMonthlyResponse with unavailable dates for the month.

    Raises:
        UnauthorizedError: If user lacks permission to view availability.
        ValidationError: If year/month are invalid.
        DatabaseError: If database operation fails.
    """
    # Validate year and month
    if not (1 <= month <= 12):
        raise ValidationError("Month must be between 1 and 12")
    if year < 2000 or year > 2100:
        raise ValidationError("Year must be between 2000 and 2100")

    # Authorization check
    current_user_id = current_user.get('id')
    user_role = current_user.get('role')

    if user_role not in ['admin'] and current_user_id != musician_id:
        logger.warning(f"User {current_user_id} with role {user_role} attempted to view monthly availability for musician {musician_id}")
        raise UnauthorizedError("You can only view your own availability")

    try:
        unavailable_dates = data.get_musician_availability_by_month(musician_id, year, month)
        response = MusicianAvailabilityMonthlyResponse(
            musician_id=musician_id,
            year=year,
            month=month,
            unavailable_dates=unavailable_dates
        )
        logger.info(f"Retrieved {len(unavailable_dates)} unavailable dates for musician {musician_id} in {year}-{month}")
        return response
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error(f"Service error in get_musician_availability_by_month for musician {musician_id} in {year}-{month}")
        raise DatabaseError("Service error")


def get_all_by_date(check_date: date, current_user: dict) -> List[MusicianAvailabilityResponse]:
    """
    Retrieve all musicians unavailable on a specific date.

    Authorization:
    - Only admins can view all musicians' availability

    Args:
        check_date: The date to check.
        current_user: Current authenticated user dict.

    Returns:
        List of MusicianAvailabilityResponse objects for the date.

    Raises:
        UnauthorizedError: If user is not admin.
        DatabaseError: If database operation fails.
    """
    # Authorization check
    user_role = current_user.get('role')

    if user_role != 'admin':
        logger.warning(f"User {current_user.get('id')} attempted to view all availability for date {check_date}")
        raise UnauthorizedError("Only administrators can view all musicians' availability")

    try:
        db_availabilities = data.get_all_by_date(check_date)
        availabilities = [
            MusicianAvailabilityResponse.model_validate(av) for av in db_availabilities
        ]
        logger.info(f"Retrieved {len(availabilities)} unavailable musicians for date {check_date}")
        return availabilities
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error(f"Service error in get_all_by_date for date {check_date}")
        raise DatabaseError("Service error")


def check_availability(musician_id: int, check_date: date, current_user: dict) -> bool:
    """
    Check if a musician is available on a specific date.

    Authorization:
    - Anyone can check availability (used for scheduling validation)

    Args:
        musician_id: The ID of the musician.
        check_date: The date to check.
        current_user: Current authenticated user dict.

    Returns:
        True if available, False if unavailable.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        is_available = data.check_availability(musician_id, check_date)
        logger.info(f"Checked availability for musician {musician_id} on {check_date}: {'available' if is_available else 'unavailable'}")
        return is_available
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error(f"Service error in check_availability for musician {musician_id} on {check_date}")
        raise DatabaseError("Service error")


def create(availability_create: MusicianAvailabilityCreate, current_user: dict) -> MusicianAvailabilityResponse:
    """
    Create a new availability entry for a musician.

    Authorization:
    - Musicians and auxiliar_musicians can only create availability for themselves
    - Admins can create availability for any musician

    Args:
        availability_create: MusicianAvailabilityCreate schema.
        current_user: Current authenticated user dict.

    Returns:
        Created MusicianAvailabilityResponse object.

    Raises:
        UnauthorizedError: If user lacks permission to create availability.
        ConflictError: If availability already exists for this musician/date.
        ValidationError: If date validation fails.
        DatabaseError: If database operation fails.
    """
    # Authorization check
    current_user_id = current_user.get('id')
    user_role = current_user.get('role')

    if user_role not in ['admin'] and current_user_id != availability_create.musician_id:
        logger.warning(f"User {current_user_id} with role {user_role} attempted to create availability for musician {availability_create.musician_id}")
        raise UnauthorizedError("You can only manage your own availability")

    # Validate unavailable_date is not in the past
    if availability_create.unavailable_date < date.today():
        raise ValidationError('Unavailable date cannot be in the past')

    # Check if musician exists
    try:
        musician = user_data.get_one_by_id(availability_create.musician_id)
        if not musician:
            raise NotFoundError(f"Musician with id {availability_create.musician_id} not found")
    except (DatabaseError, DatabaseConnectionError):
        raise NotFoundError(f"Musician with id {availability_create.musician_id} not found")

    # Check if availability already exists
    try:
        existing = data.get_by_musician_and_date(availability_create.musician_id, availability_create.unavailable_date)
        if existing:
            raise ConflictError(f"Availability already exists for musician {availability_create.musician_id} on {availability_create.unavailable_date}")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error checking existing availability")
        raise DatabaseError("Service error")

    # New validation: block unavailable date if musician assigned to event that day
    event_name = data.check_musician_event_assignment(
        availability_create.musician_id, availability_create.unavailable_date
    )
    if event_name:
        raise ConflictError(f"Cannot mark date unavailable – assigned to event '{event_name}' on this date")

    try:
        db_availability = MusicianAvailability(
            musician_id=availability_create.musician_id,
            unavailable_date=availability_create.unavailable_date,
            reason=availability_create.reason
        )
        created_db_availability = data.create(db_availability)
        availability = MusicianAvailabilityResponse.model_validate(created_db_availability)
        logger.info(f"Created availability for musician {availability_create.musician_id} on {availability_create.unavailable_date}")
        return availability
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in create")
        raise DatabaseError("Service error")


def create_bulk(availabilities_create: List[MusicianAvailabilityCreate], current_user: dict) -> List[MusicianAvailabilityResponse]:
    """
    Create multiple availability entries for a musician.

    Authorization:
    - Musicians and auxiliar_musicians can only create availability for themselves
    - Admins can create availability for any musician

    Args:
        availabilities_create: List of MusicianAvailabilityCreate schemas.
        current_user: Current authenticated user dict.

    Returns:
        List of created MusicianAvailabilityResponse objects.

    Raises:
        UnauthorizedError: If user lacks permission to create availability.
        ConflictError: If any availability already exists.
        ValidationError: If date validation fails.
        DatabaseError: If database operation fails.
    """
    if not availabilities_create:
        return []

    # Authorization check
    current_user_id = current_user.get('id')
    user_role = current_user.get('role')
    musician_id = availabilities_create[0].musician_id

    # Check all entries are for the same musician
    for av in availabilities_create:
        if av.musician_id != musician_id:
            raise ValidationError("All availability entries must be for the same musician")

    if user_role not in ['admin'] and current_user_id != musician_id:
        logger.warning(f"User {current_user_id} with role {user_role} attempted to bulk create availability for musician {musician_id}")
        raise UnauthorizedError("You can only manage your own availability")

    # Validate all unavailable_dates are not in the past
    for av in availabilities_create:
        if av.unavailable_date < date.today():
            raise ValidationError('Unavailable date cannot be in the past')

    # Check if musician exists
    try:
        musician = user_data.get_one_by_id(musician_id)
        if not musician:
            raise NotFoundError(f"Musician with id {musician_id} not found")
    except (DatabaseError, DatabaseConnectionError):
        raise NotFoundError(f"Musician with id {musician_id} not found")

    # Check for existing availabilities
    conflict_dates = []
    for av_create in availabilities_create:
        try:
            existing = data.get_by_musician_and_date(musician_id, av_create.unavailable_date)
            if existing:
                conflict_dates.append(str(av_create.unavailable_date))
        except (DatabaseError, DatabaseConnectionError):
            continue

    if conflict_dates:
        raise ConflictError(f"Availability already exists for dates: {', '.join(conflict_dates)}")

    # New validation: block any date where musician is assigned to an event
    for av_create in availabilities_create:
        event_name = data.check_musician_event_assignment(musician_id, av_create.unavailable_date)
        if event_name:
            raise ConflictError(f"Cannot mark date unavailable – assigned to event '{event_name}' on {av_create.unavailable_date}")

    try:
        db_availabilities = [
            MusicianAvailability(
                musician_id=av.musician_id,
                unavailable_date=av.unavailable_date,
                reason=av.reason
            ) for av in availabilities_create
        ]
        created_db_availabilities = data.create_bulk(db_availabilities)
        availabilities = [
            MusicianAvailabilityResponse.model_validate(av) for av in created_db_availabilities
        ]
        logger.info(f"Bulk created {len(availabilities)} availability entries for musician {musician_id}")
        return availabilities
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in create_bulk")
        raise DatabaseError("Service error")


def update(availability_id: int, availability_update: MusicianAvailabilityUpdate, current_user: dict) -> MusicianAvailabilityResponse:
    """
    Update an existing availability entry.

    Authorization:
    - Musicians and auxiliar_musicians can only update their own availability
    - Admins can update anyone's availability

    Args:
        availability_id: The ID of the availability entry to update.
        availability_update: MusicianAvailabilityUpdate schema.
        current_user: Current authenticated user dict.

    Returns:
        Updated MusicianAvailabilityResponse object.

    Raises:
        NotFoundError: If availability entry not found.
        UnauthorizedError: If user lacks permission to update.
        ConflictError: If updating to a date that already exists.
        DatabaseError: If database operation fails.
    """
    # Get the existing availability
    try:
        existing_db = data.get_by_id(availability_id)
        if not existing_db:
            raise NotFoundError(f"Availability entry with id {availability_id} not found")
    except (DatabaseError, DatabaseConnectionError):
        raise NotFoundError(f"Availability entry with id {availability_id} not found")

    # Authorization check
    current_user_id = current_user.get('id')
    user_role = current_user.get('role')

    if user_role not in ['admin'] and current_user_id != existing_db.musician_id:
        logger.warning(f"User {current_user_id} with role {user_role} attempted to update availability for musician {existing_db.musician_id}")
        raise UnauthorizedError("You can only manage your own availability")

    # Validate unavailable_date is not in the past if being updated
    if availability_update.unavailable_date and availability_update.unavailable_date < date.today():
        raise ValidationError('Unavailable date cannot be in the past')

    # Check for conflicts if date is being updated
    if availability_update.unavailable_date and availability_update.unavailable_date != existing_db.unavailable_date:
        try:
            conflict = data.get_by_musician_and_date(existing_db.musician_id, availability_update.unavailable_date)
            if conflict:
                raise ConflictError(f"Availability already exists for musician {existing_db.musician_id} on {availability_update.unavailable_date}")
        except (DatabaseError, DatabaseConnectionError) as e:
            logger.error("Service error checking for conflicts")
            raise DatabaseError("Service error")

    try:
        # Update the fields
        update_data = availability_update.model_dump(exclude_unset=True)
        updated_db = data.update(existing_db, update_data)
        if updated_db:
            availability = MusicianAvailabilityResponse.model_validate(updated_db)
            logger.info(f"Updated availability {availability_id} for musician {existing_db.musician_id}")
            return availability
        else:
            raise NotFoundError(f"Availability entry with id {availability_id} not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in update")
        raise DatabaseError("Service error")


def delete(availability_id: int, current_user: dict) -> bool:
    """
    Delete an availability entry.

    Authorization:
    - Musicians and auxiliar_musicians can only delete their own availability
    - Admins can delete anyone's availability

    Args:
        availability_id: The ID of the availability entry to delete.
        current_user: Current authenticated user dict.

    Returns:
        True if deleted successfully.

    Raises:
        NotFoundError: If availability entry not found.
        UnauthorizedError: If user lacks permission to delete.
        DatabaseError: If database operation fails.
    """
    # Get the availability to check ownership
    try:
        existing_db = data.get_by_id(availability_id)
        if not existing_db:
            raise NotFoundError(f"Availability entry with id {availability_id} not found")
    except (DatabaseError, DatabaseConnectionError):
        raise NotFoundError(f"Availability entry with id {availability_id} not found")

    # Authorization check
    current_user_id = current_user.get('id')
    user_role = current_user.get('role')

    if user_role not in ['admin'] and current_user_id != existing_db.musician_id:
        logger.warning(f"User {current_user_id} with role {user_role} attempted to delete availability for musician {existing_db.musician_id}")
        raise UnauthorizedError("You can only manage your own availability")

    try:
        result = data.delete(availability_id)
        if result:
            logger.info(f"Deleted availability {availability_id} for musician {existing_db.musician_id}")
            return True
        else:
            raise NotFoundError(f"Availability entry with id {availability_id} not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in delete")
        raise DatabaseError("Service error")


def delete_by_musician_and_date(musician_id: int, unavailable_date: date, current_user: dict) -> bool:
    """
    Delete a specific availability entry by musician and date.

    Authorization:
    - Musicians and auxiliar_musicians can only delete their own availability
    - Admins can delete anyone's availability

    Args:
        musician_id: The ID of the musician.
        unavailable_date: The date of the availability entry.
        current_user: Current authenticated user dict.

    Returns:
        True if deleted successfully.

    Raises:
        NotFoundError: If availability entry not found.
        UnauthorizedError: If user lacks permission to delete.
        DatabaseError: If database operation fails.
    """
    # Authorization check
    current_user_id = current_user.get('id')
    user_role = current_user.get('role')

    if user_role not in ['admin'] and current_user_id != musician_id:
        logger.warning(f"User {current_user_id} with role {user_role} attempted to delete availability for musician {musician_id}")
        raise UnauthorizedError("You can only manage your own availability")

    try:
        # Check if availability exists
        existing = data.get_by_musician_and_date(musician_id, unavailable_date)
        if not existing:
            raise NotFoundError(f"Availability not found for musician {musician_id} on {unavailable_date}")

        result = data.delete_by_musician_and_date(musician_id, unavailable_date)
        if result:
            logger.info(f"Deleted availability for musician {musician_id} on {unavailable_date}")
            return True
        else:
            raise NotFoundError(f"Availability not found for musician {musician_id} on {unavailable_date}")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in delete_by_musician_and_date")
        raise DatabaseError("Service error")