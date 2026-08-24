import unittest
from dataclasses import replace
from decimal import Decimal

from application.use_cases.revise_quote import (
    ReviseQuote
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
from domain.models.quote_transport_composition import (
    QuoteTransportComposition
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
        self.next_version_id = 20

    def get_by_id(
        self,
        quote_id: int
    ) -> Quote | None:
        if self.quote.quote_id == quote_id:
            return self.quote
        return None

    def get_by_id_for_update(
        self,
        quote_id: int
    ) -> Quote | None:
        return self.get_by_id(
            quote_id
        )

    def save(
        self,
        quote: Quote
    ) -> Quote:

        versions = []

        for version in quote.versions:
            if version.quote_version_id is None:
                version = replace(
                    version,
                    quote_version_id=(
                        self.next_version_id
                    ),
                    quote_id=quote.quote_id
                )
                self.next_version_id += 1

            versions.append(
                version
            )

        self.quote = replace(
            quote,
            versions=tuple(versions)
        )

        return self.quote


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


class FakeQuoteVersionCalculator:

    def execute(
        self,
        version: QuoteVersion
    ) -> QuoteVersion:
        return replace(
            version,
            driver_amount=Decimal("1000"),
            toll_amount=Decimal("100"),
            bp02=Decimal("1200"),
            tax_rate=Decimal("0.20"),
            calculated_price=Decimal("1800"),
            rounded_price=Decimal("1800")
        )


def make_offered_quote() -> Quote:

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
        modality="ClosedLoad",
        origin="São Paulo/São Paulo",
        destination="Campinas/São Paulo",
        invoice_value=Decimal("100000"),
        transport_compositions=(
            QuoteTransportComposition(
                quote_transport_composition_id=30,
                quote_version_id=10,
                position=1,
                axle_count=6,
                distance_km=Decimal("100"),
                driver_amount=Decimal("1000"),
                toll_amount=Decimal("100")
            ),
        ),
        bp02=Decimal("1200"),
        tax_rate=Decimal("0.20"),
        calculated_price=Decimal("1800"),
        rounded_price=Decimal("1800"),
        offered_price=Decimal("1750"),
        offered_margin_value=Decimal("200"),
        offered_margin_rate=Decimal("0.1666666667"),
        validity_days_snapshot=7
    )

    return Quote(
        quote_id=1,
        quote_number="ORC-2026-00001",
        customer_id=1,
        current_status=(
            QuoteStatus.OFFERED
        ),
        versions=(
            version,
        )
    )


class TestReviseQuote(unittest.TestCase):

    def test_creates_new_calculated_version_without_overwriting_offer(
        self
    ):

        repository = FakeQuoteRepository(
            make_offered_quote()
        )
        factory = FakeQuoteUnitOfWorkFactory(
            repository
        )

        result = ReviseQuote(
            quote_unit_of_work_factory=factory,
            quote_version_calculator=(
                FakeQuoteVersionCalculator()
            )
        ).execute(
            quote_id=1,
            reason="Nova condição comercial",
            user_id=9
        )

        self.assertEqual(
            result.current_status,
            QuoteStatus.CALCULATED
        )
        self.assertEqual(
            len(result.versions),
            2
        )

        version_1 = result.versions[0]
        version_2 = result.versions[1]

        self.assertEqual(
            version_1.offered_price,
            Decimal("1750")
        )
        self.assertEqual(
            version_2.version_number,
            2
        )
        self.assertIsNone(
            version_2.offered_price
        )
        self.assertEqual(
            version_2.calculated_price,
            Decimal("1800")
        )
        self.assertEqual(
            version_2.transport_compositions[0].axle_count,
            6
        )
        self.assertEqual(
            result.events[-1].event_type,
            QuoteEventType.CALCULATED
        )
        self.assertEqual(
            result.events[-1].previous_status,
            QuoteStatus.OFFERED
        )
        self.assertEqual(
            result.events[-1].new_status,
            QuoteStatus.CALCULATED
        )
        self.assertEqual(
            result.events[-1].quote_version_id,
            version_2.quote_version_id
        )
        self.assertEqual(
            result.events[-1].observation,
            "Nova condição comercial"
        )
        self.assertTrue(
            factory.created[-1].committed
        )


if __name__ == "__main__":
    unittest.main()
