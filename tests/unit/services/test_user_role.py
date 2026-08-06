import pytest
from schemas.user_role import UserRole, UserRoleCreate
from models.user_role import UserRole as DBUserRole
import services.user_role as service
from exceptions import NotFoundError

def test_get_all_user_roles_empty(mocker):
    """Test get_all() returns empty list when no roles"""
    # Arrange - Mock data.get_all to return empty list
    mock_data = mocker.patch('services.user_role.data.get_all')
    mock_data.return_value = []

    # Act - Call service function
    result = service.get_all()

    # Assert - Check result is empty list
    assert result == []
    mock_data.assert_called_once()

def test_get_all_user_roles_with_data(mocker):
    """Test get_all() returns roles when they exist"""
    # Arrange - Mock data.get_all to return specific DB roles
    db_roles = [
        DBUserRole(id=1, name="admin", description="Administrator"),
        DBUserRole(id=2, name="user", description="Regular user")
    ]
    mock_data = mocker.patch('services.user_role.data.get_all')
    mock_data.return_value = db_roles

    # Act - Call service function
    result = service.get_all()

    # Assert - Check result contains the expected UserRole objects
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "admin"
    assert result[0].description == "Administrator"
    assert result[1].id == 2
    assert result[1].name == "user"
    mock_data.assert_called_once()

def test_get_one_user_role_found(mocker):
    """Test get_one() when role exists"""
    # Arrange - Mock data.get_one to return a specific DB role
    db_role = DBUserRole(id=1, name="admin", description="Administrator")
    mock_data = mocker.patch('services.user_role.data.get_one')
    mock_data.return_value = db_role

    # Act - Call service function
    result = service.get_one("admin")

    # Assert - Check result contains the expected UserRole object
    assert result is not None
    assert result.id == 1
    assert result.name == "admin"
    assert result.description == "Administrator"
    mock_data.assert_called_once_with("admin")

def test_get_one_user_role_not_found(mocker):
    """Test get_one() when role does not exist"""
    # Arrange - Mock data.get_one to return None
    mock_data = mocker.patch('services.user_role.data.get_one')
    mock_data.return_value = None

    # Act & Assert - Call service function and expect NotFoundError
    with pytest.raises(NotFoundError) as exc_info:
        service.get_one("nonexistent")

    assert str(exc_info.value) == "User role 'nonexistent' not found"
    mock_data.assert_called_once_with("nonexistent")

def test_create_user_role(mocker):
    """Test create() function"""
    # Arrange - Mock data.get_one to return None (role doesn't exist) and data.create to return the created DB role
    user_role_create = UserRoleCreate(name="moderator", description="Moderator role")
    db_role = DBUserRole(id=3, name="moderator", description="Moderator role")
    mock_get_one = mocker.patch('services.user_role.data.get_one')
    mock_get_one.return_value = None
    mock_create = mocker.patch('services.user_role.data.create')
    mock_create.return_value = db_role

    # Act - Call service function
    result = service.create(user_role_create)

    # Assert - Check result contains the expected UserRole object
    assert result.id == 3
    assert result.name == "moderator"
    assert result.description == "Moderator role"
    mock_create.assert_called_once()
    mock_get_one.assert_called_once_with("moderator")
    # Verify the DBUserRole was created with correct data
    call_args = mock_create.call_args[0][0]
    assert isinstance(call_args, DBUserRole)
    assert call_args.name == "moderator"
    assert call_args.description == "Moderator role"

