import logging
from schemas.user import UserResponse, UserCreate, UserUpdate
import data.user as data
from models.user import User as DBUser
from exceptions import DatabaseError, DatabaseConnectionError, NotFoundError, ConflictError, UnauthorizedError
from auth.auth import get_password_hash, verify_password

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


def modify(user_update: UserUpdate) -> UserResponse:
    """modify an existing user"""
    try:
        existing_user = data.get_one(user_update.email)
        if existing_user is None:
            logger.warning(f"User with email {user_update.email} not found")
            raise NotFoundError(f"User with email {user_update.email} not found")

        db_user = DBUser(
            id=existing_user.id,
            name=user_update.name if user_update.name else existing_user.name,
            lastname=user_update.lastname if user_update.lastname else existing_user.lastname,
            second_lastname=user_update.second_lastname if user_update.second_lastname else existing_user.second_lastname,
            email=user_update.email if user_update.email else existing_user.email,
            password=existing_user.password,  # Keep existing password
            role_id=user_update.role_id if user_update.role_id else existing_user.role_id
        )
        modified_db_user = data.modify(db_user)
        if modified_db_user:
            logger.info(f"Modified user with email {user_update.email}")
            return UserResponse.model_validate(modified_db_user)
        else:
            logger.warning(f"User with email {user_update.email} not found during modification")
            raise NotFoundError(f"User with email {user_update.email} not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in modify")
        raise DatabaseError("Service error")


def modify_password(email: str, current_password: str, new_password: str) -> bool:
    """modify user password (requires current password verification)"""
    try:
        existing_user = data.get_one(email)
        if existing_user is None:
            logger.warning(f"User with email {email} not found")
            raise NotFoundError(f"User with email {email} not found")

        # Verify current password
        if not verify_password(current_password, existing_user.password):
            logger.warning(f"Invalid current password for user {email}")
            raise UnauthorizedError("Current password is incorrect")

        # Update password
        db_user = DBUser(
            id=existing_user.id,
            name=existing_user.name,
            lastname=existing_user.lastname,
            second_lastname=existing_user.second_lastname,
            email=existing_user.email,
            password=get_password_hash(new_password),
            role_id=existing_user.role_id
        )
        modified_db_user = data.modify(db_user)
        if modified_db_user:
            logger.info(f"Modified password for user {email}")
            return True
        else:
            logger.warning(f"User with email {email} not found during password modification")
            raise NotFoundError(f"User with email {email} not found")
    except (DatabaseError, DatabaseConnectionError) as e:
        logger.error("Service error in modify_password")
        raise DatabaseError("Service error")
