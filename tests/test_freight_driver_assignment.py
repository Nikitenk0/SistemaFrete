import unittest
from datetime import (
    datetime,
    timedelta,
    timezone
)
from decimal import Decimal

from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)


STARTED_AT = datetime(
    2026,
    8,
    25,
    8,
    0,
    tzinfo=timezone.utc
)


class FreightDriverAssignmentTests(
    unittest.TestCase
):

    def test_creates_active_assignment(
        self
    ) -> None:
        assignment = FreightDriverAssignment(
            freight_transport_unit_id=11,
            driver_id=7,
            started_at=STARTED_AT,
            created_by=3
        )

        self.assertTrue(
            assignment.is_active
        )
        self.assertIsNone(
            assignment.ended_at
        )
        self.assertIsNone(
            assignment.actual_driver_amount
        )

    def test_creates_finished_assignment_with_realized_amount(
        self
    ) -> None:
        assignment = FreightDriverAssignment(
            freight_transport_unit_id=11,
            driver_id=7,
            started_at=STARTED_AT,
            ended_at=(
                STARTED_AT
                + timedelta(hours=5)
            ),
            actual_driver_amount=Decimal("2300.00")
        )

        self.assertFalse(
            assignment.is_active
        )
        self.assertEqual(
            assignment.actual_driver_amount,
            Decimal("2300.00")
        )

    def test_rejects_invalid_identifiers(
        self
    ) -> None:
        with self.assertRaises(ValueError):
            FreightDriverAssignment(
                freight_transport_unit_id=0,
                driver_id=7,
                started_at=STARTED_AT
            )

        with self.assertRaises(ValueError):
            FreightDriverAssignment(
                freight_transport_unit_id=11,
                driver_id=0,
                started_at=STARTED_AT
            )

        with self.assertRaises(ValueError):
            FreightDriverAssignment(
                freight_transport_unit_id=11,
                driver_id=7,
                started_at=STARTED_AT,
                freight_driver_assignment_id=0
            )

    def test_rejects_end_before_start(
        self
    ) -> None:
        with self.assertRaises(ValueError):
            FreightDriverAssignment(
                freight_transport_unit_id=11,
                driver_id=7,
                started_at=STARTED_AT,
                ended_at=(
                    STARTED_AT
                    - timedelta(minutes=1)
                ),
                actual_driver_amount=Decimal("100.00")
            )

    def test_rejects_amount_while_assignment_is_active(
        self
    ) -> None:
        with self.assertRaises(ValueError):
            FreightDriverAssignment(
                freight_transport_unit_id=11,
                driver_id=7,
                started_at=STARTED_AT,
                actual_driver_amount=Decimal("100.00")
            )

    def test_rejects_finished_assignment_without_amount(
        self
    ) -> None:
        with self.assertRaises(ValueError):
            FreightDriverAssignment(
                freight_transport_unit_id=11,
                driver_id=7,
                started_at=STARTED_AT,
                ended_at=(
                    STARTED_AT
                    + timedelta(hours=1)
                )
            )

    def test_rejects_negative_realized_amount(
        self
    ) -> None:
        with self.assertRaises(ValueError):
            FreightDriverAssignment(
                freight_transport_unit_id=11,
                driver_id=7,
                started_at=STARTED_AT,
                ended_at=(
                    STARTED_AT
                    + timedelta(hours=1)
                ),
                actual_driver_amount=Decimal("-0.01")
            )


if __name__ == "__main__":
    unittest.main()
