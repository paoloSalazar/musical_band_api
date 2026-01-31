import logging
from schemas.user import UserResponse, UserCreate
import data.user as data
from models.user import User as DBUser
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError
from auth.auth import get_password_hash

logger = logging.getLogger(__name__)


def get_all() -> list[UserResponse]:
    """return all users"""
    try:
        db_users = data.get_all()
        users = [UserResponse.model_validate(user) for user in db_users]
        logger.info(f"Retrieved {len(users)} users")
        return users
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in get_all")
        raise DatabaseError("Service error")


def get_one(email: str) -> UserResponse:
    """return one user by email"""
    try:
        db_user = data.get_one(email)
        if db_user is None:
            logger.warning(f"User with email {email} not found")
            raise NotFoundError(f"User with email {email} not found")
        user = UserResponse.model_validate(db_user)
        logger.info(f"Retrieved user with email {email}")
        return user
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in get_one")
        raise DatabaseError("Service error")


def create(user_create: UserCreate) -> UserResponse:
    """create a new user"""
    try:
        existing_user = data.get_one(user_create.email)
        if existing_user is not None:
            logger.warning(f"User with email {user_create.email} already exists")
            raise ConflictError(f"User with email {user_create.email} already exists")

        db_user = DBUser(
            name=user_create.name,
            lastname=user_create.lastname,
            second_lastname=user_create.second_lastname,
            email=user_create.email,
            password=get_password_hash(user_create.password),
            role_id=user_create.role_id
        )
        created_db_user = data.create(db_user)
        user = UserResponse.model_validate(created_db_user)
        logger.info(f"Created user with email {user_create.email}")
        return user
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in create")
        raise DatabaseError("Service error")


def modify(user: UserResponse) -> UserResponse:
    """modify an existing user"""
    try:
        existing_user = data.get_one(user.email)
        if existing_user is None:
            logger.warning(f"User with email {user.email} not found")
            raise NotFoundError(f"User with email {user.email} not found")

        db_user = DBUser(
            id=user.id,
            name=user.name,
            lastname=user.lastname,
            second_lastname=user.second_lastname,
            email=user.email,
            password=existing_user.password,  # Keep existing password
            role_id=user.role_id
        )
        modified_db_user = data.modify(db_user)
        if modified_db_user:
            logger.info(f"Modified user with email {user.email}")
            return UserResponse.model_validate(modified_db_user)
        else:
            logger.warning(f"User with email {user.email} not found during modification")
            raise NotFoundError(f"User with email {user.email} not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in modify")
        raise DatabaseError("Service error")
