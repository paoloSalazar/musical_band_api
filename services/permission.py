"""
Service layer for Permission business logic.

Provides business logic operations for permission management,
including validation, role-permission assignment, and data transformation.

Functions:
    - get_all: Get all permissions
    - get_one: Get permission by ID
    - get_by_name: Get permission by name
    - create: Create a new permission
    - update: Update a permission
    - delete: Delete a permission
    - assign_permission_to_role: Assign permission to role
    - remove_permission_from_role: Remove permission from role
    - get_role_permissions: Get all permissions for a role
    - get_permission_roles: Get all roles for a permission
"""

import logging
from typing import List
from models.permission import Permission
from schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
import data.permission as data
from exceptions import NotFoundError, ConflictError, DatabaseError

logger = logging.getLogger(__name__)


def get_all() -> list[PermissionResponse]:
    """
    Retrieve all permissions from the database.

    Returns:
        List of PermissionResponse objects.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        db_permissions = data.get_all()
        permissions = [PermissionResponse.model_validate(p) for p in db_permissions]
        return permissions
    except DatabaseError as e:
        logger.error(f"Error getting all permissions: {e}")
        raise


def get_one(permission_id: int) -> PermissionResponse:
    """
    Retrieve a permission by its ID.

    Args:
        permission_id: The unique identifier of the permission.

    Returns:
        PermissionResponse object.

    Raises:
        NotFoundError: If permission is not found.
        DatabaseError: If database operation fails.
    """
    try:
        db_permission = data.get_one(permission_id)
        if not db_permission:
            raise NotFoundError(f"Permission with ID {permission_id} not found")
        return PermissionResponse.model_validate(db_permission)
    except DatabaseError as e:
        logger.error(f"Error getting permission {permission_id}: {e}")
        raise


def get_by_name(name: str) -> PermissionResponse | None:
    """
    Retrieve a permission by its name.

    Args:
        name: The unique name of the permission (e.g., "users:read").

    Returns:
        PermissionResponse object if found, None otherwise.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        db_permission = data.get_by_name(name)
        if not db_permission:
            return None
        return PermissionResponse.model_validate(db_permission)
    except DatabaseError as e:
        logger.error(f"Error getting permission by name {name}: {e}")
        raise


def create(permission_create: PermissionCreate) -> PermissionResponse:
    """
    Create a new permission in the database.

    Args:
        permission_create: PermissionCreate schema with permission data.

    Returns:
        Created PermissionResponse object.

    Raises:
        ConflictError: If permission with name already exists.
        DatabaseError: If database operation fails.
    """
    try:
        # Check if permission with same name exists
        existing = data.get_by_name(permission_create.name)
        if existing:
            raise ConflictError(f"Permission with name '{permission_create.name}' already exists")

        # Create new permission
        db_permission = Permission(
            name=permission_create.name,
            description=permission_create.description
        )
        created_permission = data.create(db_permission)
        return PermissionResponse.model_validate(created_permission)
    except DatabaseError as e:
        logger.error(f"Error creating permission: {e}")
        raise


def update(permission_id: int, permission_update: PermissionUpdate) -> PermissionResponse:
    """
    Update an existing permission.

    Args:
        permission_id: The ID of the permission to update.
        permission_update: PermissionUpdate schema with fields to update.

    Returns:
        Updated PermissionResponse object.

    Raises:
        NotFoundError: If permission is not found.
        DatabaseError: If database operation fails.
    """
    try:
        db_permission = data.get_one(permission_id)
        if not db_permission:
            raise NotFoundError(f"Permission with ID {permission_id} not found")

        updated_permission = data.update(permission_id, permission_update)
        return PermissionResponse.model_validate(updated_permission)
    except DatabaseError as e:
        logger.error(f"Error updating permission {permission_id}: {e}")
        raise


def delete(permission_id: int) -> bool:
    """
    Delete a permission from the database.

    Args:
        permission_id: The ID of the permission to delete.

    Returns:
        True if deleted successfully.

    Raises:
        NotFoundError: If permission is not found.
        DatabaseError: If database operation fails.
    """
    try:
        db_permission = data.get_one(permission_id)
        if not db_permission:
            raise NotFoundError(f"Permission with ID {permission_id} not found")
        return data.delete(permission_id)
    except DatabaseError as e:
        logger.error(f"Error deleting permission {permission_id}: {e}")
        raise


# ============================================
# Role-Permission Assignment Functions
# ============================================


def assign_permission_to_role(permission_id: int, role_id: int) -> bool:
    """
    Assign a permission to a role.

    Args:
        permission_id: The ID of the permission to assign.
        role_id: The ID of the role to assign the permission to.

    Returns:
        True if successful.

    Raises:
        DatabaseError: If operation fails.
    """
    try:
        return data.assign_permission_to_role(permission_id, role_id)
    except DatabaseError as e:
        logger.error(f"Error assigning permission {permission_id} to role {role_id}: {e}")
        raise


def remove_permission_from_role(permission_id: int, role_id: int) -> bool:
    """
    Remove a permission from a role.

    Args:
        permission_id: The ID of the permission to remove.
        role_id: The ID of the role to remove the permission from.

    Returns:
        True if successful.

    Raises:
        DatabaseError: If operation fails.
    """
    try:
        return data.remove_permission_from_role(permission_id, role_id)
    except DatabaseError as e:
        logger.error(f"Error removing permission {permission_id} from role {role_id}: {e}")
        raise


def get_role_permissions(role_id: int) -> list[PermissionResponse]:
    """
    Get all permissions assigned to a role.

    Args:
        role_id: The ID of the role.

    Returns:
        List of PermissionResponse objects.

    Raises:
        DatabaseError: If operation fails.
    """
    try:
        db_permissions = data.get_role_permissions(role_id)
        return [PermissionResponse.model_validate(p) for p in db_permissions]
    except DatabaseError as e:
        logger.error(f"Error getting permissions for role {role_id}: {e}")
        raise


def get_permission_roles(permission_id: int) -> list[dict]:
    """
    Get all roles that have a specific permission.

    Args:
        permission_id: The ID of the permission.

    Returns:
        List of role dictionaries.

    Raises:
        DatabaseError: If operation fails.
    """
    try:
        return data.get_permission_roles(permission_id)
    except DatabaseError as e:
        logger.error(f"Error getting roles for permission {permission_id}: {e}")
        raise
