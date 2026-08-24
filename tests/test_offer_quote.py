import unittest
from datetime import date
from decimal import Decimal

from application.exceptions import (
    InvalidQuoteDataError
)
from application.use_cases.offer_quote import (
    OfferQuote
)
from domain.models.customer import (
    CustomerPersonType
)
from domain.models.quote import (
    Quote,
    QuoteStatus
)
from domain.models.quote_event import (
    QuoteEventType
)
from domain.models.quote_version import (
    QuoteVersion
)


class FakeQuoteRepository:

    def __init__(
        self,
        quote: Quote
    ):
        self.quote = quote

    def get_by_id_for_update(
        self,
        quote_id: int
    ) -> Quote | None:
        if self.quote.quote_id == quote_id:
            return self.quote
        return None

    def save(
        self,
        quote: Quote
    ) -> Quote:
        self.quote = quote
        return quote


class FakeQuoteUnitOfWork:

    def __init__(
        self,
        repository: FakeQuoteRepository
    ):
        self.quotes = repository
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


class FakeQuoteUnitOfWorkFactory:

    def __init__(
        self,
        repository: FakeQuoteRepository
    ):
        self.repository = repository
        self.created: list[
            FakeQuoteUnitOfWork
        ] = []

    def create(
        self
    ) -> FakeQuoteUnitOfWork:
        unit_of_work = FakeQuoteUnitOfWork(
            self.repository
        )
        self.created.append(
            unit_of_work
        )
        return unit_of_work


def make_calculated_quote() -> Quote:

    version = QuoteVersion(
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
        bp02=Decimal("1000"),
        tax_rate=Decimal("0.20"),
        calculated_price=Decimal("1500"),
        rounded_price=Decimal("1500")
    )

    return Quote(
        quote_id=1,
        quote_number="ORC-2026-00001",
        customer_id=1,
        current_status=(
            QuoteStatus.CALCULATED
        ),
        versions=(
            version,
        )
    )


class TestOfferQuote(unittest.TestCase):

    def test_offers_standard_price(
        self
    ):

        repository = FakeQuoteRepository(
            make_calculated_quote()
        )
        factory = FakeQuoteUnitOfWorkFactory(
            repository
        )

        result = OfferQuote(
            factory
        ).execute(
            quote_id=1,
            validity_days=7,
            user_id=5
        )

        version = result.versions[0]

        self.assertEqual(
            result.current_status,
            QuoteStatus.OFFERED
        )
        self.assertEqual(
            version.offered_price,
            Decimal("1500")
        )
        self.assertEqual(
            version.offered_margin_value,
            Decimal("200.00")
        )
        self.assertEqual(
            version.offered_margin_rate,
            Decimal("0.20")
        )
        self.assertEqual(
            version.validity_days_snapshot,
            7
        )
        self.assertIsInstance(
            version.valid_until,
            date
        )
        self.assertEqual(
            result.events[-1].event_type,
            QuoteEventType.OFFERED
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_manual_price_requires_reason_and_audits_change(
        self
    ):

        repository = FakeQuoteRepository(
            make_calculated_quote()
        )
        factory = FakeQuoteUnitOfWorkFactory(
            repository
        )

        with self.assertRaises(
            InvalidQuoteDataError
        ):
            OfferQuote(
                factory
            ).execute(
                quote_id=1,
                validity_days=7,
                offered_price=Decimal("1450")
            )

        result = OfferQuote(
            factory
        ).execute(
            quote_id=1,
            validity_days=7,
            offered_price=Decimal("1450"),
            price_change_reason=(
                "Negociação comercial"
            )
        )

        self.assertEqual(
            result.events[-2].event_type,
            QuoteEventType.PRICE_CHANGED
        )
        self.assertEqual(
            result.events[-2].previous_amount,
            Decimal("1500")
        )
        self.assertEqual(
            result.events[-2].new_amount,
            Decimal("1450")
        )
        self.assertEqual(
            result.events[-1].event_type,
            QuoteEventType.OFFERED
        )


if __name__ == "__main__":
    unittest.main()
