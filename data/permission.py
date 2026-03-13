"""
Data access layer for Permission entities.

Provides CRUD operations and role-permission relationship management
for the Musical Band API.

Functions:
    - get_one: Get permission by ID
    - get_by_name: Get permission by name
    - get_all: Get all permissions
    - create: Create a new permission
    - update: Update an existing permission
    - delete: Delete a permission
    - assign_permission_to_role: Assign permission to role
    - remove_permission_from_role: Remove permission from role
    - get_role_permissions: Get all permissions for a role
    - get_permission_roles: Get all roles for a permission
    - user_has_permission: Check if user has specific permission
    - user_has_any_permission: Check if user has any permission
    - get_user_permissions: Get all permissions for a user
"""

import logging
from config.database import SessionLocal
from models.permission import Permission
from models.user_role import UserRole
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError, IntegrityError
from exceptions import DatabaseError, DatabaseConnectionError, ConflictError

logger = logging.getLogger(__name__)


def get_one(permission_id: int) -> Permission | None:
    """
    Retrieve a permission by its ID.

    Args:
        permission_id: The unique identifier of the permission.

    Returns:
        The Permission object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(Permission).filter(Permission.id == permission_id).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting permission '{permission_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting permission '{permission_id}'")
        raise DatabaseError("Failed to get permission")
    finally:
        db.close()


def get_by_name(name: str) -> Permission | None:
    """
    Retrieve a permission by its name.

    Args:
        name: The unique name of the permission (e.g., "users:read").

    Returns:
        The Permission object if found, None otherwise.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        return db.query(Permission).filter(Permission.name == name).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting permission '{name}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting permission '{name}'")
        raise DatabaseError("Failed to get permission")
    finally:
        db.close()


def get_all(skip: int = 0, limit: int = 20) -> tuple[list[Permission], int]:
    """
    Retrieve permissions from the database with pagination.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        Tuple of (list of Permission objects, total count).

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        # Get total count
        total = db.query(Permission).count()
        # Get paginated results
        permissions = db.query(Permission).offset(skip).limit(limit).all()
        return permissions, total
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting all permissions")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while getting all permissions")
        raise DatabaseError("Failed to get all permissions")
    finally:
        db.close()


def create(permission: Permission) -> Permission:
    """
    Create a new permission in the database.

    Args:
        permission: The Permission object to create.

    Returns:
        The created Permission object.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while creating permission '{permission.name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating permission '{permission.name}'")
        db.rollback()
        raise DatabaseError("Failed to create permission")
    finally:
        db.close()


