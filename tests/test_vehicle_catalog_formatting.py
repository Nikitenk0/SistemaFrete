import unittest

from domain.models.vehicle import VehicleStatus, VehicleType
from presentation.desktop.vehicle_catalog_formatting import (
    VEHICLE_STATUS_OPTIONS,
    VEHICLE_TYPE_OPTIONS,
    format_vehicle_plate,
    vehicle_status_label,
    vehicle_type_label,
)


class VehicleCatalogFormattingTests(unittest.TestCase):

    def test_status_options(self):
        self.assertIsNone(VEHICLE_STATUS_OPTIONS["Todos"])
        self.assertEqual(VEHICLE_STATUS_OPTIONS["Ativos"], VehicleStatus.ACTIVE)
        self.assertEqual(VEHICLE_STATUS_OPTIONS["Inativos"], VehicleStatus.INACTIVE)

    def test_type_options_have_all_types(self):
        values = {value for value in VEHICLE_TYPE_OPTIONS.values() if value is not None}
        self.assertEqual(values, set(VehicleType))

    def test_status_labels(self):
        self.assertEqual(vehicle_status_label(VehicleStatus.ACTIVE), "Ativo")
        self.assertEqual(vehicle_status_label(VehicleStatus.INACTIVE), "Inativo")

    def test_type_labels(self):
        self.assertEqual(vehicle_type_label(VehicleType.CAMINHAO_3_4), "Caminhão 3/4")
        self.assertEqual(vehicle_type_label(VehicleType.CARRETA_LS), "Carreta LS")
        self.assertEqual(
            vehicle_type_label(VehicleType.CARRETA_VANDERLEIA),
            "Carreta Vanderleia",
        )

    def test_plate_format(self):
        self.assertEqual(format_vehicle_plate("abc1d23"), "ABC-1D23")
        self.assertEqual(format_vehicle_plate("ABC-1D23"), "ABC-1D23")

    def test_invalid_plate_display_is_preserved(self):
        self.assertEqual(format_vehicle_plate("ABC"), "ABC")


if __name__ == "__main__":
    unittest.main()
