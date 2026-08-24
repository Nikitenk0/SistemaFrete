import unittest
from datetime import (
    datetime,
    timedelta,
    timezone
)

from domain.freight_lifecycle import (
    validate_freight_transition
)
from domain.models.freight import (
    Freight,
    FreightStatus
)
from domain.models.freight_event import (
    FreightEvent,
    FreightEventType
)


class FreightLifecycleTests(unittest.TestCase):

    def test_new_freight_defaults_to_pending(
        self
    ) -> None:
        freight = Freight(
            customer_id=1,
            primary_quote_id=10
        )

        self.assertEqual(
            freight.current_status,
            FreightStatus.PENDING
        )
        self.assertIsNone(freight.started_at)
        self.assertIsNone(freight.completed_at)
        self.assertIsNone(freight.cancelled_at)

    def test_accepts_valid_lifecycle_dates(
        self
    ) -> None:
        started_at = datetime.now(timezone.utc)
        completed_at = started_at + timedelta(hours=2)

        freight = Freight(
            customer_id=1,
            primary_quote_id=10,
            current_status=FreightStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at
        )

        self.assertEqual(
            freight.current_status,
            FreightStatus.COMPLETED
        )

    def test_rejects_inconsistent_lifecycle_dates(
        self
    ) -> None:
        now = datetime.now(timezone.utc)

        with self.assertRaises(ValueError):
            Freight(
                customer_id=1,
                primary_quote_id=10,
                current_status=FreightStatus.IN_PROGRESS
            )

        with self.assertRaises(ValueError):
            Freight(
                customer_id=1,
                primary_quote_id=10,
                current_status=FreightStatus.CANCELLED
            )

        with self.assertRaises(ValueError):
            Freight(
                customer_id=1,
                primary_quote_id=10,
                current_status=FreightStatus.COMPLETED,
                started_at=now,
                completed_at=(
                    now - timedelta(minutes=1)
                )
            )

    def test_allows_expected_transitions(
        self
    ) -> None:
        valid_transitions = (
            (
                FreightStatus.PENDING,
                FreightStatus.IN_PROGRESS
            ),
            (
                FreightStatus.PENDING,
                FreightStatus.CANCELLED
            ),
            (
                FreightStatus.IN_PROGRESS,
                FreightStatus.COMPLETED
            ),
            (
                FreightStatus.IN_PROGRESS,
                FreightStatus.CANCELLED
            )
        )

        for current_status, target_status in valid_transitions:
            validate_freight_transition(
                current_status,
                target_status
            )

    def test_rejects_invalid_and_terminal_transitions(
        self
    ) -> None:
        invalid_transitions = (
            (
                FreightStatus.PENDING,
                FreightStatus.COMPLETED
            ),
            (
                FreightStatus.IN_PROGRESS,
                FreightStatus.PENDING
            ),
            (
                FreightStatus.COMPLETED,
                FreightStatus.PENDING
            ),
            (
                FreightStatus.CANCELLED,
                FreightStatus.IN_PROGRESS
            )
        )

        for current_status, target_status in invalid_transitions:
            with self.assertRaises(ValueError):
                validate_freight_transition(
                    current_status,
                    target_status
                )


class FreightEventTests(unittest.TestCase):

    def test_created_event_represents_initial_state(
        self
    ) -> None:
        event = FreightEvent(
            event_type=FreightEventType.CREATED,
            new_status=FreightStatus.PENDING
        )

        self.assertIsNone(event.previous_status)
        self.assertEqual(
            event.new_status,
            FreightStatus.PENDING
        )

    def test_accepts_operational_events(
        self
    ) -> None:
        FreightEvent(
            event_type=FreightEventType.STARTED,
            previous_status=FreightStatus.PENDING,
            new_status=FreightStatus.IN_PROGRESS
        )
        FreightEvent(
            event_type=FreightEventType.COMPLETED,
            previous_status=FreightStatus.IN_PROGRESS,
            new_status=FreightStatus.COMPLETED
        )
        FreightEvent(
            event_type=FreightEventType.CANCELLED,
            previous_status=FreightStatus.IN_PROGRESS,
            new_status=FreightStatus.CANCELLED
        )

    def test_rejects_event_with_incompatible_transition(
        self
    ) -> None:
        with self.assertRaises(ValueError):
            FreightEvent(
                event_type=FreightEventType.STARTED,
                previous_status=FreightStatus.PENDING,
                new_status=FreightStatus.COMPLETED
            )

        with self.assertRaises(ValueError):
            FreightEvent(
                event_type=FreightEventType.CANCELLED,
                previous_status=FreightStatus.COMPLETED,
                new_status=FreightStatus.CANCELLED
            )


if __name__ == "__main__":
    unittest.main()
