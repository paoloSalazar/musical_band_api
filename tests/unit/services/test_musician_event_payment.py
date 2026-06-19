"""
Unit tests for MusicianEventPayment services layer.

These tests follow TDD approach - they define expected behavior before the services layer exists.
Tests should FAIL until the services/musician_event_payment.py module is implemented.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import Mock
from freezegun import freeze_time
from services.musician_event_payment import (
    create_musician_payment,
    get_payments_for_event,
    get_payments_for_musician,
    get_payment_summary_for_musician_event,
    get_payment_summary_for_musician,
    get_musician_payment_summary_for_event,
    get_event_billing_summary
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

    # Mock event with future dates to allow advance payments
    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = datetime(2023, 10, 2, 20, 0, 0, tzinfo=timezone.utc)  # Future start
    mock_event.end_datetime = datetime(2023, 10, 2, 23, 0, 0, tzinfo=timezone.utc)    # Future end
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

    # Freeze time to simulate current time before event start
    with freeze_time("2023-09-15 12:00:00"):
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

    assert "TOTAL payment must equal the full salary amount. Expected: 1000.00, Got: 1200.00" in str(exc_info.value)


def test_create_musician_payment_cumulative_exceeds_salary(mocker):
    """Test create_musician_payment() raises ValidationError when cumulative payments exceed salary"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("600.00"),  # This would make total advance = 600 > 500
        payment_type=PaymentType.ADVANCE,  # Test cumulative advance validation
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

    # Mock existing payments totaling 500.00
    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total.return_value = Decimal("500.00")

    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = []

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        create_musician_payment(payment_data, current_user)

    assert "Total ADVANCE payments cannot exceed 50% of salary" in str(exc_info.value)


def test_create_musician_payment_advance_exceeds_50_percent(mocker):
    """Test create_musician_payment() raises ValidationError when ADVANCE exceeds 50% of salary"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("600.00"),  # 60% of 1000.00 salary (50% limit = 500.00)
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

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1000.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Mock no existing payments
    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total.return_value = Decimal("0.00")

    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = []

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        create_musician_payment(payment_data, current_user)

    assert "Total ADVANCE payments cannot exceed 50% of salary. Maximum total advance: 500.000, Current total advance: 0, Requested amount: 600.00, Salary: 1000.00" in str(exc_info.value)


def test_create_musician_payment_total_with_existing_payments(mocker):
    """Test create_musician_payment() raises ValidationError when creating TOTAL payment with existing payments"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("1000.00"),
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

    # Mock existing payments (non-empty list)
    existing_payments = [
        MusicianEventPayment(id=1, event_id=1, musician_id=2, amount=Decimal("500.00"), payment_type=PaymentType.ADVANCE,
                           payment_date=datetime(2023, 9, 1, 12, 0, 0, tzinfo=timezone.utc))
    ]
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = existing_payments

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        create_musician_payment(payment_data, current_user)

    assert "Cannot create TOTAL payment when partial payments exist" in str(exc_info.value)


