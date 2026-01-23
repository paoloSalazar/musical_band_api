from config.database import SessionLocal
from models.user import User

def get_one(email: str) -> User | None:
    """return one user by email"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()

def get_all() -> list[User]:
    """return all users"""
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()

def create(user: User) -> User:
    db = SessionLocal()
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
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
    finally:
        db.close()
