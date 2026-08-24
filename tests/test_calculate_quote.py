import unittest
from dataclasses import replace
from decimal import Decimal

from application.exceptions import (
    InvalidQuoteStateError
)
from application.use_cases.calculate_quote import (
    CalculateQuote
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
        self.quote = quote
        return quote


class FakeQuoteUnitOfWork:

    def __init__(
        self,
        repository: FakeQuoteRepository
    ):
        self.quotes = repository
        self.committed = False

    def __enter__(
        self
    ):
        return self

    def __exit__(
        self,
        *_args
    ):
        return None

    def commit(
        self
    ) -> None:
        self.committed = True

    def rollback(
        self
    ) -> None:
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
            calculated_price=Decimal("1500"),
            rounded_price=Decimal("1500")
        )


def make_quote(
    status: QuoteStatus = QuoteStatus.DRAFT
) -> Quote:

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
        origin="São Paulo/São Paulo",
        destination="Campinas/São Paulo",
        invoice_value=Decimal("100000"),
        transport_compositions=(
            QuoteTransportComposition(
                quote_transport_composition_id=20,
                quote_version_id=10,
                position=1,
                axle_count=6
            ),
        )
    )

    return Quote(
        quote_id=1,
        quote_number="ORC-2026-00001",
        customer_id=1,
        current_status=status,
        versions=(
            version,
        )
    )


class TestCalculateQuote(unittest.TestCase):

    def test_calculates_and_persists_status_and_event(
        self
    ):

        repository = FakeQuoteRepository(
            make_quote()
        )
        factory = FakeQuoteUnitOfWorkFactory(
            repository
        )

        result = CalculateQuote(
            quote_unit_of_work_factory=factory,
            quote_version_calculator=(
                FakeQuoteVersionCalculator()
            )
        ).execute(
            quote_id=1,
            user_id=7
        )

        self.assertEqual(
            result.current_status,
            QuoteStatus.CALCULATED
        )
        self.assertEqual(
            result.versions[0].calculated_price,
            Decimal("1500")
        )
        self.assertEqual(
            result.events[-1].event_type,
            QuoteEventType.CALCULATED
        )
        self.assertEqual(
            result.events[-1].quote_version_id,
            10
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_rejects_calculation_after_offer(
        self
    ):

        repository = FakeQuoteRepository(
            make_quote(
                QuoteStatus.OFFERED
            )
        )
        factory = FakeQuoteUnitOfWorkFactory(
            repository
        )

        with self.assertRaises(
            InvalidQuoteStateError
        ):
            CalculateQuote(
                quote_unit_of_work_factory=factory,
                quote_version_calculator=(
                    FakeQuoteVersionCalculator()
                )
            ).execute(
                quote_id=1
            )


if __name__ == "__main__":
    unittest.main()
