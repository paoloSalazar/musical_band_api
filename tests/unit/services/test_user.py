import pytest
from exceptions.exceptions import ConflictError
from schemas.user import UserBase, UserCreate, UserResponse
from models.user import User as DBUser
import services.user as service
from exceptions import NotFoundError

def test_get_all_users_empty(mocker):
    """Test get_all() returns empty list when no users"""
    # Arrange - Mock data.get_all to return empty list
    mock_data = mocker.patch('services.user.data.get_all')
    mock_data.return_value = []

    # Act - Call service function
    result = service.get_all()

    # Assert - Check result is empty list
    assert result == []
    mock_data.assert_called_once()

def test_get_all_users_with_data(mocker):
    """Test get_all() returns users when they exist"""
    # Arrange - Mock data.get_all to return specific DB users
    db_users = [
        DBUser(id=1, name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1),
        DBUser(id=2, name="Jane", lastname="Smith", email="jane.smith@example.com", password="hashedpass", role_id=2)
    ]
    mock_data = mocker.patch('services.user.data.get_all')
    mock_data.return_value = db_users

    # Act - Call service function
    result = service.get_all()

    # Assert - Check result contains the expected User objects
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "John"
    assert result[0].email == "john.doe@example.com"
    assert result[1].id == 2
    assert result[1].name == "Jane"
    mock_data.assert_called_once()

def test_get_one_user_found(mocker):
    """Test get_one() when user exists"""
    # Arrange - Mock data.get_one to return a specific DB user
    db_user = DBUser(id=1, name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1)
    mock_data = mocker.patch('services.user.data.get_one')
    mock_data.return_value = db_user

    # Act - Call service function
    result = service.get_one("john.doe@example.com")

    # Assert - Check result contains the expected User object
    assert result is not None
    assert result.id == 1
    assert result.name == "John"
    assert result.email == "john.doe@example.com"
    mock_data.assert_called_once_with("john.doe@example.com")

def test_get_one_user_not_found(mocker):
    """Test get_one() when user does not exist"""
    # Arrange - Mock data.get_one to return None
    mock_data = mocker.patch('services.user.data.get_one')
    mock_data.return_value = None

    # Act & Assert - Call service function and expect NotFoundError
    with pytest.raises(NotFoundError) as exc_info:
        service.get_one("nonexistent@example.com")

    assert str(exc_info.value.args[0]) == "User with email nonexistent@example.com not found"
    mock_data.assert_called_once_with("nonexistent@example.com")

def test_create_user(mocker):
    """Test create() function"""
    # Arrange - Mock data.get_one to return None (user doesn't exist) and data.create to return the created DB user
    user_create = UserCreate(name="Jane", lastname="Smith", email="jane.smith@example.com", password="hashedpass", role_id=2)
    db_user = DBUser(id=3, name="Jane", lastname="Smith", email="jane.smith@example.com", password="hashedpass", role_id=2)
    mock_get_one = mocker.patch('services.user.data.get_one')
    mock_get_one.return_value = None
    mock_create = mocker.patch('services.user.data.create')
    mock_create.return_value = db_user

    # Act - Call service function
    result = service.create(user_create)

    # Assert - Check result contains the expected User object
    assert result.id == 3
    assert result.name == "Jane"
    assert result.email == "jane.smith@example.com"
    mock_create.assert_called_once()
    mock_get_one.assert_called_once_with("jane.smith@example.com")
    # Verify the DBUser was created with correct data
    call_args = mock_create.call_args[0][0]
    assert isinstance(call_args, DBUser)
    assert call_args.name == "Jane"
    assert call_args.lastname == "Smith"
    assert call_args.email == "jane.smith@example.com"
    assert call_args.role_id == 2

def test_create_user_conflict(mocker):
    """Test create() function when user already exists"""
    # Arrange - Mock data.get_one to return an existing DB user
    existing_db_user = DBUser(id=1, name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1)
    mock_get_one = mocker.patch('services.user.data.get_one')
    mock_get_one.return_value = existing_db_user

    # Act & Assert - Call service function and expect ConflictError
    user_create = UserCreate(name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1)
    with pytest.raises(ConflictError) as exc_info:
        service.create(user_create)

    assert str(exc_info.value.args[0]) == "User with email john.doe@example.com already exists"
    mock_get_one.assert_called_once_with("john.doe@example.com")

def test_modify_user_existing(mocker):
    """Test modify() function"""
    # Arrange - Mock data.get_one to return existing user and data.modify to return the modified DB user
    user = UserResponse(id=1, name="Updated John", lastname="Doe", email="john.doe@example.com", role_id=1)
    existing_db_user = DBUser(id=1, name="John", lastname="Doe", email="john.doe@example.com", password="hashedpass", role_id=1)
    modified_db_user = DBUser(id=1, name="Updated John", lastname="Doe", email="john.doe@example.com", password="newpass", role_id=1)
    mock_get_one = mocker.patch('services.user.data.get_one')
    mock_get_one.return_value = existing_db_user
    mock_modify = mocker.patch('services.user.data.modify')
    mock_modify.return_value = modified_db_user

    # Act - Call service function
    result = service.modify(user)

    # Assert - Check result contains the expected User object
    assert result.id == 1
    assert result.name == "Updated John"
    mock_modify.assert_called_once()
    mock_get_one.assert_called_once_with("john.doe@example.com")
    # Verify the DBUser was created with correct data
    call_args = mock_modify.call_args[0][0]
    assert isinstance(call_args, DBUser)
    assert call_args.id == 1
    assert call_args.name == "Updated John"

def test_modify_user_not_found(mocker):
    """Test modify() function when user does not exist"""
    # Arrange - Mock data.get_one to return None
    mock_get_one = mocker.patch('services.user.data.get_one')
    mock_get_one.return_value = None

    # Act & Assert - Call service function and expect NotFoundError
    user = UserResponse(id=99, name="Nonexistent", lastname="User", email="nonexistent@example.com", password="pass", role_id=1)
    with pytest.raises(NotFoundError) as exc_info:
        service.modify(user)
    assert str(exc_info.value.args[0]) == "User with email nonexistent@example.com not found"
    mock_get_one.assert_called_once_with("nonexistent@example.com")