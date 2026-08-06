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
    MusicianPaymentSummaryResponse,
    MusicianEventSummaryResponse,
    EventBillingSummaryResponse
)
from schemas.event_payment import PaymentType
from web.musician_event_payment import (
    create_musician_payment,
    get_musician_payments,
    get_musician_payment_summary,
    get_event_musician_payment_summary,
    get_event_billing_summary_endpoint
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


def test_get_event_musician_payment_summary_admin_success(mocker):
    """Test get_event_musician_payment_summary() returns list for admin"""
    # Arrange
    event_id = 1
    current_user = {"id": 1, "role": "admin", "permissions": ["write:musician_event_payment"]}  # Admin role requires write permission

    mock_summary_list = [
        MusicianEventSummaryResponse(
            musician_name="John Doe",
            role="Lead Guitarist",
            salary=Decimal("1000.00"),
            payment_done=Decimal("300.00"),
            remaining_payment=Decimal("700.00")
        ),
        MusicianEventSummaryResponse(
            musician_name="Jane Smith",
            role="Vocalist",
            salary=Decimal("800.00"),
            payment_done=Decimal("500.00"),
            remaining_payment=Decimal("300.00")
        )
    ]
    mock_service = mocker.patch('web.musician_event_payment.service.get_musician_payment_summary_for_event')
    mock_service.return_value = mock_summary_list

    # Act
    response = get_event_musician_payment_summary(event_id, current_user)

    # Assert
    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].musician_name == "John Doe"
    assert response[0].role == "Lead Guitarist"
    assert response[0].salary == Decimal("1000.00")
    assert response[0].payment_done == Decimal("300.00")
    assert response[0].remaining_payment == Decimal("700.00")
    assert response[1].musician_name == "Jane Smith"
    assert response[1].role == "Vocalist"
    assert response[1].salary == Decimal("800.00")
    assert response[1].payment_done == Decimal("500.00")
    assert response[1].remaining_payment == Decimal("300.00")
    mock_service.assert_called_once_with(event_id, current_user)


def test_get_event_musician_payment_summary_unauthorized(mocker):
    """Test get_event_musician_payment_summary() raises HTTPException for non-admin"""
    # Arrange
    event_id = 1
    current_user = {"id": 1, "role": "user", "permissions": []}  # Regular user

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_event_musician_payment_summary(event_id, current_user)

    assert exc_info.value.status_code == 403  # Forbidden
    assert "You can only view payment summaries for your own events" in str(exc_info.value.detail)


def test_get_event_billing_summary_admin_success(mocker):
    """Test get_event_billing_summary_endpoint() returns billing summary for admin"""
    # Arrange
    event_id = 1
    current_user = {"id": 1, "role": "admin", "permissions": ["read:musician_event_payment"]}

    mock_billing_summary = EventBillingSummaryResponse(
        event_name="Summer Festival",
        event_price=Decimal("4000.00"),
        payment_done=Decimal("4000.00"),
        sum_of_musician_salaries=Decimal("1050.00"),
        remaining_payment=Decimal("0.00"),
        payment_done_to_musicians=Decimal("350.00")
    )
    mock_service = mocker.patch('web.musician_event_payment.service.get_event_billing_summary')
    mock_service.return_value = mock_billing_summary

    # Act
    response = get_event_billing_summary_endpoint(event_id, current_user)

    # Assert
    assert isinstance(response, EventBillingSummaryResponse)
    assert response.event_name == "Summer Festival"
    assert response.event_price == Decimal("4000.00")
    assert response.payment_done == Decimal("4000.00")
    assert response.sum_of_musician_salaries == Decimal("1050.00")
    assert response.remaining_payment == Decimal("0.00")
    assert response.payment_done_to_musicians == Decimal("350.00")
    mock_service.assert_called_once_with(event_id, current_user)


def test_get_event_billing_summary_owner_success(mocker):
    """Test get_event_billing_summary_endpoint() returns billing summary for event owner"""
    # Arrange
    event_id = 1
    current_user = {"id": 1, "role": "user", "permissions": ["read:musician_event_payment"]}  # User is owner

    mock_billing_summary = EventBillingSummaryResponse(
        event_name="Winter Concert",
        event_price=Decimal("2500.00"),
        payment_done=Decimal("2500.00"),
        sum_of_musician_salaries=Decimal("1500.00"),
        remaining_payment=Decimal("0.00"),
        payment_done_to_musicians=Decimal("1500.00")
    )
    mock_service = mocker.patch('web.musician_event_payment.service.get_event_billing_summary')
    mock_service.return_value = mock_billing_summary

    # Act
    response = get_event_billing_summary_endpoint(event_id, current_user)

    # Assert
    assert isinstance(response, EventBillingSummaryResponse)
    assert response.event_name == "Winter Concert"
    assert response.event_price == Decimal("2500.00")
    assert response.payment_done == Decimal("2500.00")
    assert response.sum_of_musician_salaries == Decimal("1500.00")
    assert response.remaining_payment == Decimal("0.00")
    assert response.payment_done_to_musicians == Decimal("1500.00")
    mock_service.assert_called_once_with(event_id, current_user)


def test_get_event_billing_summary_unauthorized(mocker):
    """Test get_event_billing_summary_endpoint() raises HTTPException for non-owner, non-admin"""
    # Arrange
    event_id = 1
    current_user = {"id": 2, "role": "user", "permissions": []}  # Not admin, not owner

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_event_billing_summary_endpoint(event_id, current_user)

    assert exc_info.value.status_code == 403  # Forbidden
    assert "You can only view billing summaries for your own events" in str(exc_info.value.detail)


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
    """Test get_musician_payments() allows performer (helper) with proper permissions"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {"id": 2, "role": "helper", "permissions": ["read:musician_event_payment"]}  # helper allowed same as musician/auxiliar_musician
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