import pytest
from schemas.user_role import UserRole, UserRoleCreate
from web.user_role import get_all, get_one, create, modify, replace, delete

def test_get_user_roles_empty_list(mocker):
    """Test get_all() returns empty list when no roles"""
    # Arrange - Mock service to return empty list
    mock_service = mocker.patch('web.user_role.service.get_all')
    mock_service.return_value = []

    # Act - Call function directly
    result = get_all()

    # Assert - Check result is empty list
    assert result == []
    mock_service.assert_called_once()

def test_get_user_roles_with_data(mocker):
    """Test get_all() returns roles when they exist"""
    # Arrange - Mock service to return specific roles
    expected_roles = [
        UserRole(id=1, name="admin", description="Administrator"),
        UserRole(id=2, name="user", description="Regular user")
    ]
    mock_service = mocker.patch('web.user_role.service.get_all')
    mock_service.return_value = expected_roles

    # Act - Call function directly
    result = get_all()

    # Assert - Check result contains the mocked data
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "admin"
    assert result[0].description == "Administrator"
    assert result[1].id == 2
    assert result[1].name == "user"
    mock_service.assert_called_once()

def test_get_user_role_found(mocker):
    """Test get_one() when role exists"""
    # Arrange - Mock service to return a specific role
    expected_role = UserRole(id=1, name="admin", description="Administrator")
    mock_service = mocker.patch('web.user_role.service.get_one')
    mock_service.return_value = expected_role

    # Act - Call function directly
    result = get_one("admin")

    # Assert - Check result contains the mocked role
    assert result.id == 1
    assert result.name == "admin"
    assert result.description == "Administrator"
    mock_service.assert_called_once_with("admin")

def test_get_user_role_not_found(mocker):
    """Test get_one() when role doesn't exist"""
    # Arrange - Mock service to return None
    mock_service = mocker.patch('web.user_role.service.get_one')
    mock_service.return_value = None

    # Act - Call function directly
    result = get_one("nonexistent")

    # Assert - Check result is None
    assert result is None
    mock_service.assert_called_once_with("nonexistent")

def test_create_user_role(mocker):
    """Test create() creates and returns new role"""
    # Arrange - Mock service to return created role
    input_data = UserRoleCreate(name="moderator", description="Content moderator")
    expected_created_role = UserRole(id=3, name="moderator", description="Content moderator")
    mock_service = mocker.patch('web.user_role.service.create')
    mock_service.return_value = expected_created_role

    # Act - Call function directly
    result = create(input_data)

    # Assert - Check result contains created role
    assert result.id == 3
    assert result.name == "moderator"
    assert result.description == "Content moderator"
    mock_service.assert_called_once()
    # Verify service was called with UserRoleCreate object
    call_args = mock_service.call_args[0][0]
    assert isinstance(call_args, UserRoleCreate)
    assert call_args.name == "moderator"
    assert call_args.description == "Content moderator"

def test_patch_user_role(mocker):
    """Test modify() updates and returns modified role"""
    # Arrange - Mock service to return modified role
    input_data = UserRole(id=3, name="moderator", description="Updated moderator")
    expected_modified_role = UserRole(id=3, name="moderator", description="Updated moderator")
    mock_service = mocker.patch('web.user_role.service.modify')
    mock_service.return_value = expected_modified_role

    # Act - Call function directly
    result = modify(input_data)

    # Assert - Check result contains modified role
    assert result.id == 3
    assert result.name == "moderator"
    assert result.description == "Updated moderator"
    mock_service.assert_called_once()
    # Verify service was called with UserRole object
    call_args = mock_service.call_args[0][0]
    assert isinstance(call_args, UserRole)
    assert call_args.id == 3
    assert call_args.name == "moderator"
    assert call_args.description == "Updated moderator"

def test_replace_user_role(mocker):
    """Test replace() updates and returns replaced role"""
    # Arrange - Mock service to return replaced role
    input_data = UserRole(id=3, name="moderator", description="Replaced moderator")
    expected_replaced_role = UserRole(id=3, name="moderator", description="Replaced moderator")
    mock_service = mocker.patch('web.user_role.service.replace')
    mock_service.return_value = expected_replaced_role

    # Act - Call function directly
    result = replace(input_data)

    # Assert - Check result contains replaced role
    assert result.id == 3
    assert result.name == "moderator"
    assert result.description == "Replaced moderator"
    mock_service.assert_called_once()
    # Verify service was called with UserRole object
    call_args = mock_service.call_args[0][0]
    assert isinstance(call_args, UserRole)
    assert call_args.id == 3
    assert call_args.name == "moderator"
    assert call_args.description == "Replaced moderator"

def test_delete_user_role(mocker):
    """Test delete() deletes the role"""
    # Arrange - Mock service delete method
    mock_service = mocker.patch('web.user_role.service.delete')
    mock_service.return_value = None  # delete returns None

    # Act - Call function directly
    result = delete("moderator")

    # Assert - Check result is None
    assert result is None
    mock_service.assert_called_once_with("moderator")

def test_create_user_role_unique_constraint(mocker):
    """Test create() handles unique constraint violation"""
    # Arrange - Mock service to raise exception for duplicate role
    input_data = UserRoleCreate(name="admin", description="Duplicate admin role")
    mock_service = mocker.patch('web.user_role.service.create')
    mock_service.side_effect = Exception("Unique constraint violation")

    # Act & Assert - Call function and expect exception
    with pytest.raises(Exception) as exc_info:
        create(input_data)

    assert str(exc_info.value) == "Unique constraint violation"
    mock_service.assert_called_once()
    # Verify service was called with UserRoleCreate object
    call_args = mock_service.call_args[0][0]
    assert isinstance(call_args, UserRoleCreate)
    assert call_args.name == "admin"
    assert call_args.description == "Duplicate admin role"
