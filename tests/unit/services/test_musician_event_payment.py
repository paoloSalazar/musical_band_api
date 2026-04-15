"""
Unit tests for MusicianEventPayment services layer.

These tests follow TDD approach - they define expected behavior before the services layer exists.
Tests should FAIL until the services/musician_event_payment.py module is implemented.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import Mock
from services.musician_event_payment import (
    create_musician_payment,
    get_payments_for_event,
    get_payments_for_musician,
    get_payment_summary_for_musician_event,
    get_payment_summary_for_musician
)
from schemas.musician_event_payment import (
    MusicianEventPaymentCreate,
    MusicianEventPaymentResponse
)
from schemas.event_payment import PaymentType
from models.musician_event_payment import MusicianEventPayment
from models.event_musician import EventMusician
from exceptions import (
    NotFoundError,
    DatabaseError,
    UnauthorizedError,
    ValidationError,
)


def test_create_musician_payment_success(mocker):
    """Test create_musician_payment() creates payment successfully"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        notes="Advance payment for musician"
    )

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    now = datetime.now(timezone.utc)
    mock_payment = MusicianEventPayment(
            id=1,
            event_id=1,
            musician_id=2,
            amount=Decimal("500.00"),
            payment_type=PaymentType.ADVANCE,
            payment_date=payment_data.payment_date,
            notes="Advance payment for musician",
            created_at=now,
            updated_at=now
        )
    mock_payment_data_create = mocker.patch('services.musician_event_payment.payment_data.create')
    mock_payment_data_create.return_value = mock_payment

    # Act
    result = create_musician_payment(payment_data, current_user)

    # Assert
    assert result.id == 1
    assert result.amount == Decimal("500.00")
    mock_event_data_get.assert_called_once_with(1)
    mock_user_data_get.assert_called_once_with(2)
    mock_assignment_data_get.assert_called_once_with(1, 2)
    mock_payment_data_create.assert_called_once()


def test_create_musician_payment_event_not_found(mocker):
    """Test create_musician_payment() raises NotFoundError when event doesn't exist"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=999,
        musician_id=2,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        create_musician_payment(payment_data, current_user)

    assert "Event with id 999 not found" in str(exc_info.value)


def test_create_musician_payment_musician_not_found(mocker):
    """Test create_musician_payment() raises NotFoundError when musician doesn't exist"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=999,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        create_musician_payment(payment_data, current_user)

    assert "Musician with id 999 not found" in str(exc_info.value)


def test_create_musician_payment_not_assigned(mocker):
    """Test create_musician_payment() raises ValidationError when musician not assigned to event"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = None  # No assignment

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        create_musician_payment(payment_data, current_user)

    assert "Musician is not assigned to this event" in str(exc_info.value)


def test_create_musician_payment_amount_exceeds_salary(mocker):
    """Test create_musician_payment() raises ValidationError when payment exceeds salary"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("1200.00"),
        payment_type=PaymentType.TOTAL,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1000.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        create_musician_payment(payment_data, current_user)

    assert "Payment amount (1200.00) exceeds musician's salary (1000.00)" in str(exc_info.value)


def test_get_payments_for_event_success(mocker):
    """Test get_payments_for_event() returns payments for event owner"""
    # Arrange
    event_id = 1
    current_user = {'id': 1, 'role': 'user'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    now = datetime.now(timezone.utc)
    mock_payments = [
        MusicianEventPayment(id=1, event_id=1, musician_id=2, amount=Decimal("500.00"), payment_type=PaymentType.ADVANCE, payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc), created_at=now, updated_at=now),
        MusicianEventPayment(id=2, event_id=1, musician_id=3, amount=Decimal("300.00"), payment_type=PaymentType.REMAINING, payment_date=datetime(2023, 10, 2, 12, 0, 0, tzinfo=timezone.utc), created_at=now, updated_at=now)
    ]
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event')
    mock_payment_data_get.return_value = mock_payments

    # Act
    result = get_payments_for_event(event_id, current_user)

    # Assert
    assert len(result) == 2
    mock_event_data_get.assert_called_once_with(event_id)
    mock_payment_data_get.assert_called_once_with(event_id)


def test_get_payments_for_event_unauthorized(mocker):
    """Test get_payments_for_event() raises UnauthorizedError for non-owner"""
    # Arrange
    event_id = 1
    current_user = {'id': 2, 'role': 'user'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1  # Different user
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_payments_for_event(event_id, current_user)

    assert "You can only manage payments for your own events" in str(exc_info.value)


def test_get_payments_for_musician_success(mocker):
    """Test get_payments_for_musician() returns payments for musician"""
    # Arrange
    musician_id = 2
    current_user = {'id': 2, 'role': 'musician'}

    now = datetime.now(timezone.utc)
    mock_payments = [
        MusicianEventPayment(id=1, event_id=1, musician_id=2, amount=Decimal("500.00"), payment_type=PaymentType.ADVANCE, payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc), created_at=now, updated_at=now),
        MusicianEventPayment(id=2, event_id=2, musician_id=2, amount=Decimal("300.00"), payment_type=PaymentType.REMAINING, payment_date=datetime(2023, 10, 2, 12, 0, 0, tzinfo=timezone.utc), created_at=now, updated_at=now)
    ]
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_musician')
    mock_payment_data_get.return_value = mock_payments

    # Act
    result = get_payments_for_musician(musician_id, current_user)

    # Assert
    assert len(result) == 2
    mock_payment_data_get.assert_called_once_with(musician_id)


def test_get_payments_for_musician_unauthorized(mocker):
    """Test get_payments_for_musician() raises UnauthorizedError for non-owner"""
    # Arrange
    musician_id = 2
    current_user = {'id': 1, 'role': 'musician'}

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_payments_for_musician(musician_id, current_user)

    assert "You can only view your own payment history" in str(exc_info.value)


def test_get_payment_summary_for_musician_event_success(mocker):
    """Test get_payment_summary_for_musician_event() returns summary"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {'id': 1, 'role': 'admin'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total.return_value = Decimal("800.00")

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1500.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Act
    result = get_payment_summary_for_musician_event(event_id, musician_id, current_user)

    # Assert
    assert result.musician_id == 2
    assert result.total_paid == Decimal("800.00")
    mock_payment_data_total.assert_called_once_with(event_id, musician_id)


def test_get_payment_summary_for_musician_success(mocker):
    """Test get_payment_summary_for_musician() returns summary"""
    # Arrange
    musician_id = 2
    current_user = {'id': 2, 'role': 'musician'}

    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician')
    mock_payment_data_total.return_value = Decimal("2500.00")

    # Act
    result = get_payment_summary_for_musician(musician_id, current_user)

    # Assert
    assert result.musician_id == 2
    assert result.total_paid == Decimal("2500.00")
    mock_payment_data_total.assert_called_once_with(musician_id)