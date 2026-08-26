import unittest
from datetime import datetime, timezone

from application.dtos.freight_query import (
    FreightDriverAssignmentDetails,
    FreightOperationalAssignmentDetails,
    FreightTransportUnitDetails,
)
from domain.models.freight import FreightStatus
from domain.models.vehicle import VehicleType
from presentation.desktop.freight_operational_context_rules import (
    active_operational_context,
    can_adopt_current_operational_context,
    can_replace_current_operational_context,
)


NOW = datetime(
    2026,
    8,
    26,
    16,
    0,
    tzinfo=timezone.utc,
)


def make_context():
    return FreightOperationalAssignmentDetails(
        freight_operational_assignment_id=1,
        transport_provider_id=2,
        vehicle_id=3,
        provider_name_snapshot="Exemplo 123",
        provider_tax_document_snapshot="12345678000190",
        driver_name_snapshot="Joao",
        driver_cpf_snapshot="12345678901",
        vehicle_plate_snapshot="ABC1D23",
        vehicle_type_snapshot=VehicleType.TRUCK,
        created_at=NOW,
    )


class FreightOperationalContextRulesTests(
    unittest.TestCase
):

    def test_returns_context_from_active_assignment(self):
        context = make_context()
        unit = FreightTransportUnitDetails(
            freight_transport_unit_id=25,
            position=1,
            vehicle=None,
            driver_assignments=(
                FreightDriverAssignmentDetails(
                    freight_driver_assignment_id=10,
                    driver_id=11,
                    driver_name="Joao",
                    started_at=NOW,
                    ended_at=None,
                    actual_driver_amount=None,
                    operational_context=context,
                ),
            ),
        )

        self.assertEqual(
            active_operational_context(unit),
            context,
        )

    def test_can_replace_recognized_context_in_progress(self):
        self.assertTrue(
            can_replace_current_operational_context(
                status=FreightStatus.IN_PROGRESS,
                active_context=make_context(),
            )
        )

    def test_cannot_replace_without_recognized_context(self):
        self.assertFalse(
            can_replace_current_operational_context(
                status=FreightStatus.IN_PROGRESS,
                active_context=None,
            )
        )

    def test_cannot_replace_pending_context(self):
        self.assertFalse(
            can_replace_current_operational_context(
                status=FreightStatus.PENDING,
                active_context=make_context(),
            )
        )

    def test_adopt_rule_still_allows_legacy_in_progress_pair(self):
        self.assertTrue(
            can_adopt_current_operational_context(
                status=FreightStatus.IN_PROGRESS,
                has_vehicle=True,
                has_active_driver=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
