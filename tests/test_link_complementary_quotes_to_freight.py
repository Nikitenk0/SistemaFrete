import unittest
from decimal import Decimal

from application.exceptions import (
    InvalidFreightDataError,
    QuoteNotFoundError
)
from application.use_cases.link_complementary_quotes_to_freight import (
    LinkComplementaryQuotesToFreight
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

    def __init__(
        self,
        freight: Freight | None
    ):
        self.freight = freight

    def get_by_id(
        self,
        freight_id: int
    ) -> Freight | None:
        if (
            self.freight is not None
            and self.freight.freight_id == freight_id
        ):
            return self.freight

        return None


class FakeQuoteRepository:

    def __init__(
        self,
        primary: Quote | None,
        complementaries: tuple[Quote, ...]
    ):
        self.primary = primary
        self.complementaries = complementaries
        self.saved: list[Quote] = []

    def get_by_id_for_update(
        self,
        quote_id: int
    ) -> Quote | None:
        if (
            self.primary is not None
            and self.primary.quote_id == quote_id
        ):
            return self.primary

        return None

    def list_by_primary_quote_id_for_update(
        self,
        primary_quote_id: int
    ) -> tuple[Quote, ...]:
        return tuple(
            quote
            for quote in self.complementaries
            if quote.primary_quote_id == primary_quote_id
        )

    def save(
        self,
        quote: Quote
    ) -> Quote:
        self.saved.append(quote)
        self.complementaries = tuple(
            quote
            if item.quote_id == quote.quote_id
            else item
            for item in self.complementaries
        )
        return quote


class FakeFreightUnitOfWork:

    def __init__(
        self,
        primary: Quote | None,
        complementaries: tuple[Quote, ...],
        freight: Freight | None
    ):
        self.quotes = FakeQuoteRepository(
            primary,
            complementaries
        )
        self.freights = FakeFreightRepository(
            freight
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
        primary: Quote | None,
        complementaries: tuple[Quote, ...],
        freight: Freight | None
    ):
        self.primary = primary
        self.complementaries = complementaries
        self.freight = freight
        self.created: list[FakeFreightUnitOfWork] = []

    def create(self) -> FakeFreightUnitOfWork:
        unit_of_work = FakeFreightUnitOfWork(
            self.primary,
            self.complementaries,
            self.freight
        )
        self.created.append(unit_of_work)
        return unit_of_work


def make_version(
    quote_id: int,
    version_id: int,
    contracted: bool = False
) -> QuoteVersion:
    return QuoteVersion(
        quote_version_id=version_id,
        quote_id=quote_id,
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
        contracted_price=(
            Decimal("1500")
            if contracted
            else None
        )
    )


def make_primary(
    freight_id: int | None = 77
) -> Quote:
    return Quote(
        quote_id=1,
        quote_number="ORC-2026-00001",
        customer_id=5,
        quote_type=QuoteType.PRIMARY,
        current_status=QuoteStatus.APPROVED,
        freight_id=freight_id,
        approved_version_id=10,
        versions=(
            make_version(
                1,
                10,
                contracted=True
            ),
        )
    )


def make_complementary(
    freight_id: int | None = None,
    customer_id: int = 5
) -> Quote:
    return Quote(
        quote_id=2,
        quote_number="ORC-2026-00002",
        customer_id=customer_id,
        quote_type=QuoteType.COMPLEMENTARY,
        primary_quote_id=1,
        current_status=QuoteStatus.DRAFT,
        freight_id=freight_id,
        versions=(
            make_version(
                2,
                20
            ),
        )
    )


def make_freight() -> Freight:
    return Freight(
        freight_id=77,
        customer_id=5,
        primary_quote_id=1
    )


class TestLinkComplementaryQuotesToFreight(
    unittest.TestCase
):

    def test_links_unlinked_complementary(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            make_primary(),
            (
                make_complementary(),
            ),
            make_freight()
        )

        result = LinkComplementaryQuotesToFreight(
            factory
        ).execute(
            primary_quote_id=1
        )

        unit_of_work = factory.created[-1]

        self.assertEqual(
            result[0].freight_id,
            77
        )
        self.assertEqual(
            unit_of_work.quotes.saved[0].freight_id,
            77
        )
        self.assertTrue(
            unit_of_work.committed
        )

    def test_is_idempotent_when_already_linked(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            make_primary(),
            (
                make_complementary(
                    freight_id=77
                ),
            ),
            make_freight()
        )

        result = LinkComplementaryQuotesToFreight(
            factory
        ).execute(
            primary_quote_id=1
        )

        unit_of_work = factory.created[-1]

        self.assertEqual(
            result[0].freight_id,
            77
        )
        self.assertEqual(
            unit_of_work.quotes.saved,
            []
        )
        self.assertTrue(
            unit_of_work.committed
        )

    def test_rejects_primary_without_freight(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            make_primary(
                freight_id=None
            ),
            (
                make_complementary(),
            ),
            None
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            LinkComplementaryQuotesToFreight(
                factory
            ).execute(
                primary_quote_id=1
            )

    def test_rejects_complementary_from_other_freight(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            make_primary(),
            (
                make_complementary(
                    freight_id=88
                ),
            ),
            make_freight()
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            LinkComplementaryQuotesToFreight(
                factory
            ).execute(
                primary_quote_id=1
            )

    def test_rejects_missing_primary_quote(
        self
    ):
        factory = FakeFreightUnitOfWorkFactory(
            None,
            (),
            None
        )

        with self.assertRaises(
            QuoteNotFoundError
        ):
            LinkComplementaryQuotesToFreight(
                factory
            ).execute(
                primary_quote_id=1
            )


if __name__ == "__main__":
    unittest.main()
