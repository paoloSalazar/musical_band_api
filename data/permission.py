from sqlalchemy.orm import Session
from models.permission import Permission


def get_all(db: Session):
    """Get all permissions."""
    return db.query(Permission).all()


def get_one(db: Session, permission_id: int):
    """Get a permission by ID."""
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_by_name(db: Session, name: str):
    """Get a permission by name."""
    return db.query(Permission).filter(Permission.name == name).first()


def create(db: Session, permission):
    """Create a new permission."""
    db_permission = Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def update(db: Session, permission_id: int, permission):
    """Update a permission."""
    db_permission = get_one(db, permission_id)
    if db_permission:
        update_data = permission.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_permission, key, value)
        db.commit()
        db.refresh(db_permission)
    return db_permission


def delete(db: Session, permission_id: int):
    """Delete a permission."""
    db_permission = get_one(db, permission_id)
    if db_permission:
        db.delete(db_permission)
        db.commit()
        return True
    return False
