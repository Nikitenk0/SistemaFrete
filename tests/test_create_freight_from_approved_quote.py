import unittest
from decimal import Decimal

from application.exceptions import (
    FreightAlreadyExistsError,
    InvalidFreightDataError,
    QuoteNotFoundError
)
from application.use_cases.create_freight_from_approved_quote import (
    CreateFreightFromApprovedQuote
)
from domain.models.customer import (
    CustomerPersonType
)
from domain.models.freight import (
    Freight
)
from domain.models.quote import (
    Quote,
    QuoteStatus,
    QuoteType
)
from domain.models.quote_version import (
    QuoteVersion
)


class FakeFreightRepository:

    def __init__(self):
        self.added: Freight | None = None

    def add(
        self,
        freight: Freight
    ) -> Freight:
        self.added = freight
        return Freight(
            freight_id=77,
            customer_id=freight.customer_id,
            primary_quote_id=(
                freight.primary_quote_id
            ),
            created_at=freight.created_at,
            created_by=freight.created_by
        )


class FakeQuoteRepository:

    def __init__(
        self,
        quote: Quote | None
    ):
        self.quote = quote
        self.saved: Quote | None = None

    def get_by_id_for_update(
        self,
        quote_id: int
    ) -> Quote | None:
        if (
            self.quote is not None
            and self.quote.quote_id == quote_id
        ):
            return self.quote

        return None

    def save(
        self,
        quote: Quote
    ) -> Quote:
        self.saved = quote
        self.quote = quote
        return quote


class FakeFreightUnitOfWork:

    def __init__(
        self,
        quote: Quote | None
    ):
        self.freights = FakeFreightRepository()
        self.quotes = FakeQuoteRepository(
            quote
        )
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


class FakeFreightUnitOfWorkFactory:

    def __init__(
        self,
        quote: Quote | None
    ):
        self.quote = quote
        self.created: list[
            FakeFreightUnitOfWork
        ] = []

    def create(
        self
    ) -> FakeFreightUnitOfWork:
        unit_of_work = FakeFreightUnitOfWork(
            self.quote
        )
        self.created.append(
            unit_of_work
        )
        return unit_of_work


def make_version(
    contracted_price: Decimal | None = Decimal("1500")
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
        contracted_price=contracted_price
    )


def make_quote(
    status: QuoteStatus = QuoteStatus.APPROVED,
    quote_type: QuoteType = QuoteType.PRIMARY,
    freight_id: int | None = None
) -> Quote:

    approved = status == QuoteStatus.APPROVED

    return Quote(
        quote_id=1,
        quote_number="ORC-2026-00001",
        customer_id=5,
        quote_type=quote_type,
        primary_quote_id=(
            99
            if quote_type == QuoteType.COMPLEMENTARY
            else None
        ),
        current_status=status,
        freight_id=freight_id,
        approved_version_id=(
            10
            if approved
            else None
        ),
        versions=(
            make_version(
                Decimal("1500")
                if approved
                else None
            ),
        )
    )


class TestCreateFreightFromApprovedQuote(
    unittest.TestCase
):

    def test_creates_freight_and_links_primary_quote(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            make_quote()
        )

        result = CreateFreightFromApprovedQuote(
            factory
        ).execute(
            primary_quote_id=1,
            created_by=9
        )

        unit_of_work = factory.created[-1]

        self.assertEqual(
            result.freight_id,
            77
        )
        self.assertEqual(
            result.customer_id,
            5
        )
        self.assertEqual(
            result.primary_quote_id,
            1
        )
        self.assertEqual(
            result.created_by,
            9
        )
        self.assertEqual(
            unit_of_work.quotes.saved.freight_id,
            77
        )
        self.assertTrue(
            unit_of_work.committed
        )

    def test_rejects_missing_primary_quote(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            None
        )

        with self.assertRaises(
            QuoteNotFoundError
        ):
            CreateFreightFromApprovedQuote(
                factory
            ).execute(
                primary_quote_id=1
            )

    def test_rejects_complementary_quote(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            make_quote(
                quote_type=(
                    QuoteType.COMPLEMENTARY
                )
            )
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            CreateFreightFromApprovedQuote(
                factory
            ).execute(
                primary_quote_id=1
            )

    def test_rejects_non_approved_primary_quote(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            make_quote(
                status=QuoteStatus.OFFERED
            )
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            CreateFreightFromApprovedQuote(
                factory
            ).execute(
                primary_quote_id=1
            )

    def test_rejects_primary_quote_already_linked(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            make_quote(
                freight_id=88
            )
        )

        with self.assertRaises(
            FreightAlreadyExistsError
        ):
            CreateFreightFromApprovedQuote(
                factory
            ).execute(
                primary_quote_id=1
            )


if __name__ == "__main__":
    unittest.main()
