import unittest
from datetime import datetime, timezone

from application.exceptions import (
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError,
)
from application.use_cases.remove_freight_vehicle_record import (
    RemoveFreightVehicleRecord,
)
from domain.models.freight import Freight, FreightStatus
from domain.models.freight_transport_unit import FreightTransportUnit
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType,
)


class FakeFreightRepository:

    def __init__(self, freight: Freight | None):
        self.freight = freight

    def get_by_id_for_update(self, freight_id: int) -> Freight | None:
        if self.freight is not None and self.freight.freight_id == freight_id:
            return self.freight
        return None


class FakeTransportUnitRepository:

    def __init__(self, unit: FreightTransportUnit | None):
        self.unit = unit

    def get_by_id(
        self,
        freight_transport_unit_id: int,
    ) -> FreightTransportUnit | None:
        if (
            self.unit is not None
            and self.unit.freight_transport_unit_id
            == freight_transport_unit_id
        ):
            return self.unit
        return None


class FakeVehicleRecordRepository:

    def __init__(self, record: FreightVehicleRecord | None):
        self.record = record
        self.deleted_transport_unit_id: int | None = None

    def get_by_transport_unit_id(
        self,
        freight_transport_unit_id: int,
    ) -> FreightVehicleRecord | None:
        if (
            self.record is not None
            and self.record.freight_transport_unit_id
            == freight_transport_unit_id
        ):
            return self.record
        return None

    def delete_by_transport_unit_id(
        self,
        freight_transport_unit_id: int,
    ) -> None:
        self.deleted_transport_unit_id = freight_transport_unit_id
        self.record = None


class FakeUnitOfWork:

    def __init__(
        self,
        freight: Freight | None,
        unit: FreightTransportUnit | None,
        record: FreightVehicleRecord | None,
    ):
        self.freights = FakeFreightRepository(freight)
        self.transport_units = FakeTransportUnitRepository(unit)
        self.vehicle_records = FakeVehicleRecordRepository(record)
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


class FakeUnitOfWorkFactory:

    def __init__(
        self,
        freight: Freight | None,
        unit: FreightTransportUnit | None,
        record: FreightVehicleRecord | None,
    ):
        self.freight = freight
        self.unit = unit
        self.record = record
        self.created: list[FakeUnitOfWork] = []

    def create(self) -> FakeUnitOfWork:
        unit_of_work = FakeUnitOfWork(
            self.freight,
            self.unit,
            self.record,
        )
        self.created.append(unit_of_work)
        return unit_of_work


def make_freight(
    status: FreightStatus = FreightStatus.PENDING,
) -> Freight:
    now = datetime.now(timezone.utc)
    return Freight(
        freight_id=77,
        customer_id=5,
        primary_quote_id=1,
        current_status=status,
        started_at=(
            now
            if status in {FreightStatus.IN_PROGRESS, FreightStatus.COMPLETED}
            else None
        ),
        completed_at=(
            now if status == FreightStatus.COMPLETED else None
        ),
        cancelled_at=(
            now if status == FreightStatus.CANCELLED else None
        ),
    )


def make_unit() -> FreightTransportUnit:
    return FreightTransportUnit(
        freight_transport_unit_id=12,
        freight_id=77,
        position=1,
    )


def make_record() -> FreightVehicleRecord:
    return FreightVehicleRecord(
        freight_vehicle_record_id=81,
        freight_transport_unit_id=12,
        vehicle_type=FreightVehicleType.TOCO,
        plate="ABC1234",
        axle_count=2,
        pallet_capacity_min=12,
        pallet_capacity_max=12,
        payload_capacity_kg=6500,
    )


class RemoveFreightVehicleRecordTests(unittest.TestCase):

    def test_removes_vehicle_from_pending_freight(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit(),
            make_record(),
        )

        RemoveFreightVehicleRecord(factory).execute(12)

        unit_of_work = factory.created[-1]
        self.assertEqual(
            unit_of_work.vehicle_records.deleted_transport_unit_id,
            12,
        )
        self.assertTrue(unit_of_work.committed)

    def test_rejects_invalid_transport_unit_id(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit(),
            make_record(),
        )

        with self.assertRaises(InvalidFreightDataError):
            RemoveFreightVehicleRecord(factory).execute(0)

    def test_rejects_missing_transport_unit(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            None,
            make_record(),
        )

        with self.assertRaises(FreightTransportUnitNotFoundError):
            RemoveFreightVehicleRecord(factory).execute(12)

    def test_rejects_missing_freight(self) -> None:
        factory = FakeUnitOfWorkFactory(
            None,
            make_unit(),
            make_record(),
        )

        with self.assertRaises(FreightNotFoundError):
            RemoveFreightVehicleRecord(factory).execute(12)

    def test_rejects_non_pending_freight(self) -> None:
        for status in (
            FreightStatus.IN_PROGRESS,
            FreightStatus.COMPLETED,
            FreightStatus.CANCELLED,
        ):
            with self.subTest(status=status):
                factory = FakeUnitOfWorkFactory(
                    make_freight(status),
                    make_unit(),
                    make_record(),
                )

                with self.assertRaises(InvalidFreightStateError):
                    RemoveFreightVehicleRecord(factory).execute(12)

    def test_rejects_unit_without_vehicle(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit(),
            None,
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "não possui veículo operacional",
        ):
            RemoveFreightVehicleRecord(factory).execute(12)


if __name__ == "__main__":
    unittest.main()
