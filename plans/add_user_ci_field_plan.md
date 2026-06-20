# Plan: Add CI (DNI) Field to User Entity

## Overview
Add a `ci` field to the User entity to store the Cédula de Identidad / DNI number for users (clients and musicians).

---

## 1. Current User Model Structure

```python
# models/user.py
class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    second_lastname = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    phone_number = Column(String(50), nullable=True)
    role_id = Column(Integer, ForeignKey('user_roles.id'), nullable=False)
```

---

## 2. Proposed Changes

### 2.1 Model Update (`models/user.py`)
```python
class User(Base):
    # ... existing fields ...
    ci = Column(String(20), nullable=True)  # Cédula de Identidad / DNI
```

### 2.2 Schema Updates

#### `schemas/user.py`
```python
class UserBase(BaseModel):
    name: str
    lastname: str
    second_lastname: str | None = None
    email: str
    password: str
    phone_number: str | None = None
    ci: str | None = None  # NEW
    role_id: int

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    # ... existing fields
```

#### `schemas/user_detail.py` (if exists)
May need to update or deprecate in favor of the direct `ci` field on User.

---

## 3. Data Access Layer (`data/user.py`)

### 3.1 Create
Update `create()` function to include `ci` field:
```python
def create(user: User) -> User:
    # user.ci will be set from User object
```

### 3.2 Modify
Update `modify()` function to handle `ci` updates:
```python
def modify(user: User) -> User | None:
    # Add: db_user.ci = user.ci
```

---

## 4. Service Layer (`services/user.py`)

Update service functions to handle `ci` field:
- `create()`: Pass `ci` to data layer
- `modify()`: Update `ci` field
- Response schemas include `ci` field

---

## 5. API Endpoints (`web/user.py`)

### 5.1 POST `/api/users/`
Request body now accepts optional `ci` field.

### 5.2 PATCH `/api/users/{user_id}`
Request body can now update `ci` field.

---

## 6. Database Migration

### Alembic Migration Script
```python
# migrations/add_user_ci_field.py
def upgrade():
    op.add_column('users', sa.Column('ci', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'ci')
```

---

## 7. Impact Analysis

### Affected Components
| Component | Change Required |
|-----------|-----------------|
| `models/user.py` | Add `ci` column |
| `schemas/user.py` | Add `ci` to schemas |
| `data/user.py` | Handle `ci` in create/modify |
| `services/user.py` | Handle `ci` in service layer |
| `web/user.py` | Accept `ci` in request bodies |
| `web/event_payment.py` | May reference client CI |
| Database migrations | New migration file |

### Backward Compatibility
- `ci` field is nullable - existing records will have `NULL`
- No breaking changes to existing API contracts
- Optional field for new user creation

---

## 8. Implementation Order

1. Create database migration
2. Update model (`models/user.py`)
3. Update schemas (`schemas/user.py`)
4. Update data layer (`data/user.py`)
5. Update service layer (`services/user.py`)
6. Update API endpoints (`web/user.py`)
7. Update PDF templates to use `user.ci` instead of `UserDetail` table

---

## 9. PDF Documents Impact

### Receipt Template
Replace `UserDetail` lookup with direct `user.ci` access:
```html
<!-- Before: lookup via UserDetail table -->
<!-- After: direct from User.ci -->
```

### Contract Template
Update to use `user.ci` directly instead of querying `UserDetail` table.

---

## 10. Testing Considerations

### Test-Driven Development Approach

#### 10.1 Test File Structure
```
tests/
├── unit/
│   ├── models/
│   │   └── test_user.py         # Already exists
│   ├── schemas/
│   │   └── test_user.py         # Already exists
│   ├── data/
│   │   └── test_user.py         # Already exists
│   └── services/
│       └── test_user.py         # Already exists
├── integration/
│   └── # Add tests for CI field in existing API tests
└── conftest.py
```

#### 10.2 Test Cases (TDD - Write First)

