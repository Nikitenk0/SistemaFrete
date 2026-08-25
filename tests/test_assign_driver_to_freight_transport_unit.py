import unittest
from dataclasses import replace
from datetime import (
    datetime,
    timezone
)
from types import SimpleNamespace

from application.exceptions import (
    DriverNotFoundError,
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidDriverStateError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.use_cases.assign_driver_to_freight_transport_unit import (
    AssignDriverToFreightTransportUnit
)
from domain.models.driver import (
    DriverStatus
)
from domain.models.freight import (
    Freight,
    FreightStatus
)
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


class FakeDriverRepository:

    def __init__(self, driver):
        self.driver = driver

    def get_by_id(self, driver_id):
        if (
            self.driver is not None
            and self.driver.driver_id == driver_id
        ):
            return self.driver
        return None


class FakeAssignmentRepository:

    def __init__(
        self,
        active_unit_assignment=None,
        active_driver_assignment=None
    ):
        self.active_unit_assignment = active_unit_assignment
        self.active_driver_assignment = active_driver_assignment
        self.added = None

    def get_active_by_transport_unit_id(self, _unit_id):
        return self.active_unit_assignment

    def get_active_by_driver_id(self, _driver_id):
        return self.active_driver_assignment

    def add(self, assignment):
        created = replace(
            assignment,
            freight_driver_assignment_id=501
        )
        self.added = created
        return created


class FakeUnitOfWork:

    def __init__(
        self,
        freight,
        transport_unit,
        driver,
        active_unit_assignment=None,
        active_driver_assignment=None
    ):
        self.freights = FakeFreightRepository(freight)
        self.transport_units = FakeTransportUnitRepository(
            transport_unit
        )
        self.drivers = FakeDriverRepository(driver)
        self.driver_assignments = FakeAssignmentRepository(
            active_unit_assignment,
            active_driver_assignment
        )
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

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.created = []

    def create(self):
        unit_of_work = FakeUnitOfWork(
            **self.kwargs
        )
        self.created.append(unit_of_work)
        return unit_of_work


def make_freight(
    status=FreightStatus.PENDING
):
    now = datetime.now(timezone.utc)
    return Freight(
        freight_id=77,
        customer_id=5,
        primary_quote_id=1,
        current_status=status,
        started_at=(
            now
            if status in {
                FreightStatus.IN_PROGRESS,
                FreightStatus.COMPLETED
            }
            else None
        ),
        completed_at=(
            now
            if status == FreightStatus.COMPLETED
            else None
        ),
        cancelled_at=(
            now
            if status == FreightStatus.CANCELLED
            else None
        )
    )


def make_unit():
    return FreightTransportUnit(
        freight_transport_unit_id=101,
        freight_id=77,
        position=1
    )


def make_driver(
    status=DriverStatus.ACTIVE
):
    return SimpleNamespace(
        driver_id=8,
        status=status
    )


def make_active_assignment(
    unit_id=101,
    driver_id=8
):
    return FreightDriverAssignment(
        freight_driver_assignment_id=400,
        freight_transport_unit_id=unit_id,
        driver_id=driver_id,
        started_at=STARTED_AT
    )


class AssignDriverToFreightTransportUnitTests(
    unittest.TestCase
):

    def test_assigns_active_driver_to_pending_freight_unit(
        self
    ) -> None:
        factory = FakeFactory(
            freight=make_freight(),
            transport_unit=make_unit(),
            driver=make_driver()
        )

        result = AssignDriverToFreightTransportUnit(
            factory
        ).execute(
            freight_transport_unit_id=101,
            driver_id=8,
            started_at=STARTED_AT,
            created_by=9
        )

        self.assertEqual(
            result.freight_driver_assignment_id,
            501
        )
        self.assertEqual(
            result.freight_transport_unit_id,
            101
        )
        self.assertEqual(
            result.driver_id,
            8
        )
        self.assertTrue(
            result.is_active
        )
        self.assertEqual(
            result.created_by,
            9
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_allows_assignment_while_freight_is_in_progress(
        self
    ) -> None:
        factory = FakeFactory(
            freight=make_freight(
                FreightStatus.IN_PROGRESS
            ),
            transport_unit=make_unit(),
            driver=make_driver()
        )

        result = AssignDriverToFreightTransportUnit(
            factory
        ).execute(
            freight_transport_unit_id=101,
            driver_id=8,
            started_at=STARTED_AT
        )

        self.assertTrue(result.is_active)

    def test_rejects_missing_transport_unit(
        self
    ) -> None:
        factory = FakeFactory(
            freight=make_freight(),
            transport_unit=None,
            driver=make_driver()
        )

        with self.assertRaises(
            FreightTransportUnitNotFoundError
        ):
            AssignDriverToFreightTransportUnit(
                factory
            ).execute(101, 8)

    def test_rejects_missing_freight(
        self
    ) -> None:
        factory = FakeFactory(
            freight=None,
            transport_unit=make_unit(),
            driver=make_driver()
        )

        with self.assertRaises(
            FreightNotFoundError
        ):
            AssignDriverToFreightTransportUnit(
                factory
            ).execute(101, 8)

    def test_rejects_terminal_freight(
        self
    ) -> None:
        for status in (
            FreightStatus.COMPLETED,
            FreightStatus.CANCELLED
        ):
            with self.subTest(status=status):
                factory = FakeFactory(
                    freight=make_freight(status),
                    transport_unit=make_unit(),
                    driver=make_driver()
                )

                with self.assertRaises(
                    InvalidFreightStateError
                ):
                    AssignDriverToFreightTransportUnit(
                        factory
                    ).execute(101, 8)

    def test_rejects_missing_driver(
        self
    ) -> None:
        factory = FakeFactory(
            freight=make_freight(),
            transport_unit=make_unit(),
            driver=None
        )

        with self.assertRaises(
            DriverNotFoundError
        ):
            AssignDriverToFreightTransportUnit(
                factory
            ).execute(101, 8)

    def test_rejects_inactive_driver(
        self
    ) -> None:
        factory = FakeFactory(
            freight=make_freight(),
            transport_unit=make_unit(),
            driver=make_driver(
                DriverStatus.INACTIVE
            )
        )

        with self.assertRaises(
            InvalidDriverStateError
        ):
            AssignDriverToFreightTransportUnit(
                factory
            ).execute(101, 8)

    def test_rejects_second_active_driver_in_same_unit(
        self
    ) -> None:
        factory = FakeFactory(
            freight=make_freight(),
            transport_unit=make_unit(),
            driver=make_driver(),
            active_unit_assignment=(
                make_active_assignment()
            )
        )

        with self.assertRaises(
            InvalidFreightStateError
        ):
            AssignDriverToFreightTransportUnit(
                factory
            ).execute(101, 8)

    def test_rejects_driver_already_active_in_another_unit(
        self
    ) -> None:
        factory = FakeFactory(
            freight=make_freight(),
            transport_unit=make_unit(),
            driver=make_driver(),
            active_driver_assignment=(
                make_active_assignment(
                    unit_id=202,
                    driver_id=8
                )
            )
        )

        with self.assertRaises(
            InvalidFreightStateError
        ):
            AssignDriverToFreightTransportUnit(
                factory
            ).execute(101, 8)

    def test_rejects_invalid_identifiers(
        self
    ) -> None:
        factory = FakeFactory(
            freight=make_freight(),
            transport_unit=make_unit(),
            driver=make_driver()
        )

        use_case = AssignDriverToFreightTransportUnit(
            factory
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            use_case.execute(0, 8)

        with self.assertRaises(
            InvalidFreightDataError
        ):
            use_case.execute(101, 0)

        with self.assertRaises(
            InvalidFreightDataError
        ):
            use_case.execute(101, 8, created_by=0)


if __name__ == "__main__":
    unittest.main()
