import unittest
from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    FreightNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.use_cases.cancel_freight import (
    CancelFreight
)
from application.use_cases.complete_freight import (
    CompleteFreight
)
from application.use_cases.start_freight import (
    StartFreight
)
from domain.models.freight import (
    Freight,
    FreightStatus
)
from domain.models.freight_event import (
    FreightEventType
)


class FakeFreightRepository:

    def __init__(
        self,
        freight: Freight | None
    ):
        self.freight = freight
        self.saved: Freight | None = None

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

    def save(
        self,
        freight: Freight
    ) -> Freight:
        self.saved = freight
        self.freight = freight
        return freight


class FakeFreightTransportUnitRepository:

    def __init__(
        self,
        count: int
    ):
        self.count = count

    def count_by_freight_id(
        self,
        freight_id: int
    ) -> int:
        return self.count


class FakeFreightUnitOfWork:

    def __init__(
        self,
        repository: FakeFreightRepository,
        transport_unit_count: int
    ):
        self.freights = repository
        self.transport_units = (
            FakeFreightTransportUnitRepository(
                transport_unit_count
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
        transport_unit_count: int = 1
    ):
        self.repository = (
            FakeFreightRepository(
                freight
            )
        )
        self.transport_unit_count = (
            transport_unit_count
        )
        self.created: list[
            FakeFreightUnitOfWork
        ] = []

    def create(
        self
    ) -> FakeFreightUnitOfWork:
        unit_of_work = FakeFreightUnitOfWork(
            self.repository,
            self.transport_unit_count
        )
        self.created.append(
            unit_of_work
        )
        return unit_of_work


def make_freight(
    status: FreightStatus = FreightStatus.PENDING
) -> Freight:

    started_at = (
        datetime.now(timezone.utc)
        if status
        in {
            FreightStatus.IN_PROGRESS,
            FreightStatus.COMPLETED
        }
        else None
    )

    completed_at = (
        datetime.now(timezone.utc)
        if status == FreightStatus.COMPLETED
        else None
    )

    cancelled_at = (
        datetime.now(timezone.utc)
        if status == FreightStatus.CANCELLED
        else None
    )

    return Freight(
        freight_id=77,
        customer_id=5,
        primary_quote_id=1,
        current_status=status,
        started_at=started_at,
        completed_at=completed_at,
        cancelled_at=cancelled_at
    )


class FreightStatusUseCaseTests(
    unittest.TestCase
):

    def test_starts_pending_freight(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(),
            transport_unit_count=1
        )

        result = StartFreight(
            factory
        ).execute(
            freight_id=77,
            user_id=9,
            observation="Saída confirmada"
        )

        self.assertEqual(
            result.current_status,
            FreightStatus.IN_PROGRESS
        )
        self.assertIsNotNone(
            result.started_at
        )
        self.assertEqual(
            result.events[-1].event_type,
            FreightEventType.STARTED
        )
        self.assertEqual(
            result.events[-1].user_id,
            9
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_rejects_start_without_transport_unit(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(),
            transport_unit_count=0
        )

        with self.assertRaises(
            InvalidFreightStateError
        ):
            StartFreight(
                factory
            ).execute(
                freight_id=77
            )

        self.assertFalse(
            factory.created[-1].committed
        )

    def test_completes_in_progress_freight(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.IN_PROGRESS
            )
        )

        result = CompleteFreight(
            factory
        ).execute(
            freight_id=77
        )

        self.assertEqual(
            result.current_status,
            FreightStatus.COMPLETED
        )
        self.assertIsNotNone(
            result.completed_at
        )
        self.assertEqual(
            result.events[-1].event_type,
            FreightEventType.COMPLETED
        )

    def test_cancels_pending_freight(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight()
        )

        result = CancelFreight(
            factory
        ).execute(
            freight_id=77
        )

        self.assertEqual(
            result.current_status,
            FreightStatus.CANCELLED
        )
        self.assertIsNone(
            result.started_at
        )
        self.assertIsNotNone(
            result.cancelled_at
        )

    def test_cancels_in_progress_and_preserves_start(
        self
    ) -> None:
        original = make_freight(
            FreightStatus.IN_PROGRESS
        )
        factory = FakeFreightUnitOfWorkFactory(
            original
        )

        result = CancelFreight(
            factory
        ).execute(
            freight_id=77
        )

        self.assertEqual(
            result.started_at,
            original.started_at
        )
        self.assertIsNotNone(
            result.cancelled_at
        )
        self.assertEqual(
            result.events[-1].event_type,
            FreightEventType.CANCELLED
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
            StartFreight(
                factory
            ).execute(
                freight_id=77
            )

    def test_rejects_complete_from_pending(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight()
        )

        with self.assertRaises(
            InvalidFreightStateError
        ):
            CompleteFreight(
                factory
            ).execute(
                freight_id=77
            )

    def test_rejects_transition_from_terminal_state(
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
            CancelFreight(
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
            StartFreight(
                factory
            ).execute(
                freight_id=0
            )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            StartFreight(
                factory
            ).execute(
                freight_id=77,
                user_id=0
            )


if __name__ == "__main__":
    unittest.main()
