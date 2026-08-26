import unittest

from domain.models.freight_operational_assignment import (
    FreightOperationalAssignment,
)
from domain.models.vehicle import VehicleType


class FreightOperationalAssignmentDomainTests(
    unittest.TestCase
):

    def test_normalizes_snapshot_identity(self):
        item = FreightOperationalAssignment(
            freight_driver_assignment_id=1,
            transport_provider_id=2,
            vehicle_id=3,
            provider_name_snapshot=" Exemplo 123 ",
            provider_tax_document_snapshot="12.345.678/0001-90",
            driver_name_snapshot=" João ",
            driver_cpf_snapshot="123.456.789-01",
            vehicle_plate_snapshot="abc-1d23",
            vehicle_type_snapshot=VehicleType.TRUCK,
        )

        self.assertEqual(
            item.provider_name_snapshot,
            "Exemplo 123",
        )
        self.assertEqual(
            item.provider_tax_document_snapshot,
            "12345678000190",
        )
        self.assertEqual(
            item.driver_cpf_snapshot,
            "12345678901",
        )
        self.assertEqual(
            item.vehicle_plate_snapshot,
            "ABC1D23",
        )


if __name__ == "__main__":
    unittest.main()