**Unit Tests - `tests/unit/models/test_user.py`**
```python
def test_user_model_has_ci_field():
    """Test that User model has ci field"""
    user = User(name="Test", lastname="User", email="test@test.com", password="pass", role_id=1)
    assert hasattr(user, 'ci')
    assert user.ci is None

def test_user_creation_with_ci():
    """Test creating user with CI field"""
    user = User(
        name="Test", lastname="User", email="test@test.com",
        password="pass", role_id=1, ci="12345678"
    )
    assert user.ci == "12345678"
```

**Schema Tests - `tests/unit/schemas/test_user.py`**
```python
def test_user_create_schema_accepts_ci():
    """Test UserCreate schema accepts optional ci field"""
    schema = UserCreate(name="Test", lastname="User", email="test@test.com", password="pass", role_id=1, ci="12345678")
    assert schema.ci == "12345678"

def test_user_response_includes_ci():
    """Test UserResponse includes ci field"""
    schema = UserResponse(id=1, name="Test", lastname="User", email="test@test.com", role_id=1, ci="12345678")
    assert schema.ci == "12345678"

def test_user_to_dict_includes_ci():
    """Test model_dump includes ci field"""
    user = UserResponse(id=1, name="Test", lastname="User", email="test@test.com", role_id=1, ci="12345678")
    data = user.model_dump()
    assert data["ci"] == "12345678"
```

**Data Layer Tests - `tests/unit/data/test_user.py`**
```python
def test_create_user_with_ci(db_session):
    """Test creating user with CI field"""
    user = User(name="Test", lastname="User", email="test@test.com", ci="12345678", password="pass", role_id=1)
    created = user_data.create(user)
    assert created.ci == "12345678"

def test_update_user_ci(db_session):
    """Test updating user CI field"""
    user = user_data.get_one_by_id(1)
    user.ci = "87654321"
    updated = user_data.modify(user)
    assert updated.ci == "87654321"

def test_get_one_by_id_includes_ci(db_session):
    """Test retrieving user by ID includes ci field"""
    user = user_data.get_one_by_id(1)
    assert hasattr(user, 'ci')
```

**Service Layer Tests - `tests/unit/services/test_user.py`**
```python
def test_create_user_service_with_ci():
    """Test service layer handles CI field"""
    ...

def test_modify_user_service_updates_ci():
    """Test service layer updates CI field"""
    ...
```

**Integration Tests - Add to existing `tests/unit/web/test_user.py`**
```python
def test_create_user_api_with_ci():
    """Test POST /api/users/ with ci field"""
    response = client.post("/api/users/", json={
        "name": "Test", "lastname": "User", "email": "test@test.com",
        "password": "pass", "role_id": 1, "ci": "12345678"
    })
    assert response.status_code == 201
    assert response.json()["ci"] == "12345678"

def test_update_user_api_ci():
    """Test PATCH /api/users/{id} updates ci field"""
    response = client.patch("/api/users/1", json={"ci": "87654321"})
    assert response.json()["ci"] == "87654321"

def test_get_user_api_includes_ci():
    """Test GET /api/users/{id} includes ci field"""
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert "ci" in response.json()
```

**Note**: The existing `test_user_to_dict` test in `tests/unit/schemas/test_user.py` will need to be updated to include `ci` in the expected dictionary output.

---

## 11. Implementation Order (TDD)

1. **Write failing tests first**
   - Unit tests for model, schema, data, service layers
   - Integration tests for API endpoints

2. **Implement changes**
   - Database migration
   - Model update
   - Schema updates
   - Data layer updates
   - Service layer updates
   - API endpoint updates

3. **Run tests and verify**
   - All tests should pass after implementation

4. **Update PDF templates**
   - Use `user.ci` instead of `UserDetail` table lookup

---

## 12. Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific user-related tests
pytest tests/unit/models/test_user.py tests/unit/schemas/test_user.py tests/unit/data/test_user.py tests/unit/services/test_user.py tests/unit/web/test_user.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```