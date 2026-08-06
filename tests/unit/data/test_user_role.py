import pytest
from models.user_role import UserRole
from models.permission import Permission
import data.user_role as data
from sqlalchemy.exc import SQLAlchemyError
from exceptions import DatabaseError, ConflictError

def test_get_one_user_role_found(mocker):
    """Test get_one() when role exists"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = UserRole(id=1, name="admin", description="Administrator")

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one("admin")

    # Assert - Check result and session calls
    assert result is not None
    assert result.id == 1
    assert result.name == "admin"
    assert result.description == "Administrator"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.query.assert_called_once_with(UserRole)
    mock_query.filter.assert_called_once()
    mock_query.first.assert_called_once()

def test_get_one_user_role_not_found(mocker):
    """Test get_one() when role does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one("nonexistent")

    # Assert - Check result is None and session calls
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()

def test_get_one_user_role_database_error(mocker):
    """Test get_one() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and query to raise SQLAlchemyError
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_one("admin")

    assert "Failed to get user role" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_not_called()  # No rollback for read operations

def test_get_all_user_roles_empty(mocker):
    """Test get_all() returns empty list when no roles"""
    # Arrange - Mock SessionLocal and query to return empty list
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = []

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_all()

    # Assert - Check result is empty list
    assert result == []
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.query.assert_called_once_with(UserRole)
    mock_query.all.assert_called_once()

def test_get_all_user_roles_with_data(mocker):
    """Test get_all() returns roles when they exist"""
    # Arrange - Mock SessionLocal and query to return roles
    roles = [
        UserRole(id=1, name="admin", description="Administrator"),
        UserRole(id=2, name="user", description="Regular user")
    ]
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = roles

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_all()

    # Assert - Check result contains the expected roles
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "admin"
    assert result[1].id == 2
    assert result[1].name == "user"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()

def test_get_all_user_roles_database_error(mocker):
    """Test get_all() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and query to raise SQLAlchemyError
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_all()

    assert "Failed to get all user roles" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_not_called()  # No rollback for read operations

def test_create_user_role(mocker):
    """Test create() function"""
    # Arrange - Mock SessionLocal
    user_role = UserRole(name="moderator", description="Moderator role")
    # Simulate database setting the ID
    user_role.id = 3
    mock_session = mocker.Mock()
    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.create(user_role)

    # Assert - Check session methods were called correctly
    assert result == user_role
    assert result.id == 3
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.add.assert_called_once_with(user_role)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(user_role)

def test_create_user_role_database_error(mocker):
    """Test create() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and commit to raise SQLAlchemyError
    user_role = UserRole(name="moderator", description="Moderator role")
    mock_session = mocker.Mock()
    mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.create(user_role)

    assert "Failed to create user role" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_called_once()  # Rollback should be called on error

def test_modify_user_role_found(mocker):
    """Test modify() when role exists"""
    # Arrange - Mock SessionLocal and query
    user_role = UserRole(id=1, name="admin", description="Updated Administrator")
    existing_role = UserRole(id=1, name="admin", description="Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_role

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.modify(user_role)

    # Assert - Check result and that description was updated
    assert result == existing_role
    assert existing_role.description == "Updated Administrator"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_role)

def test_modify_user_role_not_found(mocker):
    """Test modify() when role does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    user_role = UserRole(id=1, name="admin", description="Updated Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.modify(user_role)

    # Assert - Check result is None and commit/refresh not called
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()

def test_modify_user_role_database_error(mocker):
    """Test modify() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and commit to raise SQLAlchemyError
    user_role = UserRole(id=1, name="admin", description="Updated Administrator")
    existing_role = UserRole(id=1, name="admin", description="Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_role
    mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.modify(user_role)

    assert "Failed to modify user role" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_called_once()  # Rollback should be called on error

def test_replace_user_role_found(mocker):
    """Test replace() when role exists"""
    # Arrange - Mock SessionLocal and query
    user_role = UserRole(id=1, name="administrator", description="Full Administrator")
    existing_role = UserRole(id=1, name="admin", description="Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_role

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.replace(user_role)

    # Assert - Check result and that fields were updated
    assert result == existing_role
    assert existing_role.name == "administrator"
    assert existing_role.description == "Full Administrator"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_role)

def test_replace_user_role_not_found(mocker):
    """Test replace() when role does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    user_role = UserRole(id=1, name="administrator", description="Full Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.replace(user_role)

    # Assert - Check result is None and commit/refresh not called
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()

def test_replace_user_role_database_error(mocker):
    """Test replace() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and commit to raise SQLAlchemyError
    user_role = UserRole(id=1, name="administrator", description="Full Administrator")
    existing_role = UserRole(id=1, name="admin", description="Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_role
    mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.replace(user_role)

    assert "Failed to replace user role" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_called_once()  # Rollback should be called on error

def test_delete_user_role_success(mocker):
    """Test delete() when role exists and has no integrity constraints"""
    # Arrange - Mock SessionLocal and query
    existing_role = UserRole(id=1, name="admin", description="Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_role

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Mock integrity checker to allow deletion
    mock_integrity_checker = mocker.patch('data.user_role.check_integrity_before_deletion')
    mock_integrity_checker.return_value = None  # Safe to delete

    # Act - Call data function
    result = data.delete("admin")

    # Assert - Check result is True and delete was called
    assert result is True
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.delete.assert_called_once_with(existing_role)
    mock_session.commit.assert_called_once()

def test_delete_user_role_not_found(mocker):
    """Test delete() when role does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.delete("nonexistent")

    # Assert - Check result is False and delete/commit not called
    assert result is False
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()

def test_delete_user_role_database_error(mocker):
    """Test delete() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and commit to raise SQLAlchemyError
    existing_role = UserRole(id=1, name="admin", description="Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_role
    mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Mock integrity checker to allow deletion (we want to test the commit error)
    mock_integrity_checker = mocker.patch('data.user_role.check_integrity_before_deletion')
    mock_integrity_checker.return_value = None  # Safe to delete

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.delete("admin")

    assert "Failed to delete user role" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_called_once()  # Rollback should be called on error


def test_delete_user_role_with_permissions(mocker):
    """Test delete() raises ConflictError when role has permissions assigned"""
    # Arrange - Mock role exists and integrity checker returns error
    existing_role = UserRole(id=1, name="admin", description="Administrator")

    # Mock the integrity checker to return an error about permissions
    mock_integrity_checker = mocker.patch('data.user_role.check_integrity_before_deletion')
    mock_integrity_checker.return_value = "This role cannot be deleted because it has 2 permissions assigned ('read:users', 'write:users'). Please remove these permissions from the role first."

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_role

    mock_session_local = mocker.patch('data.user_role.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect ConflictError
    with pytest.raises(ConflictError) as exc_info:
        data.delete("admin")

    assert "2 permissions assigned" in str(exc_info.value)
    assert "read:users" in str(exc_info.value)
    assert "write:users" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    # Verify delete and commit were NOT called due to integrity check
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()