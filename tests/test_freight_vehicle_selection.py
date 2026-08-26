import unittest

from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType,
)
from presentation.desktop.freight_vehicle_selection import (
    build_freight_vehicle_selection,
)


class FreightVehicleSelectionTests(
    unittest.TestCase
):

    def test_builds_snapshot_selection_from_active_master_vehicle(
        self,
    ):
        vehicle = Vehicle(
            vehicle_id=10,
            plate="ABC1D23",
            vehicle_type=VehicleType.TRUCK,
            status=VehicleStatus.ACTIVE,
        )

        vehicle_type, plate = (
            build_freight_vehicle_selection(
                vehicle
            )
        )

        self.assertEqual(
            vehicle_type,
            VehicleType.TRUCK,
        )
        self.assertEqual(
            plate,
            "ABC1D23",
        )

    def test_rejects_inactive_master_vehicle(
        self,
    ):
        vehicle = Vehicle(
            vehicle_id=10,
            plate="ABC1D23",
            vehicle_type=VehicleType.TRUCK,
            status=VehicleStatus.INACTIVE,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Somente veículo ativo",
        ):
            build_freight_vehicle_selection(
                vehicle
            )

    def test_rejects_vehicle_without_master_id(
        self,
    ):
        vehicle = Vehicle(
            plate="ABC1D23",
            vehicle_type=VehicleType.TRUCK,
            status=VehicleStatus.ACTIVE,
        )

        with self.assertRaisesRegex(
            ValueError,
            "precisa estar cadastrado",
        ):
            build_freight_vehicle_selection(
                vehicle
            )


if __name__ == "__main__":
    unittest.main()
