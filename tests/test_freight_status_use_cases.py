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
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)
from domain.models.freight_event import (
    FreightEventType
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit
)
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType,
    get_freight_vehicle_specification
)


NOW = datetime(
    2026,
    8,
    25,
    12,
    0,
    tzinfo=timezone.utc
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
        transport_units: tuple[
            FreightTransportUnit,
            ...
        ]
    ):
        self.transport_units = transport_units
        self.list_calls = 0

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightTransportUnit, ...]:
        self.list_calls += 1
        return self.transport_units


class FakeFreightDriverAssignmentRepository:

    def __init__(
        self,
        assignments: tuple[
            FreightDriverAssignment,
            ...
        ]
    ):
        self.assignments = assignments
        self.list_calls = 0

    def list_active_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightDriverAssignment, ...]:
        self.list_calls += 1
        return self.assignments

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightDriverAssignment, ...]:
        self.list_calls += 1
        return self.assignments


class FakeFreightVehicleRecordRepository:

    def __init__(
        self,
        vehicle_records: tuple[
            FreightVehicleRecord,
            ...
        ]
    ):
        self.vehicle_records = vehicle_records
        self.list_calls = 0

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightVehicleRecord, ...]:
        self.list_calls += 1
        return self.vehicle_records


class FakeFreightUnitOfWork:

    def __init__(
        self,
        repository: FakeFreightRepository,
        transport_units: tuple[
            FreightTransportUnit,
            ...
        ],
        assignments: tuple[
            FreightDriverAssignment,
            ...
        ],
        vehicle_records: tuple[
            FreightVehicleRecord,
            ...
        ]
    ):
        self.freights = repository
        self.transport_units = (
            FakeFreightTransportUnitRepository(
                transport_units
            )
        )
        self.driver_assignments = (
            FakeFreightDriverAssignmentRepository(
                assignments
            )
        )
        self.vehicle_records = (
            FakeFreightVehicleRecordRepository(
                vehicle_records
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
        transport_units: tuple[
            FreightTransportUnit,
            ...
        ] | None = None,
        assignments: tuple[
            FreightDriverAssignment,
            ...
        ] | None = None,
        vehicle_records: tuple[
            FreightVehicleRecord,
            ...
        ] | None = None
    ):
        self.repository = (
            FakeFreightRepository(
                freight
            )
        )

        if transport_units is None:
            transport_units = (
                make_transport_unit(
                    101,
                    1
                ),
            )

        if assignments is None:
            assignments = (
                make_assignment(
                    101,
                    8
                ),
            )

        if vehicle_records is None:
            vehicle_records = (
                make_vehicle(
                    101,
                    "ABC1D23"
                ),
            )

        self.transport_units = transport_units
        self.assignments = assignments
        self.vehicle_records = vehicle_records
        self.created: list[
            FakeFreightUnitOfWork
        ] = []

    def create(
        self
    ) -> FakeFreightUnitOfWork:
        unit_of_work = FakeFreightUnitOfWork(
            self.repository,
            self.transport_units,
            self.assignments,
            self.vehicle_records
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


def make_transport_unit(
    unit_id: int,
    position: int
) -> FreightTransportUnit:
    return FreightTransportUnit(
        freight_transport_unit_id=unit_id,
        freight_id=77,
        position=position,
        created_at=NOW
    )


def make_assignment(
    unit_id: int,
    driver_id: int
) -> FreightDriverAssignment:
    return FreightDriverAssignment(
        freight_driver_assignment_id=(
            1000 + unit_id
        ),
        freight_transport_unit_id=unit_id,
        driver_id=driver_id,
        started_at=NOW,
        created_at=NOW,
        updated_at=NOW
    )


def make_finished_assignment(
    unit_id: int,
    driver_id: int,
    amount: str = "1000.00"
) -> FreightDriverAssignment:
    return FreightDriverAssignment(
        freight_driver_assignment_id=(
            1000 + unit_id + driver_id
        ),
        freight_transport_unit_id=unit_id,
        driver_id=driver_id,
        started_at=NOW,
        ended_at=NOW,
        actual_driver_amount=amount,
        created_at=NOW,
        updated_at=NOW
    )


def make_vehicle(
    unit_id: int,
    plate: str
) -> FreightVehicleRecord:
    vehicle_type = FreightVehicleType.TRUCK
    specification = get_freight_vehicle_specification(
        vehicle_type
    )

    return FreightVehicleRecord(
        freight_vehicle_record_id=(
            2000 + unit_id
        ),
        freight_transport_unit_id=unit_id,
        vehicle_type=vehicle_type,
        plate=plate,
        axle_count=specification.axle_count,
        pallet_capacity_min=(
            specification.pallet_capacity_min
        ),
        pallet_capacity_max=(
            specification.pallet_capacity_max
        ),
        payload_capacity_kg=(
            specification.payload_capacity_kg
        ),
        created_at=NOW
    )


class FreightStatusUseCaseTests(
    unittest.TestCase
):

    def test_starts_pending_freight_when_unit_is_ready(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight()
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

        unit_of_work = factory.created[-1]
        self.assertEqual(
            unit_of_work.transport_units.list_calls,
            1
        )
        self.assertEqual(
            unit_of_work.driver_assignments.list_calls,
            1
        )
        self.assertEqual(
            unit_of_work.vehicle_records.list_calls,
            1
        )

    def test_rejects_start_without_transport_unit(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(),
            transport_units=(),
            assignments=(),
            vehicle_records=()
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "pelo menos uma unidade de transporte"
        ):
            StartFreight(
                factory
            ).execute(
                freight_id=77
            )

        self.assertFalse(
            factory.created[-1].committed
        )

    def test_rejects_start_without_active_driver(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(),
            assignments=()
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Unidade de transporte 1.*motorista ativo"
        ):
            StartFreight(
                factory
            ).execute(
                freight_id=77
            )

    def test_rejects_start_without_vehicle(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(),
            vehicle_records=()
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Unidade de transporte 1.*veículo operacional"
        ):
            StartFreight(
                factory
            ).execute(
                freight_id=77
            )

    def test_rejects_start_when_second_unit_is_not_ready(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(),
            transport_units=(
                make_transport_unit(
                    101,
                    1
                ),
                make_transport_unit(
                    102,
                    2
                )
            ),
            assignments=(
                make_assignment(
                    101,
                    8
                ),
            ),
            vehicle_records=(
                make_vehicle(
                    101,
                    "ABC1D23"
                ),
                make_vehicle(
                    102,
                    "DEF4G56"
                )
            )
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Unidade de transporte 2.*motorista ativo"
        ):
            StartFreight(
                factory
            ).execute(
                freight_id=77
            )

    def test_starts_with_multiple_ready_units(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(),
            transport_units=(
                make_transport_unit(
                    101,
                    1
                ),
                make_transport_unit(
                    102,
                    2
                )
            ),
            assignments=(
                make_assignment(
                    101,
                    8
                ),
                make_assignment(
                    102,
                    9
                )
            ),
            vehicle_records=(
                make_vehicle(
                    101,
                    "ABC1D23"
                ),
                make_vehicle(
                    102,
                    "DEF4G56"
                )
            )
        )

        result = StartFreight(
            factory
        ).execute(
            freight_id=77
        )

        self.assertEqual(
            result.current_status,
            FreightStatus.IN_PROGRESS
        )

    def test_completes_in_progress_freight(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.IN_PROGRESS
            ),
            assignments=(
                make_finished_assignment(
                    101,
                    8
                ),
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

        unit_of_work = factory.created[-1]
        self.assertEqual(
            unit_of_work.transport_units.list_calls,
            1
        )
        self.assertEqual(
            unit_of_work.driver_assignments.list_calls,
            1
        )
        self.assertEqual(
            unit_of_work.vehicle_records.list_calls,
            1
        )

    def test_rejects_complete_without_driver_assignment(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.IN_PROGRESS
            ),
            assignments=()
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Unidade de transporte 1.*participação de motorista"
        ):
            CompleteFreight(
                factory
            ).execute(
                freight_id=77
            )

        self.assertFalse(
            factory.created[-1].committed
        )

    def test_rejects_complete_with_active_driver(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.IN_PROGRESS
            )
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Unidade de transporte 1.*motorista ativo"
        ):
            CompleteFreight(
                factory
            ).execute(
                freight_id=77
            )

    def test_rejects_complete_without_vehicle(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.IN_PROGRESS
            ),
            assignments=(
                make_finished_assignment(
                    101,
                    8
                ),
            ),
            vehicle_records=()
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Unidade de transporte 1.*veículo operacional"
        ):
            CompleteFreight(
                factory
            ).execute(
                freight_id=77
            )

    def test_rejects_complete_when_second_unit_has_active_driver(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.IN_PROGRESS
            ),
            transport_units=(
                make_transport_unit(
                    101,
                    1
                ),
                make_transport_unit(
                    102,
                    2
                )
            ),
            assignments=(
                make_finished_assignment(
                    101,
                    8
                ),
                make_assignment(
                    102,
                    9
                )
            ),
            vehicle_records=(
                make_vehicle(
                    101,
                    "ABC1D23"
                ),
                make_vehicle(
                    102,
                    "DEF4G56"
                )
            )
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Unidade de transporte 2.*motorista ativo"
        ):
            CompleteFreight(
                factory
            ).execute(
                freight_id=77
            )

    def test_completes_with_multiple_finished_assignments(
        self
    ) -> None:
        factory = FakeFreightUnitOfWorkFactory(
            make_freight(
                FreightStatus.IN_PROGRESS
            ),
            transport_units=(
                make_transport_unit(
                    101,
                    1
                ),
                make_transport_unit(
                    102,
                    2
                )
            ),
            assignments=(
                make_finished_assignment(
                    101,
                    8,
                    "2000.00"
                ),
                make_finished_assignment(
                    101,
                    10,
                    "2300.00"
                ),
                make_finished_assignment(
                    102,
                    9,
                    "3800.00"
                )
            ),
            vehicle_records=(
                make_vehicle(
                    101,
                    "ABC1D23"
                ),
                make_vehicle(
                    102,
                    "DEF4G56"
                )
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
