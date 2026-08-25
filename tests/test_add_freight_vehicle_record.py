import unittest
from dataclasses import replace
from datetime import datetime, timezone

from application.exceptions import (
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.use_cases.add_freight_vehicle_record import (
    AddFreightVehicleRecord
)
from domain.models.freight import (
    Freight,
    FreightStatus
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit
)
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType
)


class FakeFreightRepository:

    def __init__(self, freight: Freight | None):
        self.freight = freight

    def get_by_id_for_update(
        self,
        freight_id: int
    ) -> Freight | None:
        if (
            self.freight is not None
            and self.freight.freight_id == freight_id
        ):
            return self.freight
        return None


class FakeTransportUnitRepository:

    def __init__(self, unit: FreightTransportUnit | None):
        self.unit = unit

    def get_by_id(
        self,
        freight_transport_unit_id: int
    ) -> FreightTransportUnit | None:
        if (
            self.unit is not None
            and self.unit.freight_transport_unit_id
            == freight_transport_unit_id
        ):
            return self.unit
        return None


class FakeVehicleRecordRepository:

    def __init__(
        self,
        record: FreightVehicleRecord | None = None
    ):
        self.record = record
        self.added: FreightVehicleRecord | None = None

    def add(
        self,
        vehicle_record: FreightVehicleRecord
    ) -> FreightVehicleRecord:
        created = replace(
            vehicle_record,
            freight_vehicle_record_id=101
        )
        self.added = created
        self.record = created
        return created

    def get_by_transport_unit_id(
        self,
        freight_transport_unit_id: int
    ) -> FreightVehicleRecord | None:
        if (
            self.record is not None
            and self.record.freight_transport_unit_id
            == freight_transport_unit_id
        ):
            return self.record
        return None


class FakeUnitOfWork:

    def __init__(
        self,
        freight: Freight | None,
        unit: FreightTransportUnit | None,
        record: FreightVehicleRecord | None = None
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
        record: FreightVehicleRecord | None = None
    ):
        self.freight = freight
        self.unit = unit
        self.record = record
        self.created: list[FakeUnitOfWork] = []

    def create(self) -> FakeUnitOfWork:
        uow = FakeUnitOfWork(
            self.freight,
            self.unit,
            self.record
        )
        self.created.append(uow)
        return uow


def make_freight(
    status: FreightStatus = FreightStatus.PENDING
) -> Freight:
    now = datetime.now(timezone.utc)

    return Freight(
        freight_id=77,
        customer_id=5,
        primary_quote_id=1,
        current_status=status,
        started_at=(
            now
            if status
            in {FreightStatus.IN_PROGRESS, FreightStatus.COMPLETED}
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


def make_unit() -> FreightTransportUnit:
    return FreightTransportUnit(
        freight_transport_unit_id=12,
        freight_id=77,
        position=1
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
        payload_capacity_kg=6500
    )


class AddFreightVehicleRecordTests(
    unittest.TestCase
):

    def test_adds_caminhao_3_4_to_pending_freight(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit()
        )

        result = AddFreightVehicleRecord(factory).execute(
            freight_transport_unit_id=12,
            vehicle_type=FreightVehicleType.CAMINHAO_3_4,
            plate="abc-1d23",
            created_by=9
        )

        self.assertEqual(result.freight_vehicle_record_id, 101)
        self.assertEqual(result.plate, "ABC1D23")
        self.assertEqual(result.axle_count, 2)
        self.assertEqual(result.pallet_capacity_min, 8)
        self.assertEqual(result.pallet_capacity_max, 8)
        self.assertEqual(result.payload_capacity_kg, 3500)
        self.assertTrue(factory.created[-1].committed)

    def test_copies_truck_capacity_range(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit()
        )

        result = AddFreightVehicleRecord(factory).execute(
            12,
            FreightVehicleType.TRUCK,
            "DEF5G67"
        )

        self.assertEqual(result.axle_count, 3)
        self.assertEqual(result.pallet_capacity_min, 16)
        self.assertEqual(result.pallet_capacity_max, 20)
        self.assertEqual(result.payload_capacity_kg, 12500)

    def test_copies_bitruck_capacity_range(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit()
        )

        result = AddFreightVehicleRecord(factory).execute(
            12,
            FreightVehicleType.BITRUCK,
            "DEF5G67"
        )

        self.assertEqual(result.axle_count, 4)
        self.assertEqual(result.pallet_capacity_min, 16)
        self.assertEqual(result.pallet_capacity_max, 18)
        self.assertEqual(result.payload_capacity_kg, 17000)

    def test_adds_vehicle_while_freight_is_in_progress(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(FreightStatus.IN_PROGRESS),
            make_unit()
        )

        result = AddFreightVehicleRecord(factory).execute(
            12,
            FreightVehicleType.CARRETA_LS,
            "DEF5G67"
        )

        self.assertEqual(
            result.vehicle_type,
            FreightVehicleType.CARRETA_LS
        )
        self.assertEqual(result.payload_capacity_kg, 30000)

    def test_rejects_second_vehicle_for_same_transport_unit(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit(),
            make_record()
        )

        with self.assertRaises(InvalidFreightStateError):
            AddFreightVehicleRecord(factory).execute(
                12,
                FreightVehicleType.TRUCK,
                "DEF5G67"
            )

    def test_rejects_completed_freight(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(FreightStatus.COMPLETED),
            make_unit()
        )

        with self.assertRaises(InvalidFreightStateError):
            AddFreightVehicleRecord(factory).execute(
                12,
                FreightVehicleType.CARRETA,
                "DEF5G67"
            )

    def test_rejects_cancelled_freight(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(FreightStatus.CANCELLED),
            make_unit()
        )

        with self.assertRaises(InvalidFreightStateError):
            AddFreightVehicleRecord(factory).execute(
                12,
                FreightVehicleType.CARRETA,
                "DEF5G67"
            )

    def test_rejects_missing_transport_unit(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            None
        )

        with self.assertRaises(
            FreightTransportUnitNotFoundError
        ):
            AddFreightVehicleRecord(factory).execute(
                12,
                FreightVehicleType.TOCO,
                "DEF5G67"
            )

    def test_rejects_missing_freight(self) -> None:
        factory = FakeUnitOfWorkFactory(
            None,
            make_unit()
        )

        with self.assertRaises(FreightNotFoundError):
            AddFreightVehicleRecord(factory).execute(
                12,
                FreightVehicleType.TOCO,
                "DEF5G67"
            )

    def test_wraps_invalid_vehicle_type(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit()
        )

        with self.assertRaises(InvalidFreightDataError):
            AddFreightVehicleRecord(factory).execute(
                12,
                "TRACTOR",
                "DEF5G67"
            )

    def test_wraps_invalid_plate(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit()
        )

        with self.assertRaises(InvalidFreightDataError):
            AddFreightVehicleRecord(factory).execute(
                12,
                FreightVehicleType.TOCO,
                "ABC123"
            )

    def test_rejects_invalid_created_by(self) -> None:
        factory = FakeUnitOfWorkFactory(
            make_freight(),
            make_unit()
        )

        with self.assertRaises(InvalidFreightDataError):
            AddFreightVehicleRecord(factory).execute(
                12,
                FreightVehicleType.TOCO,
                "ABC1234",
                created_by=0
            )


if __name__ == "__main__":
    unittest.main()