def update(permission_id: int, permission) -> Permission:
    """
    Update an existing permission.

    Args:
        permission_id: The ID of the permission to update.
        permission: The PermissionUpdate schema with updated fields.

    Returns:
        The updated Permission object, or None if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if db_permission:
            update_data = permission.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_permission, key, value)
            db.commit()
            db.refresh(db_permission)
        return db_permission
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while updating permission '{permission_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating permission '{permission_id}'")
        db.rollback()
        raise DatabaseError("Failed to update permission")
    finally:
        db.close()


def delete(permission_id: int) -> bool:
    """
    Delete a permission from the database.

    Args:
        permission_id: The ID of the permission to delete.

    Returns:
        True if deleted, False if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
    """
    db = SessionLocal()
    try:
        db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if db_permission:
            db.delete(db_permission)
            db.commit()
            return True
        return False
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while deleting permission '{permission_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting permission '{permission_id}'")
        db.rollback()
        raise DatabaseError("Failed to delete permission")
    finally:
        db.close()


def delete_by_name(name: str) -> bool:
    """
    Delete a permission from the database by its name.

    Args:
        name: The name of the permission to delete.

    Returns:
        True if deleted, False if not found.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If database operation fails.
        ConflictError: If permission is assigned to roles.
    """
    db = SessionLocal()
    try:
        db_permission = db.query(Permission).filter(Permission.name == name).first()
        if not db_permission:
            return False
        
        # Check if permission is assigned to any roles BEFORE attempting delete
        # This prevents cascade delete and gives a friendly error message
        if db_permission.roles:
            assigned_roles = [role.name for role in db_permission.roles]
            roles_str = "', '".join(assigned_roles)
            raise ConflictError(
                f"Permission '{name}' is already assigned to role(s): '{roles_str}'. "
                f"Remove the permission from these roles before deleting."
            )
        
        db.delete(db_permission)
        db.commit()
        return True
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while deleting permission '{name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except IntegrityError as e:
        db.rollback()
        # Check if this is a foreign key constraint violation
        error_msg = str(e).lower()
        if 'foreign key constraint' in error_msg or 'restrict' in error_msg:
            # Get the roles that have this permission assigned
            assigned_roles = []
            try:
                db2 = SessionLocal()
                permission = db2.query(Permission).filter(Permission.name == name).first()
                if permission:
                    assigned_roles = [role.name for role in permission.roles]
                db2.close()
            except Exception:
                pass
            
            if assigned_roles:
                roles_str = "', '".join(assigned_roles)
                raise ConflictError(
                    f"Permission '{name}' is already assigned to role(s): '{roles_str}'. "
                    f"Remove the permission from these roles before deleting."
                )
            raise ConflictError(f"Permission '{name}' cannot be deleted because it is in use")
        logger.error(f"Integrity error while deleting permission '{name}': {e}")
        raise DatabaseError("Failed to delete permission due to data integrity issue")
    except ConflictError:
        # Re-raise ConflictError as-is
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting permission '{name}'")
        db.rollback()
        raise DatabaseError("Failed to delete permission")
    finally:
        db.close()


# ============================================
# Role-Permission Assignment Functions
# ============================================


def assign_permission_to_role(permission_id: int, role_id: int) -> bool:
    """
    Assign a permission to a role.

    Creates a many-to-many relationship between the permission and role.

    Args:
        permission_id: The ID of the permission to assign.
        role_id: The ID of the role to assign the permission to.

    Returns:
        True if successful.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If operation fails or permission/role not found.
    """
    db = SessionLocal()
    try:
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        role = db.query(UserRole).filter(UserRole.id == role_id).first()

        if not permission:
            logger.error(f"Permission with ID {permission_id} not found")
            raise DatabaseError("Failed to assign permission: permission not found")

        if not role:
            logger.error(f"Role with ID {role_id} not found")
            raise DatabaseError("Failed to assign permission: role not found")

        if permission not in role.permissions:
            role.permissions.append(permission)
            db.commit()
            logger.info(f"Permission '{permission.name}' assigned to role '{role.name}'")

        return True
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while assigning permission '{permission_id}' to role '{role_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while assigning permission '{permission_id}' to role '{role_id}'")
        db.rollback()
        raise DatabaseError("Failed to assign permission")
    finally:
        db.close()


def remove_permission_from_role(permission_id: int, role_id: int) -> bool:
    """
    Remove a permission from a role.

    Removes the many-to-many relationship between the permission and role.

    Args:
        permission_id: The ID of the permission to remove.
        role_id: The ID of the role to remove the permission from.

    Returns:
        True if successful.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If operation fails or permission/role not found.
    """
    db = SessionLocal()
    try:
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        role = db.query(UserRole).filter(UserRole.id == role_id).first()

        if not permission:
            logger.error(f"Permission with ID {permission_id} not found")
            raise DatabaseError("Failed to remove permission: permission not found")

        if not role:
            logger.error(f"Role with ID {role_id} not found")
            raise DatabaseError("Failed to remove permission: role not found")

        if permission in role.permissions:
            role.permissions.remove(permission)
            db.commit()
            logger.info(f"Permission '{permission.name}' removed from role '{role.name}'")

        return True
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while removing permission '{permission_id}' from role '{role_id}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while removing permission '{permission_id}' from role '{role_id}'")
        db.rollback()
        raise DatabaseError("Failed to remove permission")
    finally:
        db.close()


def get_role_permissions(role_id: int) -> list[Permission]:
    """
    Get all permissions assigned to a role.

    Args:
        role_id: The ID of the role.

    Returns:
        List of Permission objects assigned to the role.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If operation fails or role not found.
    """
    db = SessionLocal()
    try:
        role = db.query(UserRole).filter(UserRole.id == role_id).first()

        if not role:
            logger.error(f"Role with ID {role_id} not found")
            raise DatabaseError("Failed to get role permissions: role not found")

        return role.permissions
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting permissions for role '{role_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting permissions for role '{role_id}'")
        raise DatabaseError("Failed to get role permissions")
    finally:
        db.close()


def get_permission_roles(permission_id: int) -> list[UserRole]:
    """
    Get all roles that have a specific permission.

    Args:
        permission_id: The ID of the permission.

    Returns:
        List of UserRole objects that have the permission.

    Raises:
        DatabaseConnectionError: If database connection fails.
        DatabaseError: If operation fails or permission not found.
    """
    db = SessionLocal()
    try:
        permission = db.query(Permission).filter(Permission.id == permission_id).first()

        if not permission:
            logger.error(f"Permission with ID {permission_id} not found")
            raise DatabaseError("Failed to get permission roles: permission not found")

        return permission.roles
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting roles for permission '{permission_id}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting roles for permission '{permission_id}'")
        raise DatabaseError("Failed to get permission roles")
    finally:
        db.close()


# ============================================
# User Permission Helper Functions
# ============================================


def user_has_permission(user_id: int, permission_name: str) -> bool:
    """
    Check if a user has a specific permission via their role.

    Args:
        user_id: The ID of the user to check.
        permission_name: The name of the permission (e.g., "users:read").

    Returns:
        True if user has the permission, False otherwise.
    """
    db = SessionLocal()
    try:
        from models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.role:
            return False
        return any(p.name == permission_name for p in user.role.permissions)
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while checking permission for user '{user_id}'")
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error while checking permission for user '{user_id}'")
        return False
    finally:
        db.close()


def user_has_any_permission(user_id: int, permission_names: list[str]) -> bool:
    """
    Check if a user has any of the specified permissions via their role.

    Args:
        user_id: The ID of the user to check.
        permission_names: List of permission names to check.

    Returns:
        True if user has any of the permissions, False otherwise.
    """
    db = SessionLocal()
    try:
        from models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.role:
            return False
        user_permission_names = [p.name for p in user.role.permissions]
        return any(perm in user_permission_names for perm in permission_names)
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while checking permissions for user '{user_id}'")
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error while checking permissions for user '{user_id}'")
        return False
    finally:
        db.close()


def get_user_permissions(user_id: int) -> list[str]:
    """
    Get all permission names for a user via their role.

    Args:
        user_id: The ID of the user.

    Returns:
        List of permission name strings.
    """
    db = SessionLocal()
    try:
        from models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.role:
            return []
        return [p.name for p in user.role.permissions]
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting permissions for user '{user_id}'")
        return []
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting permissions for user '{user_id}'")
        return []
    finally:
        db.close()
