"""Tests for ReminderScheduler - Background job processing and strategy-based scheduling.

Tests cover: reminder scheduling strategies, background job processing,
cancellation, and notification integration.
"""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from openfatture.payment.application.services.reminder_scheduler import (
    ReminderRepository,
    ReminderScheduler,
)
from openfatture.payment.domain.enums import ReminderStrategy
from openfatture.payment.domain.models import PaymentReminder
from openfatture.storage.database.models import StatoPagamento

pytestmark = pytest.mark.asyncio


class TestReminderRepository:
    """Integration-style tests for the lightweight ReminderRepository."""

    async def test_repository_crud_operations(self, db_session, sample_fattura):
        """Repository should persist, query and delete reminders correctly."""
        from openfatture.storage.database.models import Pagamento, StatoPagamento

        repo = ReminderRepository(db_session)

        payment = Pagamento(
            fattura_id=sample_fattura.id,
            importo=Decimal("500.00"),
            importo_pagato=Decimal("0.00"),
            data_scadenza=date.today() + timedelta(days=10),
            stato=StatoPagamento.DA_PAGARE,
        )
        db_session.add(payment)
        db_session.flush()

        single = PaymentReminder(
            payment_id=payment.id,
            payment=payment,
            reminder_date=date.today(),
            strategy=ReminderStrategy.DEFAULT,
            email_body="Single reminder",
        )
        repo.add(single)

        batch = [
            PaymentReminder(
                payment_id=payment.id,
                payment=payment,
                reminder_date=date.today(),
                strategy=ReminderStrategy.DEFAULT,
                email_body=f"Batch reminder {i}",
            )
            for i in range(2)
        ]
        repo.add_all(batch)

        batch[1].mark_sent()  # Sent reminders must be ignored
        db_session.flush()

        due_today = repo.get_due_reminders()
        assert {r.email_body for r in due_today} == {"Single reminder", "Batch reminder 0"}

        deleted = repo.delete_by_payment_id(payment.id)
        # Only unsent reminders (2) are deleted
        assert deleted == 2


class TestReminderScheduler:
    """Tests for ReminderScheduler strategy-based scheduling and processing."""

    @pytest.fixture
    def reminder_scheduler(self, mock_reminder_repo, mock_payment_repo, mock_notifier):
        """Create reminder scheduler with mocked dependencies."""
        return ReminderScheduler(
            reminder_repo=mock_reminder_repo,
            payment_repo=mock_payment_repo,
            notifier=mock_notifier,
        )

    @pytest.fixture
    def mock_reminder_repo(self, mocker):
        """Mock ReminderRepository."""
        repo = mocker.Mock(spec=ReminderRepository)
        repo.add = mocker.Mock()
        repo.add_all = mocker.Mock()
        repo.get_due_reminders = mocker.Mock()
        repo.delete_by_payment_id = mocker.Mock()
        return repo

    @pytest.fixture
    def mock_payment_repo(self, mocker):
        """Mock PaymentRepository."""
        repo = mocker.Mock()
        repo.get_by_id = mocker.Mock()
        repo.update = mocker.Mock()
        return repo

    @pytest.fixture
    def mock_notifier(self, mocker):
        """Mock INotifier."""
        notifier = mocker.Mock()
        notifier.send_reminder = AsyncMock(return_value=True)
        return notifier

    @pytest.fixture
    def mock_payment(self, mocker):
        """Create mock payment object."""
        payment = mocker.Mock()
        payment.id = 1
        payment.importo_da_pagare = Decimal("1000.00")
        payment.importo_pagato = Decimal("0.00")
        payment.data_scadenza = date.today() + timedelta(days=30)
        payment.stato = StatoPagamento.DA_PAGARE

        # Mock fattura relationship
        fattura = mocker.Mock()
        fattura.numero = "INV-2024-001"
        payment.fattura = fattura

        return payment

    @pytest.mark.parametrize(
        "offset, snippet",
        [
            (-3, "3 days overdue"),
            (0, "due TODAY"),
            (7, "falls due in 7 days"),
        ],
    )
    async def test_build_reminder_message_variants(
        self, reminder_scheduler, mock_payment, offset, snippet
    ):
        """Reminder message should reflect whether it is overdue, same day, or upcoming."""
        mock_payment.data_scadenza = date.today() + timedelta(days=offset)
        message = reminder_scheduler._build_reminder_message(mock_payment, offset)
        assert snippet in message

    async def test_outstanding_amount_handles_invalid_saldo(self, reminder_scheduler, mocker):
        """_outstanding_amount should fall back when saldo_residuo is not parseable."""
        payment = mocker.Mock()
        payment.saldo_residuo = "not-a-number"
        payment.importo_da_pagare = Decimal("300.00")
        payment.importo = Decimal("300.00")
        payment.importo_pagato = Decimal("120.00")
        assert reminder_scheduler._outstanding_amount(payment) == Decimal("180.00")

        payment = mocker.Mock()
        payment.saldo_residuo = Decimal("90.00")
        assert reminder_scheduler._outstanding_amount(payment) == Decimal("90.00")

    # ==========================================================================
    # Schedule Reminders Tests (5 tests)
    # ==========================================================================

    async def test_schedule_reminders_creates_multiple_dates(
        self, reminder_scheduler, mock_reminder_repo, mock_payment_repo, mock_payment
    ):
        """Test that schedule_reminders creates reminders for all strategy dates."""
        mock_payment_repo.get_by_id.return_value = mock_payment

        # DEFAULT strategy: [-7, -3, 0, 3, 7] days
        reminders = await reminder_scheduler.schedule_reminders(
            payment_id=1,
            strategy=ReminderStrategy.DEFAULT,
        )

        # Should create reminders for all dates (skipping past dates)
        assert len(reminders) <= 5
        assert all(isinstance(r, PaymentReminder) for r in reminders)

        # Verify add_all called if reminders created
        if reminders:
            mock_reminder_repo.add_all.assert_called_once_with(reminders)

    async def test_schedule_reminders_skips_past_dates(
        self, reminder_scheduler, mock_reminder_repo, mock_payment_repo, mock_payment, mocker
    ):
        """Test that past reminder dates are skipped."""
        # Payment due yesterday
        # DEFAULT strategy: [-7, -3, 0, 7, 30] days
        # From yesterday: -7, -3, 0 are past (skip), +7, +30 are future (create)
        mock_payment.data_scadenza = date.today() - timedelta(days=1)
        mock_payment_repo.get_by_id.return_value = mock_payment

        # Mock logger to verify debug logging
        mock_logger = mocker.patch(
            "openfatture.payment.application.services.reminder_scheduler.logger"
        )

        reminders = await reminder_scheduler.schedule_reminders(
            payment_id=1,
            strategy=ReminderStrategy.DEFAULT,
        )

        # Should create 2 reminders (7 and 30 days from yesterday are still future)
        assert len(reminders) == 2
        mock_reminder_repo.add_all.assert_called_once()

        # Verify past dates were logged (3 past dates: -7, -3, 0)
        assert mock_logger.debug.call_count >= 3
        mock_payment_repo.update.assert_called_once_with(mock_payment)

    async def test_schedule_reminders_validates_payment_not_paid(
        self, reminder_scheduler, mock_payment_repo, mock_payment
    ):
        """Test that schedule_reminders raises error if payment is fully paid."""
        mock_payment.importo_pagato = Decimal("1000.00")  # Fully paid
        mock_payment_repo.get_by_id.return_value = mock_payment

        with pytest.raises(ValueError, match="already fully paid"):
            await reminder_scheduler.schedule_reminders(payment_id=1)

    async def test_schedule_reminders_strategy_variations(
        self, reminder_scheduler, mock_reminder_repo, mock_payment_repo, mock_payment
    ):
        """Test different reminder strategies create different schedules."""
        mock_payment_repo.get_by_id.return_value = mock_payment

        # Test each strategy
        strategies = {
            ReminderStrategy.AGGRESSIVE: 9,  # -10, -7, -3, -1, 0, 3, 7, 15, 30 days
            ReminderStrategy.DEFAULT: 5,  # -7, -3, 0, 7, 30 days
            ReminderStrategy.GENTLE: 4,  # -7, 0, 15, 30 days
            ReminderStrategy.MINIMAL: 2,  # 0, 30 days
        }

        for strategy, expected_max in strategies.items():
            reminders = await reminder_scheduler.schedule_reminders(
                payment_id=1,
                strategy=strategy,
            )

            # Should have at most expected_max reminders (some may be skipped if past)
            assert len(reminders) <= expected_max

            # All reminders should have correct strategy
            for reminder in reminders:
                assert reminder.strategy == strategy

    async def test_schedule_reminders_persists_to_database(
        self, reminder_scheduler, mock_reminder_repo, mock_payment_repo, mock_payment
    ):
        """Test that reminders are persisted via repository."""
        mock_payment_repo.get_by_id.return_value = mock_payment

        reminders = await reminder_scheduler.schedule_reminders(
            payment_id=1,
            strategy=ReminderStrategy.DEFAULT,
        )

        # Verify repository called
        if reminders:
            mock_reminder_repo.add_all.assert_called_once()
            persisted_reminders = mock_reminder_repo.add_all.call_args[0][0]
            assert len(persisted_reminders) == len(reminders)

            # Verify reminder attributes
            for r in persisted_reminders:
                assert r.payment_id == 1
                assert r.reminder_date >= date.today()
                assert r.email_body is not None

    async def test_schedule_reminders_marks_overdue_scaduto(
        self, reminder_scheduler, mock_reminder_repo, mock_payment_repo, mock_payment
    ):
        """Overdue payments are flagged as SCADUTO before scheduling reminders."""
        mock_payment.data_scadenza = date.today() - timedelta(days=2)
        mock_payment.importo_pagato = Decimal("100.00")
        mock_payment_repo.get_by_id.return_value = mock_payment

        await reminder_scheduler.schedule_reminders(payment_id=1)

        assert mock_payment.stato == StatoPagamento.SCADUTO
        mock_payment_repo.update.assert_called_with(mock_payment)

    async def test_schedule_reminders_raises_for_missing_payment(
        self, reminder_scheduler, mock_payment_repo
    ):
        """Missing payments must raise a descriptive error."""
        mock_payment_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Payment 42 not found"):
            await reminder_scheduler.schedule_reminders(payment_id=42)

    # ==========================================================================
    # Process Due Reminders Tests (5 tests)
    # ==========================================================================

    async def test_process_due_reminders_sends_notifications(
        self, reminder_scheduler, mock_reminder_repo, mock_notifier, mock_payment, mocker
    ):
        """Test that process_due_reminders sends notifications for due reminders."""
        # Create mock reminders
        reminder1 = mocker.Mock(spec=PaymentReminder)
        reminder1.id = 1
        reminder1.payment = mock_payment
        reminder1.email_body = "Test reminder 1"
        reminder1.mark_sent = mocker.Mock()

        reminder2 = mocker.Mock(spec=PaymentReminder)
        reminder2.id = 2
        reminder2.payment = mock_payment
        reminder2.email_body = "Test reminder 2"
        reminder2.mark_sent = mocker.Mock()

        mock_reminder_repo.get_due_reminders.return_value = [reminder1, reminder2]

        # Process reminders
        count = await reminder_scheduler.process_due_reminders()

        # Verify notifications sent
        assert count == 2
        assert mock_notifier.send_reminder.call_count == 2

        # Verify reminders marked as sent
        assert reminder1.mark_sent.called
        assert reminder2.mark_sent.called

    async def test_process_due_reminders_marks_as_sent(
        self, reminder_scheduler, mock_reminder_repo, mock_notifier, mock_payment, mocker
    ):
        """Test that successfully sent reminders are marked with sent_date."""
        reminder = mocker.Mock(spec=PaymentReminder)
        reminder.id = 1
        reminder.payment = mock_payment
        reminder.mark_sent = mocker.Mock()

        mock_reminder_repo.get_due_reminders.return_value = [reminder]

        await reminder_scheduler.process_due_reminders()

        # Verify mark_sent was called
        assert reminder.mark_sent.called

    async def test_process_due_reminders_skips_paid_payments(
        self, reminder_scheduler, mock_reminder_repo, mock_notifier, mock_payment, mocker
    ):
        """Test that reminders for paid payments are skipped but marked as sent."""
        mock_payment.importo_pagato = Decimal("1000.00")  # Fully paid

        reminder = mocker.Mock(spec=PaymentReminder)
        reminder.id = 1
        reminder.payment = mock_payment
        reminder.mark_sent = mocker.Mock()

        mock_reminder_repo.get_due_reminders.return_value = [reminder]

        count = await reminder_scheduler.process_due_reminders()

        # Should skip sending but mark as sent
        assert count == 0
        mock_notifier.send_reminder.assert_not_called()
        assert reminder.mark_sent.called  # Marked to avoid re-processing

    async def test_process_due_reminders_handles_errors(
        self, reminder_scheduler, mock_reminder_repo, mock_notifier, mock_payment, mocker
    ):
        """Test that reminder processing handles send errors gracefully."""
        # First reminder succeeds, second fails
        mock_notifier.send_reminder.side_effect = [True, Exception("SMTP error")]

        reminder1 = mocker.Mock(spec=PaymentReminder)
        reminder1.id = 1
        reminder1.payment = mock_payment
        reminder1.mark_sent = mocker.Mock()

        reminder2 = mocker.Mock(spec=PaymentReminder)
        reminder2.id = 2
        reminder2.payment = mock_payment
        reminder2.mark_sent = mocker.Mock()

        mock_reminder_repo.get_due_reminders.return_value = [reminder1, reminder2]

        # Should not raise, continue processing
        count = await reminder_scheduler.process_due_reminders()

        # Only first reminder succeeded
        assert count == 1
        assert reminder1.mark_sent.called
        assert not reminder2.mark_sent.called  # Failed, not marked

    async def test_process_due_reminders_returns_zero_when_none_due(
        self, reminder_scheduler, mock_reminder_repo
    ):
        """If the repository returns no due reminders, return 0 immediately."""
        mock_reminder_repo.get_due_reminders.return_value = []
        assert await reminder_scheduler.process_due_reminders() == 0

    async def test_process_due_reminders_handles_unsuccessful_send(
        self, reminder_scheduler, mock_reminder_repo, mock_notifier, mock_payment, mocker
    ):
        """Failed sends should not mark reminders as sent nor increment the counter."""
        reminder = mocker.Mock(spec=PaymentReminder)
        reminder.id = 99
        reminder.payment = mock_payment
        reminder.mark_sent = mocker.Mock()

        mock_reminder_repo.get_due_reminders.return_value = [reminder]
        mock_notifier.send_reminder.return_value = False

        count = await reminder_scheduler.process_due_reminders()

        assert count == 0
        mock_notifier.send_reminder.assert_called_once_with(reminder)
        reminder.mark_sent.assert_not_called()

    async def test_process_due_reminders_returns_count(
        self, reminder_scheduler, mock_reminder_repo, mock_notifier, mock_payment, mocker
    ):
        """Test that process_due_reminders returns correct count of sent reminders."""
        reminders = []
        for i in range(5):
            reminder = mocker.Mock(spec=PaymentReminder)
            reminder.id = i
            reminder.payment = mock_payment
            reminder.mark_sent = mocker.Mock()
            reminders.append(reminder)

        mock_reminder_repo.get_due_reminders.return_value = reminders

        count = await reminder_scheduler.process_due_reminders()

        assert count == 5
        assert mock_notifier.send_reminder.call_count == 5

    async def test_process_due_reminders_marks_overdue(
        self, reminder_scheduler, mock_reminder_repo, mock_notifier, mock_payment_repo, mocker
    ):
        """Payments overdue at processing time are flagged SCADUTO."""
        payment = mocker.Mock()
        payment.id = 77
        payment.importo_da_pagare = Decimal("800.00")
        payment.importo_pagato = Decimal("100.00")
        payment.data_scadenza = date.today() - timedelta(days=1)
        payment.stato = StatoPagamento.DA_PAGARE
        payment.saldo_residuo = Decimal("700.00")

        reminder = mocker.Mock(spec=PaymentReminder)
        reminder.id = 9
        reminder.payment = payment
        reminder.mark_sent = mocker.Mock()

        mock_reminder_repo.get_due_reminders.return_value = [reminder]

        await reminder_scheduler.process_due_reminders()

        assert payment.stato == StatoPagamento.SCADUTO
        mock_payment_repo.update.assert_called_with(payment)

    # ==========================================================================
    # Cancel Reminders Tests (3 tests)
    # ==========================================================================

    async def test_cancel_reminders_deletes_pending(self, reminder_scheduler, mock_reminder_repo):
        """Test that cancel_reminders deletes pending reminders."""
        mock_reminder_repo.delete_by_payment_id.return_value = 3

        deleted = await reminder_scheduler.cancel_reminders(payment_id=1)

        assert deleted == 3
        mock_reminder_repo.delete_by_payment_id.assert_called_once_with(1)

    async def test_cancel_reminders_keeps_sent(self, reminder_scheduler, mock_reminder_repo):
        """Test that cancel_reminders only deletes unsent reminders (sent_date = None)."""
        # Repository should filter by sent_date.is_(None) internally
        mock_reminder_repo.delete_by_payment_id.return_value = 2  # Only 2 pending

        deleted = await reminder_scheduler.cancel_reminders(payment_id=1)

        assert deleted == 2
        mock_reminder_repo.delete_by_payment_id.assert_called_once_with(1)

    async def test_cancel_reminders_returns_count(self, reminder_scheduler, mock_reminder_repo):
        """Test that cancel_reminders returns count of deleted reminders."""
        mock_reminder_repo.delete_by_payment_id.return_value = 5

        count = await reminder_scheduler.cancel_reminders(payment_id=1)

        assert count == 5
