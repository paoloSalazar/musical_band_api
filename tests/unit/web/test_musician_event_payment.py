"""
Unit tests for MusicianEventPayment web layer.

These tests follow TDD approach - they define expected behavior before the web layer exists.
Tests should FAIL until the web/musician_event_payment.py module is implemented.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException
from schemas.musician_event_payment import (
    MusicianEventPaymentCreate,
    MusicianEventPaymentResponse,
    MusicianPaymentSummaryResponse
)
from schemas.event_payment import PaymentType
from web.musician_event_payment import (
    create_musician_payment,
    get_musician_payments,
    get_musician_payment_summary,
)
from exceptions import NotFoundError, ValidationError, UnauthorizedError


def test_create_musician_payment_success(mocker):
    """Test create_musician_payment() successfully creates payment"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "admin", "permissions": ["write:musician_event_payment"]}
    payment_data = MusicianEventPaymentCreate(
        event_id=event_id,
        musician_id=musician_id,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        notes="Advance payment"
    )

    mock_response = MusicianEventPaymentResponse(
        id=1,
        event_id=event_id,
        musician_id=musician_id,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=payment_data.payment_date,
        notes="Advance payment",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_service = mocker.patch('web.musician_event_payment.service.create_musician_payment')
    mock_service.return_value = mock_response

    # Act
    result = create_musician_payment(
        event_id=event_id,
        musician_id=musician_id,
        payment=payment_data,
        current_user=current_user
    )

    # Assert
    assert result.id == 1
    assert result.amount == Decimal("500.00")
    mock_service.assert_called_once_with(payment_data, current_user)


def test_create_musician_payment_validation_error(mocker):
    """Test create_musician_payment() handles ValidationError"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "admin", "permissions": ["write:musician_event_payment"]}
    payment_data = MusicianEventPaymentCreate(
        event_id=event_id,
        musician_id=musician_id,
        amount=Decimal("2000.00"),  # Exceeds salary
        payment_type=PaymentType.TOTAL,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    mock_service = mocker.patch('web.musician_event_payment.service.create_musician_payment')
    mock_service.side_effect = ValidationError("Payment amount exceeds musician's salary")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_musician_payment(
            event_id=event_id,
            musician_id=musician_id,
            payment=payment_data,
            current_user=current_user
        )

    assert exc_info.value.status_code == 400
    assert "Payment amount exceeds musician's salary" in exc_info.value.detail


def test_create_musician_payment_not_found_error(mocker):
    """Test create_musician_payment() handles NotFoundError"""
    # Arrange
    event_id = 999
    musician_id = 2
    current_user = {"id": 1, "role": "admin", "permissions": ["write:musician_event_payment"]}
    payment_data = MusicianEventPaymentCreate(
        event_id=event_id,
        musician_id=musician_id,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    mock_service = mocker.patch('web.musician_event_payment.service.create_musician_payment')
    mock_service.side_effect = NotFoundError("Event with id 999 not found")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_musician_payment(
            event_id=event_id,
            musician_id=musician_id,
            payment=payment_data,
            current_user=current_user
        )

    assert exc_info.value.status_code == 404
    assert "Event with id 999 not found" in exc_info.value.detail


def test_create_musician_payment_unauthorized_error(mocker):
    """Test create_musician_payment() handles UnauthorizedError"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 2, "role": "user"}  # Not owner
    payment_data = MusicianEventPaymentCreate(
        event_id=event_id,
        musician_id=musician_id,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    mock_service = mocker.patch('web.musician_event_payment.service.create_musician_payment')
    mock_service.side_effect = UnauthorizedError("You can only manage payments for your own events")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_musician_payment(
            event_id=event_id,
            musician_id=musician_id,
            payment=payment_data,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403
    assert "You can only manage payments for your own events" in exc_info.value.detail


def test_get_musician_payments_success(mocker):
    """Test get_musician_payments() returns payments for event and musician"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "admin", "permissions": ["write:musician_event_payment"]}
    mock_payments = [
        MusicianEventPaymentResponse(
            id=1,
            event_id=event_id,
            musician_id=musician_id,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
            notes="Advance",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    ]
    mock_service = mocker.patch('web.musician_event_payment.service.get_payments_for_event')
    mock_service.return_value = mock_payments

    # Act
    result = get_musician_payments(
        event_id=event_id,
        musician_id=musician_id,
        current_user=current_user
    )

    # Assert
    assert len(result) == 1
    assert result[0].event_id == event_id
    assert result[0].musician_id == musician_id
    mock_service.assert_called_once_with(event_id, musician_id, current_user)


def test_get_musician_payments_unauthorized(mocker):
    """Test get_musician_payments() handles UnauthorizedError"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 2, "role": "user"}

    mock_service = mocker.patch('web.musician_event_payment.service.get_payments_for_event')
    mock_service.side_effect = UnauthorizedError("Unauthorized to view musician payments")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_musician_payments(
            event_id=event_id,
            musician_id=musician_id,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403
    assert "Unauthorized to view musician payments" in exc_info.value.detail


def test_get_musician_payment_summary_success(mocker):
    """Test get_musician_payment_summary() returns payment summary"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "admin", "permissions": ["write:musician_event_payment"]}
    mock_summary = MusicianPaymentSummaryResponse(
        musician_id=musician_id,
        total_paid=Decimal("800.00"),
        payment_count=2
    )
    mock_service = mocker.patch('web.musician_event_payment.service.get_payment_summary_for_musician_event')
    mock_service.return_value = mock_summary

    # Act
    result = get_musician_payment_summary(
        event_id=event_id,
        musician_id=musician_id,
        current_user=current_user
    )

    # Assert
    assert result.musician_id == musician_id
    assert result.total_paid == Decimal("800.00")
    assert result.payment_count == 2
    mock_service.assert_called_once_with(event_id, musician_id, current_user)


def test_get_musician_payment_summary_not_found(mocker):
    """Test get_musician_payment_summary() handles NotFoundError"""
    # Arrange
    event_id = 999
    musician_id = 2
    current_user = {"id": 1, "role": "admin", "permissions": ["write:musician_event_payment"]}

    mock_service = mocker.patch('web.musician_event_payment.service.get_payment_summary_for_musician_event')
    mock_service.side_effect = NotFoundError("Event with id 999 not found")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_musician_payment_summary(
            event_id=event_id,
            musician_id=musician_id,
            current_user=current_user
        )

    assert exc_info.value.status_code == 404
    assert "Event with id 999 not found" in exc_info.value.detail


def test_get_musician_payments_musician_authorized(mocker):
    """Test get_musician_payments() allows musician with proper permissions"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 2, "role": "musician", "permissions": ["read:musician_event_payment"]}
    mock_payments = [
        MusicianEventPaymentResponse(
            id=1,
            event_id=event_id,
            musician_id=musician_id,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
            notes="Advance",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    ]
    mock_service = mocker.patch('web.musician_event_payment.service.get_payments_for_event')
    mock_service.return_value = mock_payments

    # Act
    result = get_musician_payments(
        event_id=event_id,
        musician_id=musician_id,
        current_user=current_user
    )

    # Assert
    assert len(result) == 1
    assert result[0].musician_id == musician_id
    mock_service.assert_called_once_with(event_id, musician_id, current_user)


def test_get_musician_payments_musician_missing_permission(mocker):
    """Test get_musician_payments() denies musician without required permission"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 2, "role": "musician", "permissions": []}  # Missing permission

    # Mock the service to simulate authorization failure
    mock_service = mocker.patch('web.musician_event_payment.service.get_payments_for_event')
    mock_service.side_effect = UnauthorizedError("Unauthorized to view musician payments")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_musician_payments(
            event_id=event_id,
            musician_id=musician_id,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403
    assert "Unauthorized to view musician payments" in exc_info.value.detail


def test_get_musician_payments_wrong_role(mocker):
    """Test get_musician_payments() denies user with wrong role"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 2, "role": "user", "permissions": ["read:musician_event_payment"]}  # Wrong role

    # Mock the service to simulate authorization failure
    mock_service = mocker.patch('web.musician_event_payment.service.get_payments_for_event')
    mock_service.side_effect = UnauthorizedError("Unauthorized to view musician payments")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_musician_payments(
            event_id=event_id,
            musician_id=musician_id,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403
    assert "Unauthorized to view musician payments" in exc_info.value.detail


def test_create_musician_payment_admin_authorized(mocker):
    """Test create_musician_payment() allows admin with proper permissions"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "admin", "permissions": ["write:musician_event_payment"]}
    payment_data = MusicianEventPaymentCreate(
        event_id=event_id,
        musician_id=musician_id,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        notes="Advance payment"
    )

    mock_response = MusicianEventPaymentResponse(
        id=1,
        event_id=event_id,
        musician_id=musician_id,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=payment_data.payment_date,
        notes="Advance payment",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_service = mocker.patch('web.musician_event_payment.service.create_musician_payment')
    mock_service.return_value = mock_response

    # Act
    result = create_musician_payment(
        event_id=event_id,
        musician_id=musician_id,
        payment=payment_data,
        current_user=current_user
    )

    # Assert
    assert result.id == 1
    assert result.event_id == event_id
    mock_service.assert_called_once_with(payment_data, current_user)


def test_create_musician_payment_musician_denied(mocker):
    """Test create_musician_payment() denies musician even with permission"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 2, "role": "musician", "permissions": ["write:musician_event_payment"]}
    payment_data = MusicianEventPaymentCreate(
        event_id=event_id,
        musician_id=musician_id,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        notes="Advance payment"
    )

    # Mock the service to simulate authorization failure
    mock_service = mocker.patch('web.musician_event_payment.service.create_musician_payment')
    mock_service.side_effect = UnauthorizedError("You can only manage payments for your own events")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_musician_payment(
            event_id=event_id,
            musician_id=musician_id,
            payment=payment_data,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403
    assert "You can only manage payments for your own events" in exc_info.value.detail


def test_create_musician_payment_admin_missing_permission(mocker):
    """Test create_musician_payment() denies admin without required permission"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 1, "role": "admin", "permissions": []}  # Missing permission
    payment_data = MusicianEventPaymentCreate(
        event_id=event_id,
        musician_id=musician_id,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        notes="Advance payment"
    )

    # Mock all the service dependencies to avoid validation errors
    mock_event = mocker.patch('web.musician_event_payment.service.event_data.get_one')
    mock_event.return_value = type('MockEvent', (), {'user_id': 1})()

    mock_musician = mocker.patch('web.musician_event_payment.service.user_data.get_one_by_id')
    mock_musician.return_value = type('MockMusician', (), {'id': musician_id})()

    mock_assignment = mocker.patch('web.musician_event_payment.service.assignment_data.get_by_event_and_musician')
    mock_assignment.return_value = type('MockAssignment', (), {'salary': Decimal("1000.00")})()

    # Mock the service to simulate permission failure
    mock_service = mocker.patch('web.musician_event_payment.service.create_musician_payment')
    mock_service.side_effect = UnauthorizedError("Missing required permission")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_musician_payment(
            event_id=event_id,
            musician_id=musician_id,
            payment=payment_data,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403
    assert "Missing required permission" in exc_info.value.detail