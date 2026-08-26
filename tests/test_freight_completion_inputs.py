import unittest
from decimal import Decimal
from types import SimpleNamespace

from domain.models.freight import FreightStatus
from presentation.desktop.freight_completion_inputs import (
    can_complete_freight,
    completion_readiness_message,
    is_freight_completion_phase,
)


def assignment(
    *,
    active: bool,
    amount=Decimal("500.00"),
):
    return SimpleNamespace(
        is_active=active,
        ended_at=None if active else object(),
        actual_driver_amount=(
            None if active else amount
        ),
    )


def unit(
    *,
    position: int = 1,
    vehicle=True,
    assignments=(),
):
    return SimpleNamespace(
        position=position,
        vehicle=object() if vehicle else None,
        driver_assignments=tuple(assignments),
    )


def details(
    *,
    status=FreightStatus.IN_PROGRESS,
    units=(),
):
    return SimpleNamespace(
        current_status=status,
        transport_units=tuple(units),
    )


class FreightCompletionInputsTests(
    unittest.TestCase
):

    def test_completion_phase_only_in_progress(self):
        self.assertTrue(
            is_freight_completion_phase(
                FreightStatus.IN_PROGRESS
            )
        )
        self.assertFalse(
            is_freight_completion_phase(
                FreightStatus.PENDING
            )
        )

    def test_rejects_active_operational_assignment(self):
        current = details(
            units=(
                unit(
                    assignments=(
                        assignment(active=True),
                    )
                ),
            )
        )

        self.assertFalse(
            can_complete_freight(current)
        )
        self.assertIn(
            "encerre o conjunto operacional atual",
            completion_readiness_message(current),
        )

    def test_accepts_finished_assignments_with_vehicle(self):
        current = details(
            units=(
                unit(
                    assignments=(
                        assignment(active=False),
                        assignment(
                            active=False,
                            amount=Decimal("700.00"),
                        ),
                    )
                ),
            )
        )

        self.assertTrue(
            can_complete_freight(current)
        )
        self.assertIn(
            "pronto para conclusão",
            completion_readiness_message(current),
        )

    def test_rejects_missing_vehicle(self):
        current = details(
            units=(
                unit(
                    vehicle=False,
                    assignments=(
                        assignment(active=False),
                    ),
                ),
            )
        )

        self.assertFalse(
            can_complete_freight(current)
        )
        self.assertIn(
            "informe o veículo",
            completion_readiness_message(current),
        )


if __name__ == "__main__":
    unittest.main()
