import logging
from config.database import SessionLocal
from models.user_role import UserRole
from sqlalchemy.exc import SQLAlchemyError
from exceptions import DatabaseError

logger = logging.getLogger(__name__)

def get_one(name: str) -> UserRole | None:
    """return one user role by name"""
    db = SessionLocal()
    try:
        return db.query(UserRole).filter(UserRole.name == name).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting user role '{name}': {str(e)}")
        raise DatabaseError(f"Failed to get user role: {str(e)}")
    finally:
        db.close()

def get_all() -> list[UserRole]:
    """return all user roles"""
    db = SessionLocal()
    try:
        return db.query(UserRole).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting all user roles: {str(e)}")
        raise DatabaseError(f"Failed to get all user roles: {str(e)}")
    finally:
        db.close()

def create(user_role: UserRole) -> UserRole:
    db = SessionLocal()
    try:
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        return user_role
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating user role '{user_role.name}': {str(e)}")
        db.rollback()
        raise DatabaseError(f"Failed to create user role: {str(e)}")
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
    except SQLAlchemyError as e:
        logger.error(f"Database error while modifying user role '{user_role.name}': {str(e)}")
        db.rollback()
        raise DatabaseError(f"Failed to modify user role: {str(e)}")
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
    except SQLAlchemyError as e:
        logger.error(f"Database error while replacing user role '{user_role.name}': {str(e)}")
        db.rollback()
        raise DatabaseError(f"Failed to replace user role: {str(e)}")
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
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting user role '{name}': {str(e)}")
        db.rollback()
        raise DatabaseError(f"Failed to delete user role: {str(e)}")
    finally:
        db.close()