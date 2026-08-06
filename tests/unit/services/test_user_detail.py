import pytest
from unittest.mock import Mock, patch, MagicMock
from services.user_detail import (
    get_one,
    get_by_user_id,
    get_all,
    create,
    update,
    delete,
    delete_by_user_id,
)
from exceptions import NotFoundError, DatabaseError, ConflictError
from models.user_detail import UserDetail
from schemas.user_detail import UserDetailCreate, UserDetailUpdate, UserDetailResponse


def test_get_one_success(mocker):
    """Test get_one() returns UserDetailResponse on success"""
    # Arrange
    mock_detail = UserDetail(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )
    mock_data_get = mocker.patch('services.user_detail.data.get_one')
    mock_data_get.return_value = mock_detail

    # Act
    result = get_one(1)

    # Assert
    assert result is not None
    assert isinstance(result, UserDetailResponse)
    assert result.id == 1
    assert result.detail_type == "phone"
    mock_data_get.assert_called_once_with(1)


def test_get_one_not_found(mocker):
    """Test get_one() returns None when not found"""
    # Arrange
    mock_data_get = mocker.patch('services.user_detail.data.get_one')
    mock_data_get.return_value = None

    # Act
    result = get_one(999)

    # Assert
    assert result is None
    mock_data_get.assert_called_once_with(999)


def test_get_one_database_error(mocker):
    """Test get_one() raises DatabaseError on failure"""
    # Arrange
    mock_data_get = mocker.patch('services.user_detail.data.get_one')
    mock_data_get.side_effect = DatabaseError("Database error")

    # Act & Assert
    with pytest.raises(DatabaseError):
        get_one(1)


def test_get_by_user_id_success(mocker):
    """Test get_by_user_id() returns list of UserDetailResponse"""
    # Arrange
    mock_details = [
        UserDetail(id=1, user_id=1, detail_type="phone", detail_value="+1234567890"),
        UserDetail(id=2, user_id=1, detail_type="address", detail_value="123 Main St")
    ]
    mock_data_get = mocker.patch('services.user_detail.data.get_by_user_id')
    mock_data_get.return_value = mock_details

    # Act
    result = get_by_user_id(1)

    # Assert
    assert result is not None
    assert len(result) == 2
    assert isinstance(result[0], UserDetailResponse)
    mock_data_get.assert_called_once_with(1)


def test_get_by_user_id_empty(mocker):
    """Test get_by_user_id() returns empty list when no details"""
    # Arrange
    mock_data_get = mocker.patch('services.user_detail.data.get_by_user_id')
    mock_data_get.return_value = []

    # Act
    result = get_by_user_id(999)

    # Assert
    assert result == []
    mock_data_get.assert_called_once_with(999)


def test_get_all_success(mocker):
    """Test get_all() returns list of UserDetailResponse"""
    # Arrange
    mock_details = [
        UserDetail(id=1, user_id=1, detail_type="phone", detail_value="+1234567890"),
        UserDetail(id=2, user_id=2, detail_type="email", detail_value="test@example.com")
    ]
    mock_data_get = mocker.patch('services.user_detail.data.get_all')
    mock_data_get.return_value = mock_details

    # Act
    result = get_all()

    # Assert
    assert result is not None
    assert len(result) == 2
    mock_data_get.assert_called_once()


def test_get_all_empty(mocker):
    """Test get_all() returns empty list when no details"""
    # Arrange
    mock_data_get = mocker.patch('services.user_detail.data.get_all')
    mock_data_get.return_value = []

    # Act
    result = get_all()

    # Assert
    assert result == []
    mock_data_get.assert_called_once()


def test_create_success(mocker):
    """Test create() creates and returns UserDetailResponse"""
    # Arrange
    mock_detail = UserDetail(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )
    mock_data_create = mocker.patch('services.user_detail.data.create')
    mock_data_create.return_value = mock_detail

    detail_data = UserDetailCreate(
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )

    # Act
    result = create(detail_data)

    # Assert
    assert result is not None
    assert isinstance(result, UserDetailResponse)
    assert result.id == 1
    assert result.detail_type == "phone"
    mock_data_create.assert_called_once()


def test_create_database_error(mocker):
    """Test create() raises DatabaseError on failure"""
    # Arrange
    mock_data_create = mocker.patch('services.user_detail.data.create')
    mock_data_create.side_effect = DatabaseError("Database error")

    detail_data = UserDetailCreate(
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )

    # Act & Assert
    with pytest.raises(DatabaseError):
        create(detail_data)


def test_update_success(mocker):
    """Test update() updates and returns UserDetailResponse"""
    # Arrange
    mock_detail = UserDetail(
        id=1,
        user_id=1,
        detail_type="phone",
        detail_value="+0987654321"
    )
    mock_data_update = mocker.patch('services.user_detail.data.update')
    mock_data_update.return_value = mock_detail

    detail_data = UserDetailUpdate(detail_value="+0987654321")

    # Act
    result = update(1, detail_data)

    # Assert
    assert result is not None
    assert isinstance(result, UserDetailResponse)
    assert result.detail_value == "+0987654321"
    mock_data_update.assert_called_once()


def test_update_not_found(mocker):
    """Test update() returns None when not found"""
    # Arrange
    mock_data_update = mocker.patch('services.user_detail.data.update')
    mock_data_update.return_value = None

    detail_data = UserDetailUpdate(detail_value="+0987654321")

    # Act
    result = update(999, detail_data)

    # Assert
    assert result is None
    mock_data_update.assert_called_once()


def test_delete_success(mocker):
    """Test delete() returns True on success"""
    # Arrange
    mock_data_delete = mocker.patch('services.user_detail.data.delete')
    mock_data_delete.return_value = True

    # Act
    result = delete(1)

    # Assert
    assert result is True
    mock_data_delete.assert_called_once_with(1)


def test_delete_not_found(mocker):
    """Test delete() returns False when not found"""
    # Arrange
    mock_data_delete = mocker.patch('services.user_detail.data.delete')
    mock_data_delete.return_value = False

    # Act
    result = delete(999)

    # Assert
    assert result is False
    mock_data_delete.assert_called_once_with(999)


def test_delete_by_user_id_success(mocker):
    """Test delete_by_user_id() returns True on success"""
    # Arrange
    mock_data_delete = mocker.patch('services.user_detail.data.delete_by_user_id')
    mock_data_delete.return_value = True

    # Act
    result = delete_by_user_id(1)

    # Assert
    assert result is True
    mock_data_delete.assert_called_once_with(1)


def test_delete_by_user_id_not_found(mocker):
    """Test delete_by_user_id() returns False when not found"""
    # Arrange
    mock_data_delete = mocker.patch('services.user_detail.data.delete_by_user_id')
    mock_data_delete.return_value = False

    # Act
    result = delete_by_user_id(999)

    # Assert
    assert result is False
    mock_data_delete.assert_called_once_with(999)


def test_create_conflict_error(mocker):
    """Test create() raises ConflictError when duplicate detail type exists"""
    # Arrange
    mock_data_create = mocker.patch('services.user_detail.data.create')
    mock_data_create.side_effect = ConflictError(
        "A detail of type 'phone' already exists for this user"
    )

    detail_data = UserDetailCreate(
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )

    # Act & Assert
    with pytest.raises(ConflictError) as exc_info:
        create(detail_data)
    
    assert "phone" in str(exc_info.value)
    mock_data_create.assert_called_once()


def test_update_conflict_error(mocker):
    """Test update() raises ConflictError when duplicate detail type exists"""
    # Arrange
    mock_data_update = mocker.patch('services.user_detail.data.update')
    mock_data_update.side_effect = ConflictError(
        "A detail of type 'address' already exists for this user"
    )

    detail_data = UserDetailUpdate(detail_type="address")

    # Act & Assert
    with pytest.raises(ConflictError) as exc_info:
        update(1, detail_data)
    
    assert "address" in str(exc_info.value)
    mock_data_update.assert_called_once()
