import unittest

from domain.models.freight_transport_unit import (
    FreightTransportUnit
)


class FreightTransportUnitDomainTests(
    unittest.TestCase
):

    def test_creates_transport_unit_identity(
        self
    ) -> None:
        unit = FreightTransportUnit(
            freight_id=10,
            position=1,
            created_by=7
        )

        self.assertEqual(
            unit.freight_id,
            10
        )
        self.assertEqual(
            unit.position,
            1
        )
        self.assertEqual(
            unit.created_by,
            7
        )
        self.assertIsNone(
            unit.freight_transport_unit_id
        )

    def test_rejects_invalid_freight_id(
        self
    ) -> None:
        with self.assertRaises(ValueError):
            FreightTransportUnit(
                freight_id=0,
                position=1
            )

    def test_rejects_invalid_position(
        self
    ) -> None:
        with self.assertRaises(ValueError):
            FreightTransportUnit(
                freight_id=10,
                position=0
            )

    def test_rejects_invalid_optional_identifiers(
        self
    ) -> None:
        with self.assertRaises(ValueError):
            FreightTransportUnit(
                freight_id=10,
                position=1,
                freight_transport_unit_id=0
            )

        with self.assertRaises(ValueError):
            FreightTransportUnit(
                freight_id=10,
                position=1,
                created_by=0
            )


if __name__ == "__main__":
    unittest.main()