def test_modify_user_role(mocker):
    """Test modify() function"""
    # Arrange - Mock data.get_by_id to return existing role and data.modify to return the modified DB role
    from schemas.user_role import UserRoleUpdate
    role_update = UserRoleUpdate(name="admin", description="Updated Administrator")
    existing_db_role = DBUserRole(id=1, name="admin", description="Administrator")
    modified_db_role = DBUserRole(id=1, name="admin", description="Updated Administrator")
    mock_get_by_id = mocker.patch('services.user_role.data.get_by_id')
    mock_get_by_id.return_value = existing_db_role
    mock_modify = mocker.patch('services.user_role.data.modify')
    mock_modify.return_value = modified_db_role

    # Act - Call service function
    result = service.modify(role_id=1, role_update=role_update)

    # Assert - Check result contains the expected UserRole object
    assert result.id == 1
    assert result.name == "admin"
    assert result.description == "Updated Administrator"
    mock_modify.assert_called_once()
    mock_get_by_id.assert_called_once_with(1)
    # Verify the DBUserRole was created with correct data
    call_args = mock_modify.call_args[0][0]
    assert isinstance(call_args, DBUserRole)
    assert call_args.id == 1
    assert call_args.name == "admin"
    assert call_args.description == "Updated Administrator"

def test_replace_user_role(mocker):
    """Test replace() function"""
    # Arrange - Mock data.replace to return the replaced DB role
    user_role = UserRole(id=1, name="administrator", description="Full Administrator")
    db_role = DBUserRole(id=1, name="administrator", description="Full Administrator")
    mock_data = mocker.patch('services.user_role.data.replace')
    mock_data.return_value = db_role

    # Act - Call service function
    result = service.replace(user_role)

    # Assert - Check result contains the expected UserRole object
    assert result.id == 1
    assert result.name == "administrator"
    assert result.description == "Full Administrator"
    mock_data.assert_called_once()
    # Verify the DBUserRole was created with correct data
    call_args = mock_data.call_args[0][0]
    assert isinstance(call_args, DBUserRole)
    assert call_args.id == 1
    assert call_args.name == "administrator"
    assert call_args.description == "Full Administrator"

def test_delete_user_role_success(mocker):
    """Test delete() function when role exists"""
    # Arrange - Mock data.get_one to return existing role and data.delete to return True
    existing_db_role = DBUserRole(id=1, name="admin", description="Administrator")
    mock_get_one = mocker.patch('services.user_role.data.get_one')
    mock_get_one.return_value = existing_db_role
    mock_delete = mocker.patch('services.user_role.data.delete')
    mock_delete.return_value = True

    # Act - Call service function
    result = service.delete("admin")

    # Assert - Check result is True
    assert result is True
    mock_get_one.assert_called_once_with("admin")
    mock_delete.assert_called_once_with("admin")

def test_delete_user_role_not_found(mocker):
    """Test delete() function when role does not exist"""
    # Arrange - Mock data.get_one to return None
    mock_get_one = mocker.patch('services.user_role.data.get_one')
    mock_get_one.return_value = None

    # Act & Assert - Call service function and expect NotFoundError
    with pytest.raises(NotFoundError) as exc_info:
        service.delete("nonexistent")

    assert str(exc_info.value) == "User role 'nonexistent' not found"
    mock_get_one.assert_called_once_with("nonexistent")


def test_delete_user_role_conflict_error(mocker):
    """Test delete() function when role has permissions assigned"""
    # Arrange - Mock data.get_one to return existing role with permissions
    from exceptions import ConflictError
    existing_db_role = DBUserRole(id=1, name="admin", description="Administrator")
    mock_get_one = mocker.patch('services.user_role.data.get_one')
    mock_get_one.return_value = existing_db_role
    
    # Mock data.delete to raise ConflictError
    mock_delete = mocker.patch('services.user_role.data.delete')
    mock_delete.side_effect = ConflictError(
        "Cannot delete role 'admin' because it has the following permissions assigned: read:users, write:users"
    )

    # Act & Assert - Call service function and expect ConflictError
    with pytest.raises(ConflictError) as exc_info:
        service.delete("admin")

    assert "admin" in str(exc_info.value)
    assert "read:users" in str(exc_info.value)
    mock_get_one.assert_called_once_with("admin")
    mock_delete.assert_called_once_with("admin")