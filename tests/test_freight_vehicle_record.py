import unittest

from domain.models.freight_vehicle_record import (
    FREIGHT_VEHICLE_SPECIFICATIONS,
    FreightVehicleRecord,
    FreightVehicleType,
    get_freight_vehicle_specification
)


class FreightVehicleRecordTests(
    unittest.TestCase
):

    def test_contains_only_approved_vehicle_types(
        self
    ) -> None:
        self.assertEqual(
            set(FreightVehicleType),
            {
                FreightVehicleType.CAMINHAO_3_4,
                FreightVehicleType.TOCO,
                FreightVehicleType.TRUCK,
                FreightVehicleType.BITRUCK,
                FreightVehicleType.CARRETA,
                FreightVehicleType.CARRETA_LS,
                FreightVehicleType.CARRETA_VANDERLEIA,
            }
        )

    def test_vehicle_specifications_match_operational_table(
        self
    ) -> None:
        expected = {
            FreightVehicleType.CAMINHAO_3_4: (2, 8, 8, 3500),
            FreightVehicleType.TOCO: (2, 12, 12, 6500),
            FreightVehicleType.TRUCK: (3, 16, 20, 12500),
            FreightVehicleType.BITRUCK: (4, 16, 18, 17000),
            FreightVehicleType.CARRETA: (5, 28, 28, 26000),
            FreightVehicleType.CARRETA_LS: (6, 28, 28, 30000),
            FreightVehicleType.CARRETA_VANDERLEIA: (6, 30, 30, 35000),
        }

        self.assertEqual(
            set(FREIGHT_VEHICLE_SPECIFICATIONS),
            set(expected)
        )

        for vehicle_type, values in expected.items():
            with self.subTest(vehicle_type=vehicle_type):
                specification = get_freight_vehicle_specification(
                    vehicle_type
                )
                self.assertEqual(
                    (
                        specification.axle_count,
                        specification.pallet_capacity_min,
                        specification.pallet_capacity_max,
                        specification.payload_capacity_kg,
                    ),
                    values
                )

    def test_creates_record_and_normalizes_mercosul_plate(
        self
    ) -> None:
        record = self._make_record(
            vehicle_type=FreightVehicleType.CARRETA_LS,
            plate="abc-1d23",
            axle_count=6,
            pallet_capacity_min=28,
            pallet_capacity_max=28,
            payload_capacity_kg=30000
        )

        self.assertEqual(record.plate, "ABC1D23")
        self.assertEqual(
            record.vehicle_type,
            FreightVehicleType.CARRETA_LS
        )

    def test_accepts_old_brazilian_plate_format(self) -> None:
        record = self._make_record(
            plate="ABC-1234"
        )
        self.assertEqual(record.plate, "ABC1234")

    def test_rejects_invalid_transport_unit_id(self) -> None:
        with self.assertRaises(ValueError):
            self._make_record(
                freight_transport_unit_id=0
            )

    def test_rejects_invalid_vehicle_type(self) -> None:
        with self.assertRaises(ValueError):
            self._make_record(
                vehicle_type="TRACTOR"
            )

    def test_rejects_invalid_plate_length(self) -> None:
        with self.assertRaises(ValueError):
            self._make_record(
                plate="ABC123"
            )

    def test_rejects_invalid_plate_characters(self) -> None:
        with self.assertRaises(ValueError):
            self._make_record(
                plate="ABC@123"
            )

    def test_rejects_invalid_axle_count(self) -> None:
        with self.assertRaises(ValueError):
            self._make_record(
                axle_count=0
            )

    def test_rejects_invalid_pallet_range(self) -> None:
        with self.assertRaises(ValueError):
            self._make_record(
                pallet_capacity_min=20,
                pallet_capacity_max=16
            )

    def test_rejects_invalid_payload_capacity(self) -> None:
        with self.assertRaises(ValueError):
            self._make_record(
                payload_capacity_kg=0
            )

    def test_rejects_invalid_created_by(self) -> None:
        with self.assertRaises(ValueError):
            self._make_record(
                created_by=0
            )

    @staticmethod
    def _make_record(
        freight_transport_unit_id: int = 12,
        vehicle_type: FreightVehicleType = FreightVehicleType.TRUCK,
        plate: str = "ABC1D23",
        axle_count: int = 3,
        pallet_capacity_min: int = 16,
        pallet_capacity_max: int = 20,
        payload_capacity_kg: int = 12500,
        created_by: int | None = None
    ) -> FreightVehicleRecord:
        return FreightVehicleRecord(
            freight_transport_unit_id=freight_transport_unit_id,
            vehicle_type=vehicle_type,
            plate=plate,
            axle_count=axle_count,
            pallet_capacity_min=pallet_capacity_min,
            pallet_capacity_max=pallet_capacity_max,
            payload_capacity_kg=payload_capacity_kg,
            created_by=created_by
        )


if __name__ == "__main__":
    unittest.main()
