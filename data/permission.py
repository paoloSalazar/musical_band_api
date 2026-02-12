import logging
from config.database import SessionLocal
from models.permission import Permission
from models.user_role import UserRole
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from exceptions import DatabaseError, DatabaseConnectionError

logger = logging.getLogger(__name__)


def get_one(permission_id: int) -> Permission | None:
    """Get a permission by ID."""
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
    """Get a permission by name."""
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


def get_all() -> list[Permission]:
    """Get all permissions."""
    db = SessionLocal()
    try:
        return db.query(Permission).all()
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting all permissions")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while getting all permissions")
        raise DatabaseError("Failed to get all permissions")
    finally:
        db.close()


def create(permission: Permission) -> Permission:
    """Create a new permission."""
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
    """Update a permission."""
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
    """Delete a permission."""
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


# ============================================
# Role-Permission Assignment Functions
# ============================================


def assign_permission_to_role(permission_id: int, role_id: int) -> bool:
    """Assign a permission to a role."""
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
    """Remove a permission from a role."""
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
    """Get all permissions for a role."""
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
    """Get all roles for a permission."""
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
    """Check if a user has a specific permission via their role."""
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
    """Check if a user has any of the specified permissions via their role."""
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
    """Get all permission names for a user via their role."""
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
