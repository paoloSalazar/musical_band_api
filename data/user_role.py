from .init import conn, cursor
from model.user_role import UserRole

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
)
""")

def row_to_model(row) -> UserRole:
    """convert a database row to a UserRole model"""
    return UserRole(id=row['id'], name=row['name'], description=row['description'])

def model_to_dict(user_role: UserRole) -> dict:
    """convert a UserRole model to a dictionary"""
    return user_role.model_dump()

def get_one(name: str) -> UserRole | None:
    """return one user role by name"""
    qry = "SELECT * FROM user_roles WHERE name=%s"
    cursor.execute(qry, (name,))
    row = cursor.fetchone()
    return row_to_model(row) if row else None

def get_all() -> list[UserRole]:
    """return all user roles"""
    qry = "SELECT * FROM user_roles"
    cursor.execute(qry)
    return [row_to_model(row) for row in cursor.fetchall()]

def create(user_role: UserRole) -> UserRole:
    qry = "INSERT INTO user_roles (name, description) VALUES (%s, %s) RETURNING id"
    params = (user_role.name, user_role.description)
    cursor.execute(qry, params)
    conn.commit()
    user_role.id = cursor.fetchone()['id']
    return user_role

def modify(user_role: UserRole) -> UserRole:
    qry = "UPDATE user_roles SET description=%s WHERE name=%s"
    params = (user_role.description, user_role.name)
    cursor.execute(qry, params)
    conn.commit()
    return get_one(user_role.name)

def replace(user_role: UserRole) -> UserRole:
    qry = "UPDATE user_roles SET name=%s, description=%s WHERE id=%s"
    params = (user_role.name, user_role.description, user_role.id)
    cursor.execute(qry, params)
    conn.commit()
    return get_one(user_role.name)

def delete(name: str) -> bool:
    qry = "DELETE FROM user_roles WHERE name=%s"
    cursor.execute(qry, (name,))
    conn.commit()
    return cursor.rowcount > 0