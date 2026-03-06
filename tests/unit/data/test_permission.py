import pytest
from models.permission import Permission
from models.user_role import UserRole
import data.permission as data
from sqlalchemy.exc import SQLAlchemyError
from exceptions import DatabaseError, ConflictError


def test_get_one_permission_found(mocker):
    """Test get_one() when permission exists"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = Permission(
        id=1,
        name="read:users",
        description="Permission to read users"
    )

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one(1)

    # Assert - Check result and session calls
    assert result is not None
    assert result.id == 1
    assert result.name == "read:users"
    assert result.description == "Permission to read users"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.query.assert_called_once_with(Permission)
    mock_query.filter.assert_called_once()
    mock_query.first.assert_called_once()


def test_get_one_permission_not_found(mocker):
    """Test get_one() when permission does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_one(99)

    # Assert - Check result is None and session calls
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_one_permission_database_error(mocker):
    """Test get_one() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and query to raise SQLAlchemyError
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_one(1)

    assert "Failed to get permission" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_not_called()  # No rollback for read operations


def test_get_by_name_permission_found(mocker):
    """Test get_by_name() when permission exists"""
    # Arrange - Mock SessionLocal and query
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = Permission(
        id=1,
        name="read:users",
        description="Permission to read users"
    )

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_by_name("read:users")

    # Assert - Check result and session calls
    assert result is not None
    assert result.id == 1
    assert result.name == "read:users"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_query.filter.assert_called_once()


def test_get_by_name_permission_not_found(mocker):
    """Test get_by_name() when permission does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_by_name("nonexistent")

    # Assert - Check result is None and session calls
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_all_permissions_empty(mocker):
    """Test get_all() returns empty list when no permissions"""
    # Arrange - Mock SessionLocal and query to return empty list
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = []

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_all()

    # Assert - Check result is empty list
    assert result == []
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.query.assert_called_once_with(Permission)
    mock_query.all.assert_called_once()


def test_get_all_permissions_with_data(mocker):
    """Test get_all() returns permissions when they exist"""
    # Arrange - Mock SessionLocal and query to return permissions
    permissions = [
        Permission(id=1, name="read:users", description="Permission to read users"),
        Permission(id=2, name="write:users", description="Permission to write users")
    ]
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = permissions

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_all()

    # Assert - Check result contains the expected permissions
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "read:users"
    assert result[1].id == 2
    assert result[1].name == "write:users"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_all_permissions_database_error(mocker):
    """Test get_all() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and query to raise SQLAlchemyError
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.all.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_all()

    assert "Failed to get all permissions" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_not_called()  # No rollback for read operations


def test_create_permission(mocker):
    """Test create() function"""
    # Arrange - Mock SessionLocal
    permission = Permission(name="delete:users", description="Permission to delete users")
    # Simulate database setting the ID
    permission.id = 3
    mock_session = mocker.Mock()
    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.create(permission)

    # Assert - Check session methods were called correctly
    assert result == permission
    assert result.id == 3
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.add.assert_called_once_with(permission)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(permission)


def test_create_permission_database_error(mocker):
    """Test create() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and commit to raise SQLAlchemyError
    permission = Permission(name="delete:users", description="Permission to delete users")
    mock_session = mocker.Mock()
    mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.create(permission)

    assert "Failed to create permission" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_called_once()  # Rollback should be called on error


def test_update_permission_found(mocker):
    """Test update() when permission exists"""
    # Arrange - Mock SessionLocal and query
    from schemas.permission import PermissionUpdate
    permission_update = PermissionUpdate(description="Updated description")
    existing_permission = Permission(
        id=1,
        name="read:users",
        description="Permission to read users"
    )

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_permission

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.update(1, permission_update)

    # Assert - Check result and that description was updated
    assert result == existing_permission
    assert existing_permission.description == "Updated description"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_permission)


def test_update_permission_not_found(mocker):
    """Test update() when permission does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    from schemas.permission import PermissionUpdate
    permission_update = PermissionUpdate(description="Updated description")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.update(99, permission_update)

    # Assert - Check result is None and commit/refresh not called
    assert result is None
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()


def test_update_permission_database_error(mocker):
    """Test update() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and commit to raise SQLAlchemyError
    from schemas.permission import PermissionUpdate
    permission_update = PermissionUpdate(description="Updated description")
    existing_permission = Permission(
        id=1,
        name="read:users",
        description="Permission to read users"
    )

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_permission
    mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.update(1, permission_update)

    assert "Failed to update permission" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_called_once()  # Rollback should be called on error


def test_delete_permission_success(mocker):
    """Test delete() when permission exists"""
    # Arrange - Mock SessionLocal and query
    existing_permission = Permission(
        id=1,
        name="read:users",
        description="Permission to read users"
    )

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_permission

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.delete(1)

    # Assert - Check result is True and delete was called
    assert result is True
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.delete.assert_called_once_with(existing_permission)
    mock_session.commit.assert_called_once()


def test_delete_permission_not_found(mocker):
    """Test delete() when permission does not exist"""
    # Arrange - Mock SessionLocal and query to return None
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.delete(99)

    # Assert - Check result is False and delete/commit not called
    assert result is False
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


def test_delete_permission_database_error(mocker):
    """Test delete() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and commit to raise SQLAlchemyError
    existing_permission = Permission(
        id=1,
        name="read:users",
        description="Permission to read users"
    )

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_permission
    mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.delete(1)

    assert "Failed to delete permission" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_called_once()  # Rollback should be called on error


def test_delete_by_name_permission_assigned_to_roles(mocker):
    """Test delete_by_name() raises ConflictError when permission is assigned to roles"""
    # Arrange - Mock permission that has roles assigned
    role_admin = UserRole(id=1, name="admin", description="Administrator")
    role_moderator = UserRole(id=2, name="moderator", description="Moderator")
    
    existing_permission = Permission(
        id=1,
        name="read:user_roles",
        description="Permission to read user roles"
    )
    # Set up the roles relationship
    existing_permission.roles = [role_admin, role_moderator]

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = existing_permission

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect ConflictError
    with pytest.raises(ConflictError) as exc_info:
        data.delete_by_name("read:user_roles")

    assert "read:user_roles" in str(exc_info.value)
    assert "admin" in str(exc_info.value)
    assert "moderator" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    # Verify delete and commit were NOT called
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


# ============================================
# Role-Permission Assignment Tests
# ============================================

def test_assign_permission_to_role_success(mocker):
    """Test assign_permission_to_role() when both exist and not already assigned"""
    # Arrange - Mock SessionLocal and queries
    permission = Permission(id=1, name="read:users", description="Permission to read users")
    role = UserRole(id=1, name="admin", description="Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    # First call: get permission by id
    # Second call: get role by id
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [permission, role]

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.assign_permission_to_role(1, 1)

    # Assert - Check result and that permission was added to role
    assert result is True
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_called_once()


def test_assign_permission_to_role_permission_not_found(mocker):
    """Test assign_permission_to_role() when permission does not exist"""
    # Arrange - Mock SessionLocal and queries
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    # First call: get permission by id returns None
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [None, None]

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.assign_permission_to_role(99, 1)

    assert "Failed to assign permission" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    # Note: rollback not called because no DB transaction was started


def test_assign_permission_to_role_role_not_found(mocker):
    """Test assign_permission_to_role() when role does not exist"""
    # Arrange - Mock SessionLocal and queries
    permission = Permission(id=1, name="read:users", description="Permission to read users")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    # First call: get permission by id
    # Second call: get role by id returns None
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [permission, None]

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.assign_permission_to_role(1, 99)

    assert "Failed to assign permission" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    # Note: rollback not called because no DB transaction was started


def test_assign_permission_to_role_already_assigned(mocker):
    """Test assign_permission_to_role() when permission is already assigned to role"""
    # Arrange - Mock SessionLocal and queries
    permission = Permission(id=1, name="read:users", description="Permission to read users")
    role = UserRole(id=1, name="admin", description="Administrator")
    role.permissions.append(permission)  # Permission already assigned

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [permission, role]

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.assign_permission_to_role(1, 1)

    # Assert - Check result is True but no commit should happen
    assert result is True
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_not_called()


def test_assign_permission_to_role_database_error(mocker):
    """Test assign_permission_to_role() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and queries
    permission = Permission(id=1, name="read:users", description="Permission to read users")
    role = UserRole(id=1, name="admin", description="Administrator")

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [permission, role]
    mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.assign_permission_to_role(1, 1)

    assert "Failed to assign permission" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_called_once()


def test_remove_permission_from_role_success(mocker):
    """Test remove_permission_from_role() when both exist and permission is assigned"""
    # Arrange - Mock SessionLocal and queries
    permission = Permission(id=1, name="read:users", description="Permission to read users")
    role = UserRole(id=1, name="admin", description="Administrator")
    role.permissions.append(permission)  # Permission assigned

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [permission, role]

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.remove_permission_from_role(1, 1)

    # Assert - Check result and that permission was removed from role
    assert result is True
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_called_once()


def test_remove_permission_from_role_permission_not_found(mocker):
    """Test remove_permission_from_role() when permission does not exist"""
    # Arrange - Mock SessionLocal and queries
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [None, None]

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.remove_permission_from_role(99, 1)

    assert "Failed to remove permission" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    # Note: rollback not called because no DB transaction was started


def test_remove_permission_from_role_not_assigned(mocker):
    """Test remove_permission_from_role() when permission is not assigned to role"""
    # Arrange - Mock SessionLocal and queries
    permission = Permission(id=1, name="read:users", description="Permission to read users")
    role = UserRole(id=1, name="admin", description="Administrator")
    # Permission NOT assigned (no append)

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [permission, role]

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.remove_permission_from_role(1, 1)

    # Assert - Check result is True but no commit should happen
    assert result is True
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_not_called()


def test_remove_permission_from_role_database_error(mocker):
    """Test remove_permission_from_role() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and queries
    permission = Permission(id=1, name="read:users", description="Permission to read users")
    role = UserRole(id=1, name="admin", description="Administrator")
    role.permissions.append(permission)

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [permission, role]
    mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.remove_permission_from_role(1, 1)

    assert "Failed to remove permission" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_called_once()


def test_get_role_permissions_success(mocker):
    """Test get_role_permissions() returns list of permissions for a role"""
    # Arrange - Mock SessionLocal and queries
    role = UserRole(id=1, name="admin", description="Administrator")
    permissions = [
        Permission(id=1, name="read:users", description="Permission to read users"),
        Permission(id=2, name="write:users", description="Permission to write users")
    ]
    role.permissions.extend(permissions)

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = role

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_role_permissions(1)

    # Assert - Check result contains the expected permissions
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "read:users"
    assert result[1].id == 2
    assert result[1].name == "write:users"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_role_permissions_role_not_found(mocker):
    """Test get_role_permissions() when role does not exist"""
    # Arrange - Mock SessionLocal and queries
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_role_permissions(99)

    assert "Failed to get role permissions" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_role_permissions_database_error(mocker):
    """Test get_role_permissions() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and queries
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_role_permissions(1)

    assert "Failed to get role permissions" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_permission_roles_success(mocker):
    """Test get_permission_roles() returns list of roles for a permission"""
    # Arrange - Mock SessionLocal and queries
    permission = Permission(id=1, name="read:users", description="Permission to read users")
    roles = [
        UserRole(id=1, name="admin", description="Administrator"),
        UserRole(id=2, name="moderator", description="Moderator")
    ]
    # Set up the many-to-many relationship
    permission.roles = roles

    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = permission

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function
    result = data.get_permission_roles(1)

    # Assert - Check result contains the expected roles
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == "admin"
    assert result[1].id == 2
    assert result[1].name == "moderator"
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_permission_roles_permission_not_found(mocker):
    """Test get_permission_roles() when permission does not exist"""
    # Arrange - Mock SessionLocal and queries
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_permission_roles(99)

    assert "Failed to get permission roles" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_permission_roles_database_error(mocker):
    """Test get_permission_roles() raises DatabaseError on SQLAlchemyError"""
    # Arrange - Mock SessionLocal and queries
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = SQLAlchemyError("Database connection failed")

    mock_session_local = mocker.patch('data.permission.SessionLocal')
    mock_session_local.return_value = mock_session

    # Act & Assert - Call data function and expect DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        data.get_permission_roles(1)

    assert "Failed to get permission roles" in str(exc_info.value)
    mock_session_local.assert_called_once()
    mock_session.close.assert_called_once()
