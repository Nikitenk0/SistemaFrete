import unittest
from datetime import datetime, timezone

from application.exceptions import (
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError,
)
from application.use_cases.remove_freight_transport_unit import (
    RemoveFreightTransportUnit,
)
from domain.models.freight import Freight, FreightStatus
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment,
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit,
)
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType,
)


NOW = datetime(2026, 8, 25, 20, 0, tzinfo=timezone.utc)


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

    def __init__(self, units):
        self.units = list(units)
        self.deleted_ids = []

    def get_by_id(self, unit_id):
        return next(
            (
                unit
                for unit in self.units
                if unit.freight_transport_unit_id == unit_id
            ),
            None,
        )

    def list_by_freight_id(self, freight_id):
        return tuple(
            unit
            for unit in self.units
            if unit.freight_id == freight_id
        )

    def delete_by_id(self, unit_id):
        self.deleted_ids.append(unit_id)
        self.units = [
            unit
            for unit in self.units
            if unit.freight_transport_unit_id != unit_id
        ]


class FakeVehicleRepository:

    def __init__(self, vehicle=None):
        self.vehicle = vehicle

    def get_by_transport_unit_id(self, unit_id):
        if (
            self.vehicle is not None
            and self.vehicle.freight_transport_unit_id == unit_id
        ):
            return self.vehicle
        return None


class FakeAssignmentRepository:

    def __init__(self, assignments=()):
        self.assignments = tuple(assignments)

    def list_by_transport_unit_id(self, unit_id):
        return tuple(
            assignment
            for assignment in self.assignments
            if assignment.freight_transport_unit_id == unit_id
        )


class FakeUnitOfWork:

    def __init__(
        self,
        freight,
        units,
        vehicle=None,
        assignments=(),
    ):
        self.freights = FakeFreightRepository(freight)
        self.transport_units = FakeTransportUnitRepository(units)
        self.vehicle_records = FakeVehicleRepository(vehicle)
        self.driver_assignments = FakeAssignmentRepository(assignments)
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

    def __init__(self, unit_of_work):
        self.unit_of_work = unit_of_work

    def create(self):
        return self.unit_of_work


def make_freight(status=FreightStatus.PENDING):
    return Freight(
        freight_id=77,
        customer_id=5,
        primary_quote_id=1,
        current_status=status,
        started_at=(NOW if status == FreightStatus.IN_PROGRESS else None),
    )


def make_unit(position):
    return FreightTransportUnit(
        freight_transport_unit_id=100 + position,
        freight_id=77,
        position=position,
    )


def make_vehicle(unit_id):
    return FreightVehicleRecord(
        freight_transport_unit_id=unit_id,
        vehicle_type=FreightVehicleType.TRUCK,
        plate="ABC1D23",
        axle_count=3,
        pallet_capacity_min=16,
        pallet_capacity_max=20,
        payload_capacity_kg=12500,
        freight_vehicle_record_id=501,
    )


def make_assignment(unit_id):
    return FreightDriverAssignment(
        freight_transport_unit_id=unit_id,
        driver_id=9,
        started_at=NOW,
        freight_driver_assignment_id=701,
    )


class RemoveFreightTransportUnitTests(unittest.TestCase):

    def test_removes_last_empty_unit_from_pending_freight(self):
        units = (make_unit(1), make_unit(2))
        uow = FakeUnitOfWork(make_freight(), units)

        RemoveFreightTransportUnit(
            FakeFactory(uow)
        ).execute(102)

        self.assertEqual(uow.transport_units.deleted_ids, [102])
        self.assertTrue(uow.committed)

    def test_rejects_removing_unit_that_is_not_last(self):
        uow = FakeUnitOfWork(
            make_freight(),
            (make_unit(1), make_unit(2)),
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "última unidade",
        ):
            RemoveFreightTransportUnit(
                FakeFactory(uow)
            ).execute(101)

    def test_rejects_unit_with_vehicle(self):
        unit = make_unit(1)
        uow = FakeUnitOfWork(
            make_freight(),
            (unit,),
            vehicle=make_vehicle(101),
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "veículo operacional",
        ):
            RemoveFreightTransportUnit(
                FakeFactory(uow)
            ).execute(101)

    def test_rejects_unit_with_driver_assignment(self):
        unit = make_unit(1)
        uow = FakeUnitOfWork(
            make_freight(),
            (unit,),
            assignments=(make_assignment(101),),
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "participação de motorista",
        ):
            RemoveFreightTransportUnit(
                FakeFactory(uow)
            ).execute(101)

    def test_rejects_non_pending_freight(self):
        uow = FakeUnitOfWork(
            make_freight(FreightStatus.IN_PROGRESS),
            (make_unit(1),),
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Somente frete pendente",
        ):
            RemoveFreightTransportUnit(
                FakeFactory(uow)
            ).execute(101)

    def test_rejects_missing_unit(self):
        uow = FakeUnitOfWork(make_freight(), ())

        with self.assertRaises(
            FreightTransportUnitNotFoundError
        ):
            RemoveFreightTransportUnit(
                FakeFactory(uow)
            ).execute(999)

    def test_rejects_missing_freight(self):
        uow = FakeUnitOfWork(None, (make_unit(1),))

        with self.assertRaises(FreightNotFoundError):
            RemoveFreightTransportUnit(
                FakeFactory(uow)
            ).execute(101)

    def test_rejects_invalid_id(self):
        uow = FakeUnitOfWork(make_freight(), ())

        with self.assertRaises(InvalidFreightDataError):
            RemoveFreightTransportUnit(
                FakeFactory(uow)
            ).execute(0)


if __name__ == "__main__":
    unittest.main()