def test_create_musician_payment_advance_after_event_start(mocker):
    """Test create_musician_payment() raises ValidationError when ADVANCE payment is made after event start"""

    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("300.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    # Mock event that starts before current time
    event_start = datetime(2023, 10, 1, 10, 0, 0, tzinfo=timezone.utc)  # Event started 2 hours ago
    event_end = datetime(2023, 10, 1, 14, 0, 0, tzinfo=timezone.utc)
    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = event_start
    mock_event.end_datetime = event_end
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1000.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Mock no existing payments
    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total.return_value = Decimal("0.00")

    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = []

    # Freeze time to simulate current time (after event start)
    with freeze_time("2023-10-01 12:00:00"):
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            create_musician_payment(payment_data, current_user)

    assert "ADVANCE payments can only be made before event start date" in str(exc_info.value)


def test_create_musician_payment_advance_before_event_start(mocker):
    """Test create_musician_payment() allows ADVANCE payment before event start"""

    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("300.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    # Mock event that starts in the future
    event_start = datetime(2023, 10, 2, 20, 0, 0, tzinfo=timezone.utc)  # Event starts tomorrow
    event_end = datetime(2023, 10, 2, 23, 0, 0, tzinfo=timezone.utc)
    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = event_start
    mock_event.end_datetime = event_end
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1000.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Mock no existing payments
    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total.return_value = Decimal("0.00")

    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = []

    now = datetime.now(timezone.utc)
    mock_payment = MusicianEventPayment(
        id=1,
        event_id=1,
        musician_id=2,
        amount=Decimal("300.00"),
        payment_type=PaymentType.ADVANCE,
        payment_date=payment_data.payment_date,
        notes=None,
        created_at=now,
        updated_at=now
    )
    mock_payment_data_create = mocker.patch('services.musician_event_payment.payment_data.create')
    mock_payment_data_create.return_value = mock_payment

    mock_assignment_data_update = mocker.patch('services.musician_event_payment.assignment_data.update_payment_status')
    mock_assignment_data_update.return_value = True

    # Freeze time to simulate current time (before event start)
    with freeze_time("2023-10-01 12:00:00"):
        # Act
        result = create_musician_payment(payment_data, current_user)

    # Assert
    assert result.id == 1
    mock_payment_data_create.assert_called_once()


def test_create_musician_payment_remaining_before_event_end(mocker):
    """Test create_musician_payment() raises ValidationError when REMAINING payment is made before event end"""

    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("700.00"),
        payment_type=PaymentType.REMAINING,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    # Mock event that ends in the future
    event_start = datetime(2023, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    event_end = datetime(2023, 10, 2, 14, 0, 0, tzinfo=timezone.utc)  # Event ends tomorrow
    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = event_start
    mock_event.end_datetime = event_end
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1000.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Mock existing payments totaling 300.00
    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total.return_value = Decimal("300.00")

    mock_advance_payment = Mock()
    mock_advance_payment.amount = Decimal("200.00")
    mock_advance_payment.payment_type = PaymentType.ADVANCE
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = [mock_advance_payment]

    # Freeze time to simulate current time (before event end)
    with freeze_time("2023-10-01 12:00:00"):
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            create_musician_payment(payment_data, current_user)

    assert "REMAINING payments can only be made on or after event end date" in str(exc_info.value)


def test_create_musician_payment_remaining_after_event_end(mocker):
    """Test create_musician_payment() allows REMAINING payment after event end"""

    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("700.00"),
        payment_type=PaymentType.REMAINING,
        payment_date=datetime(2023, 10, 2, 16, 0, 0, tzinfo=timezone.utc)
    )

    # Mock event that ended in the past
    event_start = datetime(2023, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    event_end = datetime(2023, 10, 1, 14, 0, 0, tzinfo=timezone.utc)  # Event ended yesterday
    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = event_start
    mock_event.end_datetime = event_end
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1000.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Mock existing payments totaling 300.00
    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total.return_value = Decimal("300.00")

    mock_advance_payment = Mock()
    mock_advance_payment.amount = Decimal("200.00")
    mock_advance_payment.payment_type = PaymentType.ADVANCE
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = [mock_advance_payment]

    now = datetime.now(timezone.utc)
    mock_payment = MusicianEventPayment(
        id=1,
        event_id=1,
        musician_id=2,
        amount=Decimal("700.00"),
        payment_type=PaymentType.REMAINING,
        payment_date=payment_data.payment_date,
        notes=None,
        created_at=now,
        updated_at=now
    )
    mock_payment_data_create = mocker.patch('services.musician_event_payment.payment_data.create')
    mock_payment_data_create.return_value = mock_payment

    mock_assignment_data_update = mocker.patch('services.musician_event_payment.assignment_data.update_payment_status')
    mock_assignment_data_update.return_value = True

    # Freeze time to simulate current time (after event end)
    with freeze_time("2023-10-02 16:00:00"):
        # Act
        result = create_musician_payment(payment_data, current_user)

    # Assert
    assert result.id == 1
    mock_payment_data_create.assert_called_once()


def test_create_musician_payment_total_before_event_end(mocker):
    """Test create_musician_payment() raises ValidationError when TOTAL payment is made before event end"""

    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("1000.00"),
        payment_type=PaymentType.TOTAL,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    # Mock event that ends in the future
    event_start = datetime(2023, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    event_end = datetime(2023, 10, 2, 14, 0, 0, tzinfo=timezone.utc)  # Event ends tomorrow
    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = event_start
    mock_event.end_datetime = event_end
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1000.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Mock no existing payments for TOTAL payment
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = []

    # Freeze time to simulate current time (before event end)
    with freeze_time("2023-10-01 12:00:00"):
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            create_musician_payment(payment_data, current_user)

    assert "TOTAL payments can only be made on or after event end date" in str(exc_info.value)


def test_create_musician_payment_total_after_event_end(mocker):
    """Test create_musician_payment() allows TOTAL payment after event end"""

    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("1000.00"),
        payment_type=PaymentType.TOTAL,
        payment_date=datetime(2023, 10, 2, 16, 0, 0, tzinfo=timezone.utc)
    )

    # Mock event that ended in the past
    event_start = datetime(2023, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    event_end = datetime(2023, 10, 1, 14, 0, 0, tzinfo=timezone.utc)  # Event ended yesterday
    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = event_start
    mock_event.end_datetime = event_end
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1000.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Mock no existing payments for TOTAL payment
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = []

    now = datetime.now(timezone.utc)
    mock_payment = MusicianEventPayment(
        id=1,
        event_id=1,
        musician_id=2,
        amount=Decimal("1000.00"),
        payment_type=PaymentType.TOTAL,
        payment_date=payment_data.payment_date,
        notes=None,
        created_at=now,
        updated_at=now
    )
    mock_payment_data_create = mocker.patch('services.musician_event_payment.payment_data.create')
    mock_payment_data_create.return_value = mock_payment

    mock_assignment_data_update = mocker.patch('services.musician_event_payment.assignment_data.update_payment_status')
    mock_assignment_data_update.return_value = True

    # Freeze time to simulate current time (after event end)
    with freeze_time("2023-10-02 16:00:00"):
        # Act
        result = create_musician_payment(payment_data, current_user)

    # Assert
    assert result.id == 1
    mock_payment_data_create.assert_called_once()


def test_create_musician_payment_total_on_event_end_date(mocker):
    """Test create_musician_payment() allows TOTAL payment exactly on event end date"""

    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("1000.00"),
        payment_type=PaymentType.TOTAL,
        payment_date=datetime(2023, 10, 1, 14, 0, 0, tzinfo=timezone.utc)
    )

    # Mock event ending at exactly the same time
    event_start = datetime(2023, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    event_end = datetime(2023, 10, 1, 14, 0, 0, tzinfo=timezone.utc)  # Event ends at 14:00
    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = event_start
    mock_event.end_datetime = event_end
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("1000.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Mock no existing payments for TOTAL payment
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = []

    now = datetime.now(timezone.utc)
    mock_payment = MusicianEventPayment(
        id=1,
        event_id=1,
        musician_id=2,
        amount=Decimal("1000.00"),
        payment_type=PaymentType.TOTAL,
        payment_date=payment_data.payment_date,
        notes=None,
        created_at=now,
        updated_at=now
    )
    mock_payment_data_create = mocker.patch('services.musician_event_payment.payment_data.create')
    mock_payment_data_create.return_value = mock_payment

    mock_assignment_data_update = mocker.patch('services.musician_event_payment.assignment_data.update_payment_status')
    mock_assignment_data_update.return_value = True

    # Freeze time to simulate current time (exactly at event end)
    with freeze_time("2023-10-01 14:00:00"):
        # Act
        result = create_musician_payment(payment_data, current_user)

    # Assert
    assert result.id == 1
    mock_payment_data_create.assert_called_once()


def test_create_musician_payment_updates_payment_status_completed(mocker):
    """Test create_musician_payment() updates payment status to COMPLETED when fully paid"""
    # Arrange
    current_user = {'id': 1, 'role': 'admin'}
    payment_data = MusicianEventPaymentCreate(
        event_id=1,
        musician_id=2,
        amount=Decimal("500.00"),  # Total will be 800.00, which equals salary
        payment_type=PaymentType.REMAINING,
        payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    # Mock event with past dates to allow final payments
    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.start_datetime = datetime(2023, 10, 1, 10, 0, 0, tzinfo=timezone.utc)  # Past start
    mock_event.end_datetime = datetime(2023, 10, 1, 14, 0, 0, tzinfo=timezone.utc)    # Past end
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_musician = Mock()
    mock_musician.id = 2
    mock_user_data_get = mocker.patch('services.musician_event_payment.user_data.get_one_by_id')
    mock_user_data_get.return_value = mock_musician

    mock_assignment = EventMusician(id=1, event_id=1, musician_id=2, role="Lead Guitarist", salary=Decimal("800.00"), payment_status="PENDING")
    mock_assignment_data_get = mocker.patch('services.musician_event_payment.assignment_data.get_by_event_and_musician')
    mock_assignment_data_get.return_value = mock_assignment

    # Mock existing payments totaling 300.00, new payment 500.00 = 800.00 total
    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total.return_value = Decimal("300.00")

    mock_advance_payment = Mock()
    mock_advance_payment.amount = Decimal("200.00")
    mock_advance_payment.payment_type = PaymentType.ADVANCE
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = [mock_advance_payment]

    now = datetime.now(timezone.utc)
    mock_payment = MusicianEventPayment(
        id=1,
        event_id=1,
        musician_id=2,
        amount=Decimal("500.00"),
        payment_type=PaymentType.REMAINING,
        payment_date=payment_data.payment_date,
        notes=None,
        created_at=now,
        updated_at=now
    )
    mock_payment_data_create = mocker.patch('services.musician_event_payment.payment_data.create')
    mock_payment_data_create.return_value = mock_payment

    mock_assignment_data_update = mocker.patch('services.musician_event_payment.assignment_data.update_payment_status')
    mock_assignment_data_update.return_value = True

    # Act
    result = create_musician_payment(payment_data, current_user)

    # Assert
    assert result.id == 1
    mock_assignment_data_update.assert_called_once_with(1, 2, "COMPLETED")


def test_get_payments_for_event_admin_success(mocker):
    """Test get_payments_for_event() returns payments for admin"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {'id': 1, 'role': 'admin'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    now = datetime.now(timezone.utc)
    mock_payments = [
        MusicianEventPayment(id=1, event_id=1, musician_id=2, amount=Decimal("500.00"), payment_type=PaymentType.ADVANCE, payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc), created_at=now, updated_at=now)
    ]
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = mock_payments

    # Act
    result = get_payments_for_event(event_id, musician_id, current_user)

    # Assert
    assert len(result) == 1
    mock_event_data_get.assert_called_once_with(event_id)
    mock_payment_data_get.assert_called_once_with(event_id, musician_id)


def test_get_payments_for_event_musician_success(mocker):
    """Test get_payments_for_event() returns payments for performer (helper) viewing own payments"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {'id': 2, 'role': 'helper'}  # helper treated same as musician/auxiliar_musician for own payments

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    now = datetime.now(timezone.utc)
    mock_payments = [
        MusicianEventPayment(id=1, event_id=1, musician_id=2, amount=Decimal("500.00"), payment_type=PaymentType.ADVANCE, payment_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc), created_at=now, updated_at=now)
    ]
    mock_payment_data_get = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_get.return_value = mock_payments

    # Act
    result = get_payments_for_event(event_id, musician_id, current_user)

    # Assert
    assert len(result) == 1
    mock_payment_data_get.assert_called_once_with(event_id, musician_id)


def test_get_payments_for_event_musician_unauthorized(mocker):
    """Test get_payments_for_event() raises UnauthorizedError for musician viewing others' payments"""
    # Arrange
    event_id = 1
    musician_id = 3  # Different musician
    current_user = {'id': 2, 'role': 'musician'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_payments_for_event(event_id, musician_id, current_user)

    assert "You can only view your own payment information" in str(exc_info.value)


def test_get_payments_for_event_user_unauthorized(mocker):
    """Test get_payments_for_event() raises UnauthorizedError for regular users"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {'id': 1, 'role': 'user'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_payments_for_event(event_id, musician_id, current_user)

    assert "Unauthorized to view musician payments" in str(exc_info.value)


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


def test_get_payment_summary_for_musician_event_admin_success(mocker):
    """Test get_payment_summary_for_musician_event() returns summary for admin"""
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

    mock_payment_data_count = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_count.return_value = [Mock(), Mock()]  # 2 payments

    # Act
    result = get_payment_summary_for_musician_event(event_id, musician_id, current_user)

    # Assert
    assert result.musician_id == 2
    assert result.total_paid == Decimal("800.00")
    assert result.payment_count == 2
    mock_payment_data_total.assert_called_once_with(event_id, musician_id)


def test_get_payment_summary_for_musician_event_musician_success(mocker):
    """Test get_payment_summary_for_musician_event() returns summary for performer (helper) viewing own payments"""
    # Arrange
    event_id = 1
    musician_id = 2
    current_user = {'id': 2, 'role': 'helper'}  # helper treated same as musician/auxiliar_musician for own payments

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    mock_payment_data_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total.return_value = Decimal("800.00")

    mock_payment_data_count = mocker.patch('services.musician_event_payment.payment_data.get_payments_by_event_and_musician')
    mock_payment_data_count.return_value = [Mock()]  # 1 payment

    # Act
    result = get_payment_summary_for_musician_event(event_id, musician_id, current_user)

    # Assert
    assert result.musician_id == 2
    assert result.total_paid == Decimal("800.00")
    assert result.payment_count == 1


def test_get_payment_summary_for_musician_event_musician_unauthorized(mocker):
    """Test get_payment_summary_for_musician_event() raises UnauthorizedError for musician viewing others' payments"""
    # Arrange
    event_id = 1
    musician_id = 3  # Different musician
    current_user = {'id': 2, 'role': 'musician'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_payment_summary_for_musician_event(event_id, musician_id, current_user)

    assert "You can only view your own payment information" in str(exc_info.value)


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


def test_get_musician_payment_summary_for_event_admin_success(mocker):
    """Test get_musician_payment_summary_for_event() returns summary for admin"""
    # Arrange
    event_id = 1
    current_user = {'id': 1, 'role': 'admin'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Mock musician assignments
    mock_musician1 = Mock()
    mock_musician1.id = 2
    mock_musician1.name = "John"
    mock_musician1.lastname = "Doe"
    mock_musician1.second_lastname = None

    mock_musician2 = Mock()
    mock_musician2.id = 3
    mock_musician2.name = "Jane"
    mock_musician2.lastname = "Smith"
    mock_musician2.second_lastname = "Jr"

    mock_assignment1 = Mock()
    mock_assignment1.id = 1
    mock_assignment1.event_id = 1
    mock_assignment1.musician_id = 2
    mock_assignment1.role = "Lead Guitarist"
    mock_assignment1.salary = Decimal("1000.00")
    mock_assignment1.payment_status = "PENDING"
    mock_assignment1.musician = mock_musician1

    mock_assignment2 = Mock()
    mock_assignment2.id = 2
    mock_assignment2.event_id = 1
    mock_assignment2.musician_id = 3
    mock_assignment2.role = "Vocalist"
    mock_assignment2.salary = Decimal("800.00")
    mock_assignment2.payment_status = "PARTIAL"
    mock_assignment2.musician = mock_musician2

    mock_assignments = [mock_assignment1, mock_assignment2]
    mock_assignment_data_get_by_event = mocker.patch('services.musician_event_payment.assignment_data.get_by_event')
    mock_assignment_data_get_by_event.return_value = mock_assignments

    # Mock payment totals for each musician
    mock_payment_data_total_1 = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_musician_for_event')
    mock_payment_data_total_1.side_effect = [Decimal("300.00"), Decimal("500.00")]  # For musician 2 and 3 respectively

    # Act
    result = get_musician_payment_summary_for_event(event_id, current_user)

    # Assert
    assert len(result) == 2
    # First musician
    assert result[0].musician_name == "John Doe"
    assert result[0].role == "Lead Guitarist"
    assert result[0].salary == Decimal("1000.00")
    assert result[0].payment_done == Decimal("300.00")
    assert result[0].remaining_payment == Decimal("700.00")
    # Second musician
    assert result[1].musician_name == "Jane Smith Jr"
    assert result[1].role == "Vocalist"
    assert result[1].salary == Decimal("800.00")
    assert result[1].payment_done == Decimal("500.00")
    assert result[1].remaining_payment == Decimal("300.00")
    
    mock_event_data_get.assert_called_once_with(event_id)
    mock_assignment_data_get_by_event.assert_called_once_with(event_id)
    assert mock_payment_data_total_1.call_count == 2


def test_get_musician_payment_summary_for_event_unauthorized(mocker):
    """Test get_musician_payment_summary_for_event() raises UnauthorizedError for non-admin"""
    # Arrange
    event_id = 1
    current_user = {'id': 1, 'role': 'user'}  # Not admin

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_musician_payment_summary_for_event(event_id, current_user)

    assert "You can only view payment summaries for your own events" in str(exc_info.value)


def test_get_musician_payment_summary_for_event_event_not_found(mocker):
    """Test get_musician_payment_summary_for_event() raises NotFoundError when event doesn't exist"""
    # Arrange
    event_id = 999
    current_user = {'id': 1, 'role': 'admin'}

    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        get_musician_payment_summary_for_event(event_id, current_user)

    assert "Event with id 999 not found" in str(exc_info.value)


def test_get_event_billing_summary_admin_success(mocker):
    """Test get_event_billing_summary() returns billing summary for admin"""
    # Arrange
    event_id = 1
    current_user = {'id': 1, 'role': 'admin'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.name = "Summer Festival"
    mock_event.price = Decimal("4000.00")  # Event final price
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Mock total paid for the event (event payments)
    mock_event_payment_total = mocker.patch('services.musician_event_payment.event_payment_data.get_total_paid')
    mock_event_payment_total.return_value = Decimal("4000.00")

    # Mock total paid to musicians
    mock_musician_payment_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_event_for_musicians')
    mock_musician_payment_total.return_value = Decimal("350.00")

    # Mock sum of musician salaries
    mock_assignment1 = Mock()
    mock_assignment1.salary = Decimal("500.00")
    mock_assignment2 = Mock()
    mock_assignment2.salary = Decimal("550.00")
    mock_assignments = [mock_assignment1, mock_assignment2]
    mock_assignment_data_get_by_event = mocker.patch('services.musician_event_payment.assignment_data.get_by_event')
    mock_assignment_data_get_by_event.return_value = mock_assignments

    # Act
    result = get_event_billing_summary(event_id, current_user)

    # Assert
    assert result.event_name == "Summer Festival"
    assert result.event_price == Decimal("4000.00")
    assert result.payment_done == Decimal("4000.00")
    assert result.sum_of_musician_salaries == Decimal("1050.00")
    assert result.remaining_payment == Decimal("0.00")
    assert result.payment_done_to_musicians == Decimal("350.00")

    mock_event_data_get.assert_called_once_with(event_id)
    mock_event_payment_total.assert_called_once_with(event_id)
    mock_musician_payment_total.assert_called_once_with(event_id)
    mock_assignment_data_get_by_event.assert_called_once_with(event_id)


def test_get_event_billing_summary_owner_success(mocker):
    """Test get_event_billing_summary() returns billing summary for event owner"""
    # Arrange
    event_id = 1
    current_user = {'id': 1, 'role': 'user'}  # User is the event owner

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1  # Same as current_user.id
    mock_event.name = "Winter Concert"
    mock_event.price = Decimal("2500.00")
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Mock total paid for the event (event payments)
    mock_event_payment_total = mocker.patch('services.musician_event_payment.event_payment_data.get_total_paid')
    mock_event_payment_total.return_value = Decimal("2500.00")

    # Mock total paid to musicians
    mock_musician_payment_total = mocker.patch('services.musician_event_payment.payment_data.get_total_paid_by_event_for_musicians')
    mock_musician_payment_total.return_value = Decimal("1500.00")

    # Mock sum of musician salaries
    mock_assignment1 = Mock()
    mock_assignment1.salary = Decimal("800.00")
    mock_assignment2 = Mock()
    mock_assignment2.salary = Decimal("700.00")
    mock_assignments = [mock_assignment1, mock_assignment2]
    mock_assignment_data_get_by_event = mocker.patch('services.musician_event_payment.assignment_data.get_by_event')
    mock_assignment_data_get_by_event.return_value = mock_assignments

    # Act
    result = get_event_billing_summary(event_id, current_user)

    # Assert
    assert result.event_name == "Winter Concert"
    assert result.event_price == Decimal("2500.00")
    assert result.payment_done == Decimal("2500.00")
    assert result.sum_of_musician_salaries == Decimal("1500.00")
    assert result.remaining_payment == Decimal("0.00")
    assert result.payment_done_to_musicians == Decimal("1500.00")

    mock_event_data_get.assert_called_once_with(event_id)
    mock_event_payment_total.assert_called_once_with(event_id)
    mock_musician_payment_total.assert_called_once_with(event_id)
    mock_assignment_data_get_by_event.assert_called_once_with(event_id)


def test_get_event_billing_summary_unauthorized(mocker):
    """Test get_event_billing_summary() raises UnauthorizedError for non-owner, non-admin"""
    # Arrange
    event_id = 1
    current_user = {'id': 2, 'role': 'user'}  # Not admin, not event owner

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1  # Different from current_user.id
    mock_event.name = "Summer Festival"
    mock_event.price = Decimal("5000.00")
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Act & Assert
    with pytest.raises(UnauthorizedError) as exc_info:
        get_event_billing_summary(event_id, current_user)

    assert "You can only view billing summaries for your own events" in str(exc_info.value)


def test_get_event_billing_summary_event_not_found(mocker):
    """Test get_event_billing_summary() raises NotFoundError when event doesn't exist"""
    # Arrange
    event_id = 999
    current_user = {'id': 1, 'role': 'admin'}

    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        get_event_billing_summary(event_id, current_user)

    assert "Event with id 999 not found" in str(exc_info.value)


def test_get_event_billing_summary_price_not_set(mocker):
    """Test get_event_billing_summary() raises ValidationError when event price is not set"""
    # Arrange
    event_id = 1
    current_user = {'id': 1, 'role': 'admin'}

    mock_event = Mock()
    mock_event.id = 1
    mock_event.user_id = 1
    mock_event.name = "Event Without Price"
    mock_event.price = None  # Price not set
    mock_event_data_get = mocker.patch('services.musician_event_payment.event_data.get_one')
    mock_event_data_get.return_value = mock_event

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        get_event_billing_summary(event_id, current_user)

    assert "Event final price not set" in str(exc_info.value)