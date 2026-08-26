import unittest
from datetime import datetime, timezone

from application.dtos.freight_query import (
    FreightOperationalAssignmentDetails,
)
from domain.models.freight import FreightStatus
from domain.models.vehicle import VehicleType
from presentation.desktop.freight_operational_context_rules import (
    can_finish_current_operational_context,
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
        provider_name_snapshot="Exemplo 456",
        provider_tax_document_snapshot="98765432000110",
        driver_name_snapshot="Carlos",
        driver_cpf_snapshot="98765432100",
        vehicle_plate_snapshot="DEF2E34",
        vehicle_type_snapshot=VehicleType.TRUCK,
        created_at=NOW,
    )


class FreightFinishOperationalContextRuleTests(
    unittest.TestCase
):

    def test_allows_finish_in_progress_with_active_context(self):
        self.assertTrue(
            can_finish_current_operational_context(
                status=FreightStatus.IN_PROGRESS,
                active_context=make_context(),
                has_active_driver=True,
            )
        )

    def test_rejects_without_active_context(self):
        self.assertFalse(
            can_finish_current_operational_context(
                status=FreightStatus.IN_PROGRESS,
                active_context=None,
                has_active_driver=True,
            )
        )

    def test_rejects_without_active_driver(self):
        self.assertFalse(
            can_finish_current_operational_context(
                status=FreightStatus.IN_PROGRESS,
                active_context=make_context(),
                has_active_driver=False,
            )
        )

    def test_rejects_pending(self):
        self.assertFalse(
            can_finish_current_operational_context(
                status=FreightStatus.PENDING,
                active_context=make_context(),
                has_active_driver=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
