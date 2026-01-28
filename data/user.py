import logging
from config.database import SessionLocal
from models.user import User
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from exceptions import DatabaseError, DatabaseConnectionError

logger = logging.getLogger(__name__)

def get_one(email: str) -> User | None:
    """return one user by email"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while getting user '{email}'")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting user '{email}'")
        raise DatabaseError("Failed to get user")
    finally:
        db.close()

def get_all() -> list[User]:
    """return all users"""
    db = SessionLocal()
    try:
        return db.query(User).all()
    except (OperationalError, InterfaceError) as e:
        logger.error("Database connection error while getting all users")
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error("Database error while getting all users")
        raise DatabaseError("Failed to get all users")
    finally:
        db.close()

def create(user: User) -> User:
    db = SessionLocal()
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while creating user '{user.email}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating user '{user.email}'")
        db.rollback()
        raise DatabaseError("Failed to create user")
    finally:
        db.close()

def modify(user: User) -> User:
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if db_user:
            db_user.name = user.name
            db_user.lastname = user.lastname
            db_user.second_lastname = user.second_lastname
            db_user.email = user.email
            db_user.password = user.password
            db_user.role_id = user.role_id
            db.commit()
            db.refresh(db_user)
        return db_user
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection error while modifying user '{user.email}'")
        db.rollback()
        raise DatabaseConnectionError("Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error while modifying user '{user.email}'")
        db.rollback()
        raise DatabaseError("Failed to modify user")
    finally:
        db.close()
