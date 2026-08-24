import unittest
from dataclasses import replace
from decimal import Decimal

from domain.models.customer import (
    CustomerPersonType
)
from domain.models.quote import (
    Quote,
    QuoteStatus
)
from domain.models.quote_event import (
    QuoteEvent,
    QuoteEventType
)
from domain.models.quote_version import (
    QuoteVersion
)
from domain.quote_audit import (
    validate_persisted_quote_version_update,
    validate_quote_audit_consistency
)


def make_offered_version(
    contracted: bool = False
) -> QuoteVersion:

    return QuoteVersion(
        quote_version_id=10,
        quote_id=1,
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
        origin="São Paulo/São Paulo",
        destination="Campinas/São Paulo",
        bp02=Decimal("1000"),
        tax_rate=Decimal("0.20"),
        calculated_price=Decimal("1510"),
        rounded_price=Decimal("1500"),
        offered_price=Decimal("1500"),
        offered_margin_value=Decimal("200"),
        offered_margin_rate=Decimal("0.20"),
        contracted_price=(
            Decimal("1500")
            if contracted
            else None
        ),
        contracted_margin_value=(
            Decimal("200")
            if contracted
            else None
        ),
        contracted_margin_rate=(
            Decimal("0.20")
            if contracted
            else None
        ),
        validity_days_snapshot=7
    )


def make_approved_quote() -> Quote:

    version = make_offered_version(
        contracted=True
    )

    events = (
        QuoteEvent(
            quote_event_id=1,
            quote_id=1,
            event_type=QuoteEventType.CREATED,
            new_status=QuoteStatus.DRAFT
        ),
        QuoteEvent(
            quote_event_id=2,
            quote_id=1,
            quote_version_id=10,
            event_type=QuoteEventType.CALCULATED,
            previous_status=QuoteStatus.DRAFT,
            new_status=QuoteStatus.CALCULATED
        ),
        QuoteEvent(
            quote_event_id=3,
            quote_id=1,
            quote_version_id=10,
            event_type=QuoteEventType.OFFERED,
            previous_status=QuoteStatus.CALCULATED,
            new_status=QuoteStatus.OFFERED,
            new_amount=Decimal("1500")
        ),
        QuoteEvent(
            quote_event_id=4,
            quote_id=1,
            quote_version_id=10,
            event_type=(
                QuoteEventType.NEGOTIATION_STARTED
            ),
            previous_status=QuoteStatus.OFFERED,
            new_status=QuoteStatus.NEGOTIATION,
            new_amount=Decimal("1500")
        ),
        QuoteEvent(
            quote_event_id=5,
            quote_id=1,
            quote_version_id=10,
            event_type=QuoteEventType.APPROVED,
            previous_status=QuoteStatus.NEGOTIATION,
            new_status=QuoteStatus.APPROVED,
            new_amount=Decimal("1500")
        )
    )

    return Quote(
        quote_id=1,
        quote_number="ORC-2026-00001",
        customer_id=1,
        current_status=QuoteStatus.APPROVED,
        approved_version_id=10,
        versions=(version,),
        events=events
    )


class TestQuoteAudit(unittest.TestCase):

    def test_offered_version_rejects_core_change(
        self
    ):

        persisted = make_offered_version()
        proposed = replace(
            persisted,
            origin="Santos/São Paulo"
        )

        with self.assertRaises(ValueError):
            validate_persisted_quote_version_update(
                persisted,
                proposed
            )

    def test_offered_version_allows_first_contracting(
        self
    ):

        persisted = make_offered_version()
        proposed = replace(
            persisted,
            contracted_price=Decimal("1400"),
            contracted_margin_value=Decimal("120"),
            contracted_margin_rate=Decimal("0.12")
        )

        validate_persisted_quote_version_update(
            persisted,
            proposed
        )

    def test_approved_version_rejects_contract_change(
        self
    ):

        persisted = make_offered_version(
            contracted=True
        )
        proposed = replace(
            persisted,
            contracted_price=Decimal("1400"),
            contracted_margin_value=Decimal("120"),
            contracted_margin_rate=Decimal("0.12")
        )

        with self.assertRaises(ValueError):
            validate_persisted_quote_version_update(
                persisted,
                proposed
            )

    def test_accepts_consistent_approved_history(
        self
    ):

        validate_quote_audit_consistency(
            make_approved_quote()
        )

    def test_rejects_current_status_divergent_from_history(
        self
    ):

        quote = make_approved_quote()

        tampered = replace(
            quote,
            current_status=QuoteStatus.APPROVED,
            events=quote.events[:-1]
        )

        with self.assertRaises(ValueError):
            validate_quote_audit_consistency(
                tampered
            )


if __name__ == "__main__":
    unittest.main()
