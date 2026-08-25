import unittest
from dataclasses import replace
from datetime import datetime, timezone

from application.exceptions import (
    InvalidVehicleDataError,
    VehicleAlreadyExistsError,
    VehicleNotFoundError
)
from application.use_cases.create_vehicle import CreateVehicle
from application.use_cases.get_vehicle import GetVehicle
from application.use_cases.search_vehicles import SearchVehicles
from application.use_cases.update_vehicle import UpdateVehicle
from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType
)


class FakeVehicleRepository:

    def __init__(
        self,
        vehicles: tuple[Vehicle, ...] = ()
    ):
        self.vehicles = list(vehicles)
        self.next_id = max(
            (
                vehicle.vehicle_id or 0
                for vehicle in self.vehicles
            ),
            default=0
        ) + 1

    def add(self, vehicle: Vehicle) -> Vehicle:
        created = replace(
            vehicle,
            vehicle_id=self.next_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.next_id += 1
        self.vehicles.append(created)
        return created

    def save(self, vehicle: Vehicle) -> Vehicle:
        for index, current in enumerate(self.vehicles):
            if current.vehicle_id == vehicle.vehicle_id:
                self.vehicles[index] = vehicle
                return vehicle
        raise RuntimeError("vehicle not found")

    def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        return next(
            (
                vehicle
                for vehicle in self.vehicles
                if vehicle.vehicle_id == vehicle_id
            ),
            None
        )

    def get_by_id_for_update(
        self,
        vehicle_id: int
    ) -> Vehicle | None:
        return self.get_by_id(vehicle_id)

    def get_by_plate(self, plate: str) -> Vehicle | None:
        compact = "".join(
            character
            for character in plate.upper()
            if character not in {"-", " "}
        )
        return next(
            (
                vehicle
                for vehicle in self.vehicles
                if vehicle.plate == compact
            ),
            None
        )

    def search(
        self,
        query: str = "",
        status: VehicleStatus | None = None,
        vehicle_type: VehicleType | None = None,
        limit: int = 100
    ) -> tuple[Vehicle, ...]:
        query = query.strip().upper()
        items = self.vehicles
        if query:
            items = [
                vehicle
                for vehicle in items
                if query.replace("-", "").replace(" ", "")
                in vehicle.plate
                or query in vehicle.vehicle_type.value
            ]
        if status is not None:
            items = [
                vehicle
                for vehicle in items
                if vehicle.status == status
            ]
        if vehicle_type is not None:
            items = [
                vehicle
                for vehicle in items
                if vehicle.vehicle_type == vehicle_type
            ]
        return tuple(items[:limit])


class FakeVehicleUnitOfWork:

    def __init__(self, repository: FakeVehicleRepository):
        self.vehicles = repository
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


class FakeVehicleUnitOfWorkFactory:

    def __init__(
        self,
        vehicles: tuple[Vehicle, ...] = ()
    ):
        self.repository = FakeVehicleRepository(vehicles)
        self.created: list[FakeVehicleUnitOfWork] = []

    def create(self) -> FakeVehicleUnitOfWork:
        uow = FakeVehicleUnitOfWork(self.repository)
        self.created.append(uow)
        return uow


def make_vehicle(
    vehicle_id: int,
    plate: str,
    vehicle_type: VehicleType = VehicleType.TRUCK,
    status: VehicleStatus = VehicleStatus.ACTIVE
) -> Vehicle:
    now = datetime.now(timezone.utc)
    return Vehicle(
        vehicle_id=vehicle_id,
        plate=plate,
        vehicle_type=vehicle_type,
        status=status,
        created_at=now,
        updated_at=now
    )


class VehicleUseCaseTests(unittest.TestCase):

    def test_create_vehicle(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory()
        result = CreateVehicle(factory).execute(
            plate="abc-1d23",
            vehicle_type=VehicleType.TRUCK,
            created_by=9
        )
        self.assertEqual(result.plate, "ABC1D23")
        self.assertEqual(result.vehicle_id, 1)
        self.assertTrue(factory.created[-1].committed)

    def test_create_rejects_duplicate_plate(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory(
            (make_vehicle(1, "ABC1D23"),)
        )
        with self.assertRaises(VehicleAlreadyExistsError):
            CreateVehicle(factory).execute(
                plate="abc-1d23",
                vehicle_type=VehicleType.TOCO
            )

    def test_create_rejects_invalid_data(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory()
        with self.assertRaises(InvalidVehicleDataError):
            CreateVehicle(factory).execute(
                plate="123",
                vehicle_type=VehicleType.TRUCK
            )

    def test_get_vehicle(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory(
            (make_vehicle(5, "ABC1D23"),)
        )
        result = GetVehicle(factory).execute(5)
        self.assertEqual(result.vehicle_id, 5)

    def test_get_rejects_missing_vehicle(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory()
        with self.assertRaises(VehicleNotFoundError):
            GetVehicle(factory).execute(5)

    def test_get_rejects_invalid_id(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory()
        with self.assertRaises(InvalidVehicleDataError):
            GetVehicle(factory).execute(0)

    def test_search_all(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory(
            (
                make_vehicle(1, "ABC1D23"),
                make_vehicle(2, "DEF4G56"),
            )
        )
        result = SearchVehicles(factory).execute()
        self.assertEqual(len(result), 2)

    def test_search_filters_status_and_type(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory(
            (
                make_vehicle(
                    1,
                    "ABC1D23",
                    VehicleType.TRUCK,
                    VehicleStatus.ACTIVE
                ),
                make_vehicle(
                    2,
                    "DEF4G56",
                    VehicleType.TOCO,
                    VehicleStatus.INACTIVE
                ),
            )
        )
        result = SearchVehicles(factory).execute(
            status=VehicleStatus.INACTIVE,
            vehicle_type=VehicleType.TOCO
        )
        self.assertEqual(
            tuple(vehicle.vehicle_id for vehicle in result),
            (2,)
        )

    def test_search_rejects_invalid_limit(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory()
        with self.assertRaises(InvalidVehicleDataError):
            SearchVehicles(factory).execute(limit=0)

    def test_update_vehicle(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory(
            (make_vehicle(3, "ABC1D23"),)
        )
        result = UpdateVehicle(factory).execute(
            vehicle_id=3,
            plate="xyz-9h87",
            vehicle_type=VehicleType.CARRETA,
            status=VehicleStatus.INACTIVE,
            updated_by=7
        )
        self.assertEqual(result.plate, "XYZ9H87")
        self.assertEqual(result.vehicle_type, VehicleType.CARRETA)
        self.assertEqual(result.status, VehicleStatus.INACTIVE)
        self.assertEqual(result.updated_by, 7)
        self.assertTrue(factory.created[-1].committed)

    def test_update_rejects_duplicate_plate(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory(
            (
                make_vehicle(1, "ABC1D23"),
                make_vehicle(2, "DEF4G56"),
            )
        )
        with self.assertRaises(VehicleAlreadyExistsError):
            UpdateVehicle(factory).execute(
                vehicle_id=2,
                plate="ABC1D23",
                vehicle_type=VehicleType.TOCO,
                status=VehicleStatus.ACTIVE
            )

    def test_update_rejects_missing_vehicle(self) -> None:
        factory = FakeVehicleUnitOfWorkFactory()
        with self.assertRaises(VehicleNotFoundError):
            UpdateVehicle(factory).execute(
                vehicle_id=99,
                plate="ABC1D23",
                vehicle_type=VehicleType.TRUCK,
                status=VehicleStatus.ACTIVE
            )


if __name__ == "__main__":
    unittest.main()
