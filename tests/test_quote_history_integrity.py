import unittest

from dataclasses import replace
from datetime import date
from decimal import Decimal

from domain.models.customer import (
    CustomerPersonType
)
from domain.models.quote import (
    QuoteStatus
)
from domain.models.quote_event import (
    QuoteEvent,
    QuoteEventType
)
from domain.models.quote_version import (
    QuoteVersion
)
from domain.quote_history_integrity import (
    validate_persisted_event_unchanged,
    validate_persisted_quote_state_update,
    validate_persisted_version_update
)


class QuoteHistoryIntegrityTests(
    unittest.TestCase
):

    @staticmethod
    def _version(
        **changes
    ) -> QuoteVersion:

        base = QuoteVersion(
            version_number=1,
            customer_person_type_snapshot=(
                CustomerPersonType.COMPANY
            ),
            customer_document_snapshot=(
                "12345678000195"
            ),
            customer_legal_name_snapshot=(
                "Cliente Teste Ltda."
            ),
            invoice_value=Decimal("100000"),
            bp02=Decimal("5000"),
            tax_rate=Decimal("0.20"),
            calculated_price=Decimal("6250"),
            rounded_price=Decimal("6250"),
            quote_version_id=10,
            quote_id=1
        )

        return replace(
            base,
            **changes
        )

    def test_calculated_version_can_change_before_offer(
        self
    ) -> None:

        persisted = self._version()
        candidate = replace(
            persisted,
            invoice_value=Decimal("120000")
        )

        validate_persisted_version_update(
            persisted,
            candidate
        )

    def test_offered_version_rejects_commercial_change(
        self
    ) -> None:

        persisted = self._version(
            offered_price=Decimal("6250"),
            offered_margin_value=Decimal("100"),
            offered_margin_rate=Decimal("0.02"),
            validity_days_snapshot=7,
            valid_until=date(2026, 8, 31)
        )

        candidate = replace(
            persisted,
            invoice_value=Decimal("120000")
        )

        with self.assertRaises(ValueError):
            validate_persisted_version_update(
                persisted,
                candidate
            )

    def test_offered_version_accepts_contract_fields_once(
        self
    ) -> None:

        persisted = self._version(
            offered_price=Decimal("6250"),
            offered_margin_value=Decimal("100"),
            offered_margin_rate=Decimal("0.02")
        )

        candidate = replace(
            persisted,
            contracted_price=Decimal("6200"),
            contracted_margin_value=Decimal("-40"),
            contracted_margin_rate=Decimal("-0.008")
        )

        validate_persisted_version_update(
            persisted,
            candidate
        )

    def test_contract_fields_must_be_defined_together(
        self
    ) -> None:

        persisted = self._version(
            offered_price=Decimal("6250"),
            offered_margin_value=Decimal("100"),
            offered_margin_rate=Decimal("0.02")
        )

        candidate = replace(
            persisted,
            contracted_price=Decimal("6200")
        )

        with self.assertRaises(ValueError):
            validate_persisted_version_update(
                persisted,
                candidate
            )

    def test_approved_version_is_fully_frozen(
        self
    ) -> None:

        persisted = self._version(
            offered_price=Decimal("6250"),
            contracted_price=Decimal("6200"),
            contracted_margin_value=Decimal("-40"),
            contracted_margin_rate=Decimal("-0.008")
        )

        candidate = replace(
            persisted,
            contracted_price=Decimal("6100")
        )

        with self.assertRaises(ValueError):
            validate_persisted_version_update(
                persisted,
                candidate
            )

    def test_terminal_status_cannot_change(
        self
    ) -> None:

        with self.assertRaises(ValueError):
            validate_persisted_quote_state_update(
                persisted_status=QuoteStatus.APPROVED,
                persisted_approved_version_id=10,
                candidate_status=QuoteStatus.CANCELLED,
                candidate_approved_version_id=None
            )

    def test_event_is_append_only_and_immutable(
        self
    ) -> None:

        persisted = QuoteEvent(
            event_type=QuoteEventType.OFFERED,
            quote_event_id=20,
            quote_id=1,
            quote_version_id=10,
            previous_status=QuoteStatus.CALCULATED,
            new_status=QuoteStatus.OFFERED,
            new_amount=Decimal("6250")
        )

        candidate = replace(
            persisted,
            new_amount=Decimal("6200")
        )

        with self.assertRaises(ValueError):
            validate_persisted_event_unchanged(
                persisted,
                candidate
            )


if __name__ == "__main__":
    unittest.main()
