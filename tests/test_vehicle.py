import unittest

from domain.models.freight_vehicle_record import (
    FreightVehicleType
)
from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType,
    normalize_vehicle_plate
)


class VehicleTests(unittest.TestCase):

    def test_normalizes_plate(self) -> None:
        vehicle = Vehicle(
            plate="abc-1d23",
            vehicle_type=VehicleType.TRUCK
        )
        self.assertEqual(vehicle.plate, "ABC1D23")

    def test_rejects_invalid_plate(self) -> None:
        with self.assertRaises(ValueError):
            Vehicle(
                plate="ABC123",
                vehicle_type=VehicleType.TRUCK
            )

    def test_normalize_vehicle_plate(self) -> None:
        self.assertEqual(
            normalize_vehicle_plate(" abc 1d23 "),
            "ABC1D23"
        )

    def test_defaults_to_active(self) -> None:
        vehicle = Vehicle(
            plate="ABC1D23",
            vehicle_type=VehicleType.TOCO
        )
        self.assertEqual(
            vehicle.status,
            VehicleStatus.ACTIVE
        )

    def test_accepts_inactive(self) -> None:
        vehicle = Vehicle(
            plate="ABC1D23",
            vehicle_type=VehicleType.CARRETA,
            status=VehicleStatus.INACTIVE
        )
        self.assertEqual(
            vehicle.status,
            VehicleStatus.INACTIVE
        )

    def test_rejects_invalid_optional_id(self) -> None:
        with self.assertRaises(ValueError):
            Vehicle(
                plate="ABC1D23",
                vehicle_type=VehicleType.TRUCK,
                vehicle_id=0
            )

    def test_freight_vehicle_type_remains_compatible(self) -> None:
        self.assertIs(
            FreightVehicleType,
            VehicleType
        )
        self.assertEqual(
            FreightVehicleType.TRUCK,
            VehicleType.TRUCK
        )


if __name__ == "__main__":
    unittest.main()
