from config.database import SessionLocal
from model.user_role import UserRole

def get_one(name: str) -> UserRole | None:
    """return one user role by name"""
    db = SessionLocal()
    try:
        return db.query(UserRole).filter(UserRole.name == name).first()
    finally:
        db.close()

def get_all() -> list[UserRole]:
    """return all user roles"""
    db = SessionLocal()
    try:
        return db.query(UserRole).all()
    finally:
        db.close()

def create(user_role: UserRole) -> UserRole:
    db = SessionLocal()
    try:
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        return user_role
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
    finally:
        db.close()