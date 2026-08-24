import unittest
from dataclasses import replace
from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    FreightNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.use_cases.add_freight_transport_unit import (
    AddFreightTransportUnit
)
from domain.models.freight import (
    Freight,
    FreightStatus
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit
)


class FakeFreightRepository:

    def __init__(
        self,
        freight: Freight | None
    ):
        self.freight = freight

    def get_by_id_for_update(
        self,
        freight_id: int
    ) -> Freight | None:
        if (
            self.freight is not None
            and self.freight.freight_id
            == freight_id
        ):
            return self.freight

        return None


class FakeFreightTransportUnitRepository:

    def __init__(
        self,
        units: tuple[FreightTransportUnit, ...] = ()
    ):
        self.units = units
        self.added: FreightTransportUnit | None = None

    def add(
        self,
        transport_unit: FreightTransportUnit
    ) -> FreightTransportUnit:
        created = replace(
            transport_unit,
            freight_transport_unit_id=(
                100 + transport_unit.position
            )
        )
        self.added = created
        self.units = (
            *self.units,
            created
        )
        return created

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightTransportUnit, ...]:
        return tuple(
            unit
            for unit in self.units
            if unit.freight_id == freight_id
        )

    def count_by_freight_id(
        self,
        freight_id: int
    ) -> int:
        return len(
            self.list_by_freight_id(
                freight_id
            )
        )


class FakeFreightUnitOfWork:

    def __init__(
        self,
        freight: Freight | None,
        units: tuple[FreightTransportUnit, ...] = ()
    ):
        self.freights = FakeFreightRepository(
            freight
        )
        self.transport_units = (
            FakeFreightTransportUnitRepository(
                units
            )
        )
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


class FakeFreightUnitOfWorkFactory:

    def __init__(
        self,
        freight: Freight | None,
        units: tuple[FreightTransportUnit, ...] = ()
    ):
        self.freight = freight
        self.units = units
        self.created: list[
            FakeFreightUnitOfWork
        ] = []

    def create(
        self
    ) -> FakeFreightUnitOfWork:
        unit_of_work = FakeFreightUnitOfWork(
            self.freight,
            self.units
        )
        self.created.append(
            unit_of_work
        )
        return unit_of_work


def make_freight(
    status: FreightStatus = FreightStatus.PENDING
) -> Freight:
    now = datetime.now(
        timezone.utc
    )

    return Freight(
        freight_id=77,
        customer_id=5,
        primary_quote_id=1,
        current_status=status,
        started_at=(
            now
            if status
            in {
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


def make_unit(
    position: int
) -> FreightTransportUnit:
    return FreightTransportUnit(
        freight_transport_unit_id=(
            100 + position
        ),
        freight_id=77,
        position=position
    )


class AddFreightTransportUnitTests(
    unittest.TestCase
):

    def test_adds_first_unit_to_pending_freight(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight()
        )

        result = AddFreightTransportUnit(
            factory
        ).execute(
            freight_id=77,
            created_by=9
        )

        self.assertEqual(
            result.freight_transport_unit_id,
            101
        )
        self.assertEqual(
            result.position,
            1
        )
        self.assertEqual(
            result.created_by,
            9
        )
        self.assertIsNotNone(
            result.created_at
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_uses_next_position_after_existing_units(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(),
            (
                make_unit(1),
                make_unit(3),
            )
        )

        result = AddFreightTransportUnit(
            factory
        ).execute(
            freight_id=77
        )

        self.assertEqual(
            result.position,
            4
        )

    def test_adds_unit_while_freight_is_in_progress(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.IN_PROGRESS
            )
        )

        result = AddFreightTransportUnit(
            factory
        ).execute(
            freight_id=77
        )

        self.assertEqual(
            result.position,
            1
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_rejects_completed_freight(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.COMPLETED
            )
        )

        with self.assertRaises(
            InvalidFreightStateError
        ):
            AddFreightTransportUnit(
                factory
            ).execute(
                freight_id=77
            )

    def test_rejects_cancelled_freight(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.CANCELLED
            )
        )

        with self.assertRaises(
            InvalidFreightStateError
        ):
            AddFreightTransportUnit(
                factory
            ).execute(
                freight_id=77
            )

    def test_rejects_missing_freight(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            None
        )

        with self.assertRaises(
            FreightNotFoundError
        ):
            AddFreightTransportUnit(
                factory
            ).execute(
                freight_id=77
            )

    def test_rejects_invalid_identifiers(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight()
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            AddFreightTransportUnit(
                factory
            ).execute(
                freight_id=0
            )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            AddFreightTransportUnit(
                factory
            ).execute(
                freight_id=77,
                created_by=0
            )


if __name__ == "__main__":
    unittest.main()
