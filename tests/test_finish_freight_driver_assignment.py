import unittest
from datetime import (
    datetime,
    timedelta,
    timezone
)
from decimal import Decimal

from application.exceptions import (
    FreightDriverAssignmentNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.use_cases.finish_freight_driver_assignment import (
    FinishFreightDriverAssignment
)
from domain.models.freight import Freight
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit
)


STARTED_AT = datetime(
    2026,
    8,
    25,
    8,
    0,
    tzinfo=timezone.utc
)
ENDED_AT = STARTED_AT + timedelta(hours=5)


class FakeFreightRepository:

    def __init__(self, freight):
        self.freight = freight

    def get_by_id_for_update(self, freight_id):
        if (
            self.freight is not None
            and self.freight.freight_id == freight_id
        ):
            return self.freight
        return None


class FakeTransportUnitRepository:

    def __init__(self, transport_unit):
        self.transport_unit = transport_unit

    def get_by_id(self, transport_unit_id):
        if (
            self.transport_unit is not None
            and self.transport_unit.freight_transport_unit_id
            == transport_unit_id
        ):
            return self.transport_unit
        return None


class FakeAssignmentRepository:

    def __init__(self, assignment):
        self.assignment = assignment
        self.saved = None

    def get_by_id(self, assignment_id):
        if (
            self.assignment is not None
            and self.assignment.freight_driver_assignment_id
            == assignment_id
        ):
            return self.assignment
        return None

    def save(self, assignment):
        self.assignment = assignment
        self.saved = assignment
        return assignment


class FakeUnitOfWork:

    def __init__(
        self,
        freight,
        transport_unit,
        assignment
    ):
        self.freights = FakeFreightRepository(freight)
        self.transport_units = FakeTransportUnitRepository(
            transport_unit
        )
        self.driver_assignments = FakeAssignmentRepository(
            assignment
        )
        self.drivers = None
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeFactory:

    def __init__(self, assignment):
        self.assignment = assignment
        self.created = []

    def create(self):
        unit_of_work = FakeUnitOfWork(
            freight=Freight(
                freight_id=77,
                customer_id=5,
                primary_quote_id=1
            ),
            transport_unit=FreightTransportUnit(
                freight_transport_unit_id=101,
                freight_id=77,
                position=1
            ),
            assignment=self.assignment
        )
        self.created.append(unit_of_work)
        return unit_of_work


def make_active_assignment():
    return FreightDriverAssignment(
        freight_driver_assignment_id=501,
        freight_transport_unit_id=101,
        driver_id=8,
        started_at=STARTED_AT,
        created_by=9
    )


def make_finished_assignment():
    return FreightDriverAssignment(
        freight_driver_assignment_id=501,
        freight_transport_unit_id=101,
        driver_id=8,
        started_at=STARTED_AT,
        ended_at=ENDED_AT,
        actual_driver_amount=Decimal("2300.00"),
        created_by=9,
        updated_by=9
    )


class FinishFreightDriverAssignmentTests(
    unittest.TestCase
):

    def test_finishes_assignment_and_records_realized_amount(
        self
    ) -> None:
        factory = FakeFactory(
            make_active_assignment()
        )

        result = FinishFreightDriverAssignment(
            factory
        ).execute(
            freight_driver_assignment_id=501,
            actual_driver_amount=Decimal("2300.00"),
            ended_at=ENDED_AT,
            updated_by=10
        )

        self.assertFalse(
            result.is_active
        )
        self.assertEqual(
            result.ended_at,
            ENDED_AT
        )
        self.assertEqual(
            result.actual_driver_amount,
            Decimal("2300.00")
        )
        self.assertEqual(
            result.updated_by,
            10
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_rejects_missing_assignment(
        self
    ) -> None:
        factory = FakeFactory(None)

        with self.assertRaises(
            FreightDriverAssignmentNotFoundError
        ):
            FinishFreightDriverAssignment(
                factory
            ).execute(
                501,
                Decimal("100.00")
            )

    def test_rejects_assignment_already_finished(
        self
    ) -> None:
        factory = FakeFactory(
            make_finished_assignment()
        )

        with self.assertRaises(
            InvalidFreightStateError
        ):
            FinishFreightDriverAssignment(
                factory
            ).execute(
                501,
                Decimal("100.00")
            )

    def test_rejects_end_before_start(
        self
    ) -> None:
        factory = FakeFactory(
            make_active_assignment()
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            FinishFreightDriverAssignment(
                factory
            ).execute(
                501,
                Decimal("100.00"),
                ended_at=(
                    STARTED_AT
                    - timedelta(minutes=1)
                )
            )

    def test_rejects_negative_realized_amount(
        self
    ) -> None:
        factory = FakeFactory(
            make_active_assignment()
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            FinishFreightDriverAssignment(
                factory
            ).execute(
                501,
                Decimal("-0.01"),
                ended_at=ENDED_AT
            )

    def test_rejects_invalid_identifiers(
        self
    ) -> None:
        factory = FakeFactory(
            make_active_assignment()
        )

        use_case = FinishFreightDriverAssignment(
            factory
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            use_case.execute(
                0,
                Decimal("100.00")
            )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            use_case.execute(
                501,
                Decimal("100.00"),
                updated_by=0
            )


if __name__ == "__main__":
    unittest.main()
