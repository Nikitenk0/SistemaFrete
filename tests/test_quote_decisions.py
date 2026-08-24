import unittest
from decimal import Decimal

from application.exceptions import (
    InvalidQuoteDataError,
    InvalidQuoteStateError
)
from application.use_cases.approve_quote import (
    ApproveQuote
)
from application.use_cases.cancel_quote import (
    CancelQuote
)
from application.use_cases.reject_quote import (
    RejectQuote
)
from application.use_cases.start_quote_negotiation import (
    StartQuoteNegotiation
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


def make_offered_version() -> QuoteVersion:

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
        bp02=Decimal("1000"),
        tax_rate=Decimal("0.20"),
        calculated_price=Decimal("1510"),
        rounded_price=Decimal("1500"),
        offered_price=Decimal("1500"),
        offered_margin_value=Decimal("200"),
        offered_margin_rate=Decimal("0.20"),
        validity_days_snapshot=7
    )


def make_quote(
    status: QuoteStatus
) -> Quote:

    return Quote(
        quote_id=1,
        quote_number="ORC-2026-00001",
        customer_id=1,
        current_status=status,
        versions=(
            make_offered_version(),
        )
    )


class TestQuoteDecisions(unittest.TestCase):

    def test_starts_negotiation_from_offer(
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

        result = StartQuoteNegotiation(
            factory
        ).execute(
            quote_id=1,
            observation="Cliente solicitou negociação",
            user_id=7
        )

        self.assertEqual(
            result.current_status,
            QuoteStatus.NEGOTIATION
        )
        self.assertEqual(
            result.events[-1].event_type,
            QuoteEventType.NEGOTIATION_STARTED
        )
        self.assertEqual(
            result.events[-1].previous_status,
            QuoteStatus.OFFERED
        )
        self.assertEqual(
            result.events[-1].new_status,
            QuoteStatus.NEGOTIATION
        )
        self.assertEqual(
            result.events[-1].quote_version_id,
            10
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_approval_requires_negotiation(
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
            ApproveQuote(
                factory
            ).execute(
                quote_id=1,
                contracted_price=(
                    Decimal("1500")
                )
            )

    def test_approves_with_contracted_price(
        self
    ):

        repository = FakeQuoteRepository(
            make_quote(
                QuoteStatus.NEGOTIATION
            )
        )
        factory = FakeQuoteUnitOfWorkFactory(
            repository
        )

        result = ApproveQuote(
            factory
        ).execute(
            quote_id=1,
            contracted_price=Decimal("1500"),
            acceptance_observation=(
                "Aceite confirmado pelo cliente"
            ),
            user_id=8
        )

        version = result.versions[0]

        self.assertEqual(
            result.current_status,
            QuoteStatus.APPROVED
        )
        self.assertEqual(
            result.approved_version_id,
            10
        )
        self.assertEqual(
            version.contracted_price,
            Decimal("1500")
        )
        self.assertEqual(
            version.contracted_margin_value,
            Decimal("200.00")
        )
        self.assertEqual(
            version.contracted_margin_rate,
            Decimal("0.20")
        )
        self.assertEqual(
            result.events[-1].event_type,
            QuoteEventType.APPROVED
        )
        self.assertEqual(
            result.events[-1].new_amount,
            Decimal("1500")
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_contracted_price_change_requires_reason_and_is_audited(
        self
    ):

        repository = FakeQuoteRepository(
            make_quote(
                QuoteStatus.NEGOTIATION
            )
        )
        factory = FakeQuoteUnitOfWorkFactory(
            repository
        )

        with self.assertRaises(
            InvalidQuoteDataError
        ):
            ApproveQuote(
                factory
            ).execute(
                quote_id=1,
                contracted_price=(
                    Decimal("1400")
                )
            )

        result = ApproveQuote(
            factory
        ).execute(
            quote_id=1,
            contracted_price=Decimal("1400"),
            price_change_reason=(
                "Condição final negociada"
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
            Decimal("1400")
        )
        self.assertEqual(
            result.events[-1].event_type,
            QuoteEventType.APPROVED
        )

    def test_rejects_with_structured_reason_code(
        self
    ):

        repository = FakeQuoteRepository(
            make_quote(
                QuoteStatus.NEGOTIATION
            )
        )
        factory = FakeQuoteUnitOfWorkFactory(
            repository
        )

        result = RejectQuote(
            factory
        ).execute(
            quote_id=1,
            reason_code="preco",
            observation=(
                "Cliente recusou o valor final"
            ),
            user_id=9
        )

        self.assertEqual(
            result.current_status,
            QuoteStatus.REJECTED
        )
        self.assertEqual(
            result.events[-1].event_type,
            QuoteEventType.REJECTED
        )
        self.assertEqual(
            result.events[-1].reason_code,
            "PRECO"
        )
        self.assertEqual(
            result.events[-1].new_status,
            QuoteStatus.REJECTED
        )

    def test_rejection_requires_valid_reason_code(
        self
    ):

        repository = FakeQuoteRepository(
            make_quote(
                QuoteStatus.NEGOTIATION
            )
        )
        factory = FakeQuoteUnitOfWorkFactory(
            repository
        )

        with self.assertRaises(
            InvalidQuoteDataError
        ):
            RejectQuote(
                factory
            ).execute(
                quote_id=1,
                reason_code=" "
            )

    def test_cancels_active_quote_and_blocks_terminal_quote(
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

        result = CancelQuote(
            factory
        ).execute(
            quote_id=1,
            reason="Solicitação do cliente"
        )

        self.assertEqual(
            result.current_status,
            QuoteStatus.CANCELLED
        )
        self.assertEqual(
            result.events[-1].event_type,
            QuoteEventType.CANCELLED
        )

        with self.assertRaises(
            InvalidQuoteStateError
        ):
            CancelQuote(
                factory
            ).execute(
                quote_id=1,
                reason="Nova tentativa"
            )


if __name__ == "__main__":
    unittest.main()
