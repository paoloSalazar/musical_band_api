import logging
from config.database import SessionLocal
from models.user_role import UserRole
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from exceptions import DatabaseError, DatabaseConnectionError

logger = logging.getLogger(__name__)

def get_one(name: str) -> UserRole | None:
    """return one user role by name"""
    db = SessionLocal()
    try:
        return db.query(UserRole).filter(UserRole.name == name).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting user role '{name}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting user role '{name}'")
        raise DatabaseError("Failed to get user role")
    finally:
        db.close()

def get_all() -> list[UserRole]:
    """return all user roles"""
    db = SessionLocal()
    try:
        return db.query(UserRole).all()
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting all user roles")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while getting all user roles")
        raise DatabaseError("Failed to get all user roles")
    finally:
        db.close()

def create(user_role: UserRole) -> UserRole:
    db = SessionLocal()
    try:
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        return user_role
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while creating user role '{user_role.name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating user role '{user_role.name}'")
        db.rollback()
        raise DatabaseError("Failed to create user role")
    finally:
        db.close()

def modify(user_role: UserRole) -> UserRole:
    db = SessionLocal()
    try:
        db_user = db.query(UserRole).filter(UserRole.name == user_role.name).first()
        if db_user:
            db_user.description = user_role.description
            db.commit()
            db.refresh(db_user)
        return db_user
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while modifying user role '{user_role.name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while modifying user role '{user_role.name}'")
        db.rollback()
        raise DatabaseError("Failed to modify user role")
    finally:
        db.close()

def replace(user_role: UserRole) -> UserRole:
    db = SessionLocal()
    try:
        db_user = db.query(UserRole).filter(UserRole.id == user_role.id).first()
        if db_user:
            db_user.name = user_role.name
            db_user.description = user_role.description
            db.commit()
            db.refresh(db_user)
        return db_user
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while replacing user role '{user_role.name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while replacing user role '{user_role.name}'")
        db.rollback()
        raise DatabaseError("Failed to replace user role")
    finally:
        db.close()

def delete(name: str) -> bool:
    db = SessionLocal()
    try:
        db_user = db.query(UserRole).filter(UserRole.name == name).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while deleting user role '{name}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting user role '{name}'")
        db.rollback()
        raise DatabaseError("Failed to delete user role")
    finally:
        db.close()