import unittest
from dataclasses import replace

from application.exceptions import InvalidFreightStateError
from application.use_cases.add_freight_vehicle_record import AddFreightVehicleRecord
from domain.models.freight import Freight, FreightStatus
from domain.models.freight_transport_unit import FreightTransportUnit
from domain.models.freight_vehicle_record import FreightVehicleRecord
from domain.models.vehicle import Vehicle, VehicleStatus, VehicleType


class Repo:
    def __init__(self, value=None):
        self.value = value
    def get_by_id(self, _id):
        return self.value
    def get_by_id_for_update(self, _id):
        return self.value


class VehicleRecords:
    def __init__(self, active=None):
        self.active = active
        self.added = None
    def get_by_transport_unit_id(self, _id):
        return None
    def get_active_by_master_vehicle(
        self, vehicle_id, plate, exclude_transport_unit_id=None
    ):
        return self.active
    def add(self, record):
        self.added = replace(record, freight_vehicle_record_id=90)
        return self.added


class Uow:
    def __init__(self, active=None):
        self.freights = Repo(Freight(
            freight_id=1, customer_id=1, primary_quote_id=1,
            current_status=FreightStatus.PENDING,
        ))
        self.transport_units = Repo(FreightTransportUnit(
            freight_transport_unit_id=5, freight_id=1, position=1,
        ))
        self.vehicles = Repo(Vehicle(
            vehicle_id=7, plate="ABC1D23", vehicle_type=VehicleType.TRUCK,
            status=VehicleStatus.ACTIVE,
        ))
        self.vehicle_records = VehicleRecords(active)
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


class AddMasterVehicleToFreightTests(unittest.TestCase):
    def test_copies_master_vehicle_into_operational_snapshot(self):
        uow = Uow()
        result = AddFreightVehicleRecord(Factory(uow)).execute(
            freight_transport_unit_id=5, vehicle_id=7
        )
        self.assertEqual(result.vehicle_id, 7)
        self.assertEqual(result.plate, "ABC1D23")
        self.assertEqual(result.vehicle_type, VehicleType.TRUCK)
        self.assertEqual(result.payload_capacity_kg, 12500)
        self.assertTrue(uow.committed)

    def test_rejects_master_vehicle_already_in_active_unit(self):
        active = FreightVehicleRecord(
            freight_vehicle_record_id=1,
            freight_transport_unit_id=99,
            vehicle_id=7,
            vehicle_type=VehicleType.TRUCK,
            plate="ABC1D23",
            axle_count=3,
            pallet_capacity_min=16,
            pallet_capacity_max=20,
            payload_capacity_kg=12500,
        )
        uow = Uow(active=active)
        with self.assertRaisesRegex(
            InvalidFreightStateError, "outra unidade operacional ativa"
        ):
            AddFreightVehicleRecord(Factory(uow)).execute(
                freight_transport_unit_id=5, vehicle_id=7
            )


if __name__ == "__main__":
    unittest.main()
