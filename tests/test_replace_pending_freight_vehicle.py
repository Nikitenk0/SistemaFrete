import unittest
from dataclasses import replace
from datetime import datetime, timezone

from application.exceptions import InvalidFreightStateError
from application.use_cases.replace_pending_freight_vehicle import (
    ReplacePendingFreightVehicle,
)
from domain.models.freight import Freight, FreightStatus
from domain.models.freight_transport_unit import FreightTransportUnit
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType,
)
from domain.models.vehicle import Vehicle, VehicleStatus, VehicleType


def make_freight(status=FreightStatus.PENDING):
    now = datetime.now(timezone.utc)
    return Freight(
        freight_id=7,
        customer_id=3,
        primary_quote_id=2,
        current_status=status,
        started_at=now if status == FreightStatus.IN_PROGRESS else None,
    )


def make_unit():
    return FreightTransportUnit(
        freight_transport_unit_id=11, freight_id=7, position=1
    )


def make_record(vehicle_id=1, plate="AAA1A11"):
    return FreightVehicleRecord(
        freight_vehicle_record_id=15,
        freight_transport_unit_id=11,
        vehicle_id=vehicle_id,
        vehicle_type=FreightVehicleType.TOCO,
        plate=plate,
        axle_count=2,
        pallet_capacity_min=12,
        pallet_capacity_max=12,
        payload_capacity_kg=6500,
    )


class SimpleRepo:
    def __init__(self, value):
        self.value = value
    def get_by_id(self, _id):
        return self.value
    def get_by_id_for_update(self, _id):
        return self.value


class VehicleRecordRepo:
    def __init__(self, current, active_other=None):
        self.current = current
        self.active_other = active_other
        self.deleted = False
        self.added = None
    def get_by_transport_unit_id(self, _unit_id):
        return self.current
    def get_active_by_master_vehicle(
        self, vehicle_id, plate, exclude_transport_unit_id=None
    ):
        return self.active_other
    def delete_by_transport_unit_id(self, _unit_id):
        self.deleted = True
        self.current = None
    def add(self, record):
        self.added = replace(record, freight_vehicle_record_id=99)
        self.current = self.added
        return self.added


class FakeUow:
    def __init__(self, freight, unit, current, vehicle, active_other=None):
        self.freights = SimpleRepo(freight)
        self.transport_units = SimpleRepo(unit)
        self.vehicle_records = VehicleRecordRepo(current, active_other)
        self.vehicles = SimpleRepo(vehicle)
        self.committed = False
    def __enter__(self):
        return self
    def __exit__(self, *_args):
        return None
    def commit(self):
        self.committed = True
    def rollback(self):
        pass


class Factory:
    def __init__(self, uow):
        self.uow = uow
    def create(self):
        return self.uow


class ReplacePendingFreightVehicleTests(unittest.TestCase):
    def test_replaces_vehicle_atomically_in_pending_freight(self):
        new_vehicle = Vehicle(
            vehicle_id=2,
            plate="BBB2B22",
            vehicle_type=VehicleType.TRUCK,
            status=VehicleStatus.ACTIVE,
        )
        uow = FakeUow(make_freight(), make_unit(), make_record(), new_vehicle)
        result = ReplacePendingFreightVehicle(Factory(uow)).execute(11, 2)
        self.assertTrue(uow.vehicle_records.deleted)
        self.assertTrue(uow.committed)
        self.assertEqual(result.vehicle_id, 2)
        self.assertEqual(result.plate, "BBB2B22")
        self.assertEqual(result.axle_count, 3)

    def test_rejects_vehicle_already_used_elsewhere(self):
        new_vehicle = Vehicle(
            vehicle_id=2, plate="BBB2B22", vehicle_type=VehicleType.TRUCK
        )
        uow = FakeUow(
            make_freight(),
            make_unit(),
            make_record(),
            new_vehicle,
            active_other=make_record(vehicle_id=2, plate="BBB2B22"),
        )
        with self.assertRaisesRegex(
            InvalidFreightStateError, "outra unidade operacional ativa"
        ):
            ReplacePendingFreightVehicle(Factory(uow)).execute(11, 2)

    def test_rejects_same_vehicle(self):
        same_vehicle = Vehicle(
            vehicle_id=1, plate="AAA1A11", vehicle_type=VehicleType.TOCO
        )
        uow = FakeUow(make_freight(), make_unit(), make_record(), same_vehicle)
        with self.assertRaisesRegex(InvalidFreightStateError, "veículo diferente"):
            ReplacePendingFreightVehicle(Factory(uow)).execute(11, 1)

    def test_rejects_non_pending_freight(self):
        vehicle = Vehicle(
            vehicle_id=2, plate="BBB2B22", vehicle_type=VehicleType.TRUCK
        )
        uow = FakeUow(
            make_freight(FreightStatus.IN_PROGRESS),
            make_unit(),
            make_record(),
            vehicle,
        )
        with self.assertRaisesRegex(InvalidFreightStateError, "Somente frete pendente"):
            ReplacePendingFreightVehicle(Factory(uow)).execute(11, 2)


if __name__ == "__main__":
    unittest.main()
