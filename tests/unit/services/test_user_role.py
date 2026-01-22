import pytest
from schemas.user_role import UserRole, UserRoleCreate
from models.user_role import UserRole as DBUserRole
import services.user_role as service

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

    # Act - Call service function
    result = service.get_one("nonexistent")

    # Assert - Check result is None
    assert result is None
    mock_data.assert_called_once_with("nonexistent")

def test_create_user_role(mocker):
    """Test create() function"""
    # Arrange - Mock data.create to return the created DB role
    user_role_create = UserRoleCreate(name="moderator", description="Moderator role")
    db_role = DBUserRole(id=3, name="moderator", description="Moderator role")
    mock_data = mocker.patch('services.user_role.data.create')
    mock_data.return_value = db_role

    # Act - Call service function
    result = service.create(user_role_create)

    # Assert - Check result contains the expected UserRole object
    assert result.id == 3
    assert result.name == "moderator"
    assert result.description == "Moderator role"
    mock_data.assert_called_once()
    # Verify the DBUserRole was created with correct data
    call_args = mock_data.call_args[0][0]
    assert isinstance(call_args, DBUserRole)
    assert call_args.name == "moderator"
    assert call_args.description == "Moderator role"

def test_modify_user_role(mocker):
    """Test modify() function"""
    # Arrange - Mock data.modify to return the modified DB role
    user_role = UserRole(id=1, name="admin", description="Updated Administrator")
    db_role = DBUserRole(id=1, name="admin", description="Updated Administrator")
    mock_data = mocker.patch('services.user_role.data.modify')
    mock_data.return_value = db_role

    # Act - Call service function
    result = service.modify(user_role)

    # Assert - Check result contains the expected UserRole object
    assert result.id == 1
    assert result.name == "admin"
    assert result.description == "Updated Administrator"
    mock_data.assert_called_once()
    # Verify the DBUserRole was created with correct data
    call_args = mock_data.call_args[0][0]
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
    # Arrange - Mock data.delete to return True
    mock_data = mocker.patch('services.user_role.data.delete')
    mock_data.return_value = True

    # Act - Call service function
    result = service.delete("admin")

    # Assert - Check result is True
    assert result is True
    mock_data.assert_called_once_with("admin")

def test_delete_user_role_not_found(mocker):
    """Test delete() function when role does not exist"""
    # Arrange - Mock data.delete to return False
    mock_data = mocker.patch('services.user_role.data.delete')
    mock_data.return_value = False

    # Act - Call service function
    result = service.delete("nonexistent")

    # Assert - Check result is False
    assert result is False
    mock_data.assert_called_once_with("nonexistent")