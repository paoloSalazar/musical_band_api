import pytest
from fastapi import HTTPException
from schemas.user_detail import UserDetailCreate, UserDetailUpdate, UserDetailResponse
from web.user_detail import get_all_by_user, get_one, create, update, delete
from exceptions import NotFoundError, DatabaseError, ConflictError


def test_get_all_by_user_success(mocker):
    """Test get_all_by_user() returns list of user details"""
    # Arrange - Mock service to return list of details
    mock_details = [
        UserDetailResponse(id=1, user_id=1, detail_type="phone", detail_value="+1234567890"),
        UserDetailResponse(id=2, user_id=1, detail_type="address", detail_value="123 Main St")
    ]
    mock_service = mocker.patch('web.user_detail.service.get_by_user_id')
    mock_service.return_value = mock_details
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = get_all_by_user(current_user=mock_current_user, user_id=1)

    # Assert - Check result
    assert len(result) == 2
    assert result[0].detail_type == "phone"
    mock_service.assert_called_once_with(1)


def test_get_all_by_user_database_error(mocker):
    """Test get_all_by_user() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    mock_service = mocker.patch('web.user_detail.service.get_by_user_id')
    mock_service.side_effect = DatabaseError("Database error")
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_all_by_user(current_user=mock_current_user, user_id=1)

    assert exc_info.value.status_code == 500
    mock_service.assert_called_once_with(1)


def test_get_one_user_detail_found(mocker):
    """Test get_one() when detail exists"""
    # Arrange - Mock service to return detail
    mock_detail = UserDetailResponse(id=1, user_id=1, detail_type="phone", detail_value="+1234567890")
    mock_service = mocker.patch('web.user_detail.service.get_one')
    mock_service.return_value = mock_detail
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = get_one(current_user=mock_current_user, user_id=1, detail_id=1)

    # Assert - Check result
    assert result.id == 1
    assert result.detail_type == "phone"
    mock_service.assert_called_once_with(1)


def test_get_one_user_detail_not_found(mocker):
    """Test get_one() when detail does not exist"""
    # Arrange - Mock service to return None
    mock_service = mocker.patch('web.user_detail.service.get_one')
    mock_service.return_value = None
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_one(current_user=mock_current_user, user_id=1, detail_id=999)

    assert exc_info.value.status_code == 404
    assert "User detail not found" in exc_info.value.detail


def test_get_one_user_detail_wrong_user(mocker):
    """Test get_one() when detail belongs to different user"""
    # Arrange - Mock service to return detail with different user_id
    mock_detail = UserDetailResponse(id=1, user_id=2, detail_type="phone", detail_value="+1234567890")
    mock_service = mocker.patch('web.user_detail.service.get_one')
    mock_service.return_value = mock_detail
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_one(current_user=mock_current_user, user_id=1, detail_id=1)

    assert exc_info.value.status_code == 404
    assert "User detail not found" in exc_info.value.detail


def test_create_user_detail_success(mocker):
    """Test create() creates and returns new user detail"""
    # Arrange - Mock service to return created detail
    input_data = UserDetailCreate(user_id=1, detail_type="phone", detail_value="+1234567890")
    expected_created_detail = UserDetailResponse(id=1, user_id=1, detail_type="phone", detail_value="+1234567890")
    mock_service = mocker.patch('web.user_detail.service.create')
    mock_service.return_value = expected_created_detail
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = create(current_user=mock_current_user, user_id=1, detail=input_data)

    # Assert - Check result
    assert result.id == 1
    assert result.detail_type == "phone"
    mock_service.assert_called_once()


def test_create_user_detail_user_id_mismatch(mocker):
    """Test create() when user_id in path doesn't match detail data"""
    # Arrange
    input_data = UserDetailCreate(user_id=2, detail_type="phone", detail_value="+1234567890")
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        create(current_user=mock_current_user, user_id=1, detail=input_data)

    assert exc_info.value.status_code == 400
    assert "User ID mismatch" in exc_info.value.detail


def test_create_user_detail_database_error(mocker):
    """Test create() handles database errors"""
    # Arrange - Mock service to raise DatabaseError
    input_data = UserDetailCreate(user_id=1, detail_type="phone", detail_value="+1234567890")
    mock_service = mocker.patch('web.user_detail.service.create')
    mock_service.side_effect = DatabaseError("Database error")
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        create(current_user=mock_current_user, user_id=1, detail=input_data)

    assert exc_info.value.status_code == 500


def test_update_user_detail_success(mocker):
    """Test update() updates and returns user detail"""
    # Arrange - Mock service to return updated detail
    input_data = UserDetailUpdate(detail_value="+0987654321")
    updated_detail = UserDetailResponse(id=1, user_id=1, detail_type="phone", detail_value="+0987654321")
    mock_service_get = mocker.patch('web.user_detail.service.get_one')
    mock_service_get.return_value = updated_detail
    mock_service_update = mocker.patch('web.user_detail.service.update')
    mock_service_update.return_value = updated_detail
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    result = update(current_user=mock_current_user, user_id=1, detail_id=1, detail=input_data)

    # Assert - Check result
    assert result.detail_value == "+0987654321"
    mock_service_update.assert_called_once()


def test_update_user_detail_not_found(mocker):
    """Test update() when detail does not exist"""
    # Arrange - Mock service to return None for get_one
    input_data = UserDetailUpdate(detail_value="+0987654321")
    mock_service_get = mocker.patch('web.user_detail.service.get_one')
    mock_service_get.return_value = None
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        update(current_user=mock_current_user, user_id=1, detail_id=999, detail=input_data)

    assert exc_info.value.status_code == 404


def test_update_user_detail_wrong_user(mocker):
    """Test update() when detail belongs to different user"""
    # Arrange - Mock service to return detail with different user_id
    input_data = UserDetailUpdate(detail_value="+0987654321")
    mock_detail = UserDetailResponse(id=1, user_id=2, detail_type="phone", detail_value="+1234567890")
    mock_service_get = mocker.patch('web.user_detail.service.get_one')
    mock_service_get.return_value = mock_detail
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        update(current_user=mock_current_user, user_id=1, detail_id=1, detail=input_data)

    assert exc_info.value.status_code == 404


def test_delete_user_detail_success(mocker):
    """Test delete() deletes user detail"""
    # Arrange - Mock service to return detail
    mock_detail = UserDetailResponse(id=1, user_id=1, detail_type="phone", detail_value="+1234567890")
    mock_service_get = mocker.patch('web.user_detail.service.get_one')
    mock_service_get.return_value = mock_detail
    mock_service_delete = mocker.patch('web.user_detail.service.delete')
    mock_service_delete.return_value = True
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act - Call function directly
    delete(current_user=mock_current_user, user_id=1, detail_id=1)

    # Assert - Check delete was called
    mock_service_delete.assert_called_once_with(1)


def test_delete_user_detail_not_found(mocker):
    """Test delete() when detail does not exist"""
    # Arrange - Mock service to return None
    mock_service_get = mocker.patch('web.user_detail.service.get_one')
    mock_service_get.return_value = None
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete(current_user=mock_current_user, user_id=1, detail_id=999)

    assert exc_info.value.status_code == 404


def test_delete_user_detail_wrong_user(mocker):
    """Test delete() when detail belongs to different user"""
    # Arrange - Mock service to return detail with different user_id
    mock_detail = UserDetailResponse(id=1, user_id=2, detail_type="phone", detail_value="+1234567890")
    mock_service_get = mocker.patch('web.user_detail.service.get_one')
    mock_service_get.return_value = mock_detail
    mock_current_user = {"sub": "test@example.com", "role": "admin"}

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete(current_user=mock_current_user, user_id=1, detail_id=1)

    assert exc_info.value.status_code == 404


def test_create_user_detail_conflict_error(mocker):
    """Test create() returns HTTP 409 when duplicate detail type exists"""
    # Arrange - Mock service to raise ConflictError
    mock_service = mocker.patch('web.user_detail.service.create')
    mock_service.side_effect = ConflictError(
        "A detail of type 'phone' already exists for this user"
    )
    mock_current_user = {"sub": "test@example.com", "role": "admin"}
    detail_data = UserDetailCreate(
        user_id=1,
        detail_type="phone",
        detail_value="+1234567890"
    )

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        create(current_user=mock_current_user, user_id=1, detail=detail_data)

    assert exc_info.value.status_code == 409
    assert "phone" in exc_info.value.detail
    mock_service.assert_called_once()


def test_update_user_detail_conflict_error(mocker):
    """Test update() returns HTTP 409 when duplicate detail type exists"""
    # Arrange - Mock service.get_one to return existing detail
    mock_existing = UserDetailResponse(id=1, user_id=1, detail_type="phone", detail_value="+1234567890")
    mock_service_get = mocker.patch('web.user_detail.service.get_one')
    mock_service_get.return_value = mock_existing

    # Mock service.update to raise ConflictError
    mock_service_update = mocker.patch('web.user_detail.service.update')
    mock_service_update.side_effect = ConflictError(
        "A detail of type 'address' already exists for this user"
    )
    mock_current_user = {"sub": "test@example.com", "role": "admin"}
    detail_data = UserDetailUpdate(detail_type="address")

    # Act & Assert - Call function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        update(current_user=mock_current_user, user_id=1, detail_id=1, detail=detail_data)

    assert exc_info.value.status_code == 409
    assert "address" in exc_info.value.detail
    mock_service_update.assert_called_once()
