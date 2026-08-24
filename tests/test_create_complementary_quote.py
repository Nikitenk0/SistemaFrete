import unittest
from decimal import Decimal

from application.exceptions import (
    InvalidQuoteDataError
)
from application.use_cases.create_quote_draft import (
    CreateQuoteDraft
)
from domain.models.customer import (
    Customer,
    CustomerPersonType
)
from domain.models.quote import (
    Quote,
    QuoteStatus,
    QuoteType
)
from domain.models.quote_event import (
    QuoteEventType
)
from domain.models.quote_version import (
    QuoteVersion
)


class FakeCustomerRepository:

    def __init__(
        self,
        customers: tuple[Customer, ...]
    ):
        self._customers = {
            customer.customer_id: customer
            for customer in customers
        }

    def get_by_id(
        self,
        customer_id: int
    ) -> Customer | None:
        return self._customers.get(
            customer_id
        )


class FakeCustomerUnitOfWork:

    def __init__(
        self,
        repository: FakeCustomerRepository
    ):
        self.customers = repository

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


class FakeCustomerUnitOfWorkFactory:

    def __init__(
        self,
        repository: FakeCustomerRepository
    ):
        self.repository = repository

    def create(
        self
    ) -> FakeCustomerUnitOfWork:
        return FakeCustomerUnitOfWork(
            self.repository
        )


class FakeQuoteNumberGenerator:

    def __init__(
        self,
        number: str = "ORC-2026-00002"
    ):
        self.number = number
        self.requested_year: int | None = None

    def next_number(
        self,
        year: int
    ) -> str:
        self.requested_year = year
        return self.number


class FakeQuoteRepository:

    def __init__(
        self,
        quotes: tuple[Quote, ...]
    ):
        self._quotes = {
            quote.quote_id: quote
            for quote in quotes
            if quote.quote_id is not None
        }
        self.added_quote: Quote | None = None

    def get_by_id(
        self,
        quote_id: int
    ) -> Quote | None:
        return self._quotes.get(
            quote_id
        )

    def add(
        self,
        quote: Quote
    ) -> Quote:
        self.added_quote = quote
        return quote


class FakeQuoteUnitOfWork:

    def __init__(
        self,
        repository: FakeQuoteRepository,
        number_generator: FakeQuoteNumberGenerator
    ):
        self.quotes = repository
        self.quote_numbers = number_generator
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
        repository: FakeQuoteRepository,
        number_generator: FakeQuoteNumberGenerator
    ):
        self.repository = repository
        self.number_generator = number_generator
        self.created: list[
            FakeQuoteUnitOfWork
        ] = []

    def create(
        self
    ) -> FakeQuoteUnitOfWork:
        unit_of_work = FakeQuoteUnitOfWork(
            self.repository,
            self.number_generator
        )
        self.created.append(
            unit_of_work
        )
        return unit_of_work


def make_customer(
    customer_id: int,
    document: str
) -> Customer:
    return Customer(
        customer_id=customer_id,
        person_type=CustomerPersonType.COMPANY,
        document=document,
        legal_name=f"Cliente {customer_id} Ltda."
    )


def make_version(
    quote_id: int,
    quote_version_id: int,
    contracted_price: Decimal | None = None
) -> QuoteVersion:
    return QuoteVersion(
        quote_version_id=quote_version_id,
        quote_id=quote_id,
        version_number=1,
        customer_person_type_snapshot=(
            CustomerPersonType.COMPANY
        ),
        customer_document_snapshot=(
            "12345678000195"
        ),
        customer_legal_name_snapshot=(
            "Cliente 1 Ltda."
        ),
        contracted_price=contracted_price
    )


def make_primary_quote(
    status: QuoteStatus = QuoteStatus.APPROVED,
    customer_id: int = 1,
    freight_id: int | None = 77
) -> Quote:
    version = make_version(
        quote_id=1,
        quote_version_id=10,
        contracted_price=(
            Decimal("1500")
            if status == QuoteStatus.APPROVED
            else None
        )
    )

    return Quote(
        quote_id=1,
        quote_number="ORC-2026-00001",
        customer_id=customer_id,
        quote_type=QuoteType.PRIMARY,
        current_status=status,
        freight_id=freight_id,
        approved_version_id=(
            10
            if status == QuoteStatus.APPROVED
            else None
        ),
        versions=(
            version,
        )
    )


def make_complementary_quote() -> Quote:
    version = make_version(
        quote_id=2,
        quote_version_id=20,
        contracted_price=Decimal("200")
    )

    return Quote(
        quote_id=2,
        quote_number="ORC-2026-00002",
        customer_id=1,
        quote_type=QuoteType.COMPLEMENTARY,
        primary_quote_id=1,
        current_status=QuoteStatus.APPROVED,
        approved_version_id=20,
        versions=(
            version,
        )
    )


class TestCreateComplementaryQuote(
    unittest.TestCase
):

    def setUp(self) -> None:
        self.customer_1 = make_customer(
            1,
            "12345678000195"
        )
        self.customer_2 = make_customer(
            2,
            "98765432000198"
        )

    def _make_use_case(
        self,
        quote: Quote
    ) -> tuple[
        CreateQuoteDraft,
        FakeQuoteUnitOfWorkFactory
    ]:
        customer_repository = (
            FakeCustomerRepository(
                (
                    self.customer_1,
                    self.customer_2
                )
            )
        )
        quote_repository = (
            FakeQuoteRepository(
                (
                    quote,
                )
            )
        )
        number_generator = (
            FakeQuoteNumberGenerator()
        )
        quote_factory = (
            FakeQuoteUnitOfWorkFactory(
                quote_repository,
                number_generator
            )
        )

        use_case = CreateQuoteDraft(
            FakeCustomerUnitOfWorkFactory(
                customer_repository
            ),
            quote_factory
        )

        return (
            use_case,
            quote_factory
        )

    def test_creates_complementary_quote_from_approved_primary(
        self
    ) -> None:
        primary_quote = make_primary_quote()
        use_case, quote_factory = (
            self._make_use_case(
                primary_quote
            )
        )

        result = use_case.execute(
            customer_id=1,
            quote_type=QuoteType.COMPLEMENTARY,
            primary_quote_id=1,
            modality="ClosedLoad",
            origin="São Paulo - SP",
            destination="Campinas - SP",
            invoice_value=Decimal("10000")
        )

        self.assertEqual(
            result.quote_number,
            "ORC-2026-00002"
        )
        self.assertEqual(
            result.quote_type,
            QuoteType.COMPLEMENTARY
        )
        self.assertEqual(
            result.primary_quote_id,
            1
        )
        self.assertEqual(
            result.customer_id,
            primary_quote.customer_id
        )
        self.assertEqual(
            result.freight_id,
            primary_quote.freight_id
        )
        self.assertEqual(
            result.current_status,
            QuoteStatus.DRAFT
        )
        self.assertEqual(
            len(result.versions),
            1
        )
        self.assertEqual(
            result.versions[0].version_number,
            1
        )
        self.assertEqual(
            len(result.events),
            1
        )
        self.assertEqual(
            result.events[0].event_type,
            QuoteEventType.CREATED
        )
        self.assertTrue(
            quote_factory.created[-1].committed
        )

    def test_rejects_complement_without_primary_quote_id(
        self
    ) -> None:
        use_case, _factory = (
            self._make_use_case(
                make_primary_quote()
            )
        )

        with self.assertRaises(
            InvalidQuoteDataError
        ):
            use_case.execute(
                customer_id=1,
                quote_type=(
                    QuoteType.COMPLEMENTARY
                )
            )

    def test_rejects_complement_for_non_approved_primary(
        self
    ) -> None:
        use_case, _factory = (
            self._make_use_case(
                make_primary_quote(
                    status=QuoteStatus.OFFERED
                )
            )
        )

        with self.assertRaises(
            InvalidQuoteDataError
        ):
            use_case.execute(
                customer_id=1,
                quote_type=(
                    QuoteType.COMPLEMENTARY
                ),
                primary_quote_id=1
            )

    def test_rejects_complement_targeting_another_complement(
        self
    ) -> None:
        use_case, _factory = (
            self._make_use_case(
                make_complementary_quote()
            )
        )

        with self.assertRaises(
            InvalidQuoteDataError
        ):
            use_case.execute(
                customer_id=1,
                quote_type=(
                    QuoteType.COMPLEMENTARY
                ),
                primary_quote_id=2
            )

    def test_rejects_complement_with_different_customer(
        self
    ) -> None:
        use_case, _factory = (
            self._make_use_case(
                make_primary_quote(
                    customer_id=1
                )
            )
        )

        with self.assertRaises(
            InvalidQuoteDataError
        ):
            use_case.execute(
                customer_id=2,
                quote_type=(
                    QuoteType.COMPLEMENTARY
                ),
                primary_quote_id=1
            )


if __name__ == "__main__":
    unittest.main()
