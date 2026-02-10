import logging
from config.database import SessionLocal
from models.permission import Permission
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
