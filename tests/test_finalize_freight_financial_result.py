import unittest
from datetime import (
    datetime,
    timezone
)
from decimal import Decimal
from types import SimpleNamespace

from application.exceptions import (
    FreightNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.use_cases.finalize_freight_financial_result import (
    FinalizeFreightFinancialResult
)
from domain.models.freight import (
    FreightStatus
)
from domain.models.quote import (
    QuoteStatus,
    QuoteType
)


NOW = datetime(
    2026,
    8,
    25,
    17,
    50,
    tzinfo=timezone.utc
)


def make_freight(
    status: FreightStatus = FreightStatus.COMPLETED
):
    return SimpleNamespace(
        freight_id=77,
        primary_quote_id=101,
        current_status=status
    )


def make_version(
    version_id: int,
    contracted_price: str,
    administrative_cost: str,
    toll_amount: str = "100.00",
    insurance: str = "10.00",
    tax_rate: str = "0.10"
):
    return SimpleNamespace(
        quote_version_id=version_id,
        contracted_price=Decimal(
            contracted_price
        ),
        toll_amount=Decimal(
            toll_amount
        ),
        freight_insurance_total=Decimal(
            insurance
        ),
        tax_rate=Decimal(
            tax_rate
        ),
        administrative_cost=Decimal(
            administrative_cost
        )
    )


def make_quote(
    quote_id: int,
    quote_type: QuoteType,
    status: QuoteStatus,
    version,
    approved_version_id: int | None = None
):
    return SimpleNamespace(
        quote_id=quote_id,
        quote_type=quote_type,
        current_status=status,
        approved_version_id=(
            approved_version_id
            if approved_version_id is not None
            else (
                version.quote_version_id
                if status == QuoteStatus.APPROVED
                else None
            )
        ),
        versions=(version,)
    )


def make_closed_assignment(
    amount: str
):
    return SimpleNamespace(
        is_active=False,
        actual_driver_amount=Decimal(amount)
    )


def make_active_assignment():
    return SimpleNamespace(
        is_active=True,
        actual_driver_amount=None
    )


def make_expense(
    value: str,
    considered: bool = True
):
    return SimpleNamespace(
        value=Decimal(value),
        is_considered=considered
    )


class FakeFreightRepository:

    def __init__(self, freight):
        self.freight = freight
        self.locked_ids: list[int] = []

    def get_by_id_for_update(self, freight_id: int):
        self.locked_ids.append(freight_id)
        if (
            self.freight is not None
            and self.freight.freight_id == freight_id
        ):
            return self.freight
        return None


class FakeQuoteRepository:

    def __init__(self, quotes):
        self.quotes = tuple(quotes)
        self.locked_freight_ids: list[int] = []

    def list_by_freight_id_for_update(
        self,
        freight_id: int
    ):
        self.locked_freight_ids.append(
            freight_id
        )
        return self.quotes


class FakeDriverAssignmentRepository:

    def __init__(self, assignments):
        self.assignments = tuple(assignments)
        self.listed_freight_ids: list[int] = []

    def list_by_freight_id(self, freight_id: int):
        self.listed_freight_ids.append(
            freight_id
        )
        return self.assignments


class FakeExpenseRepository:

    def __init__(self, expenses):
        self.expenses = tuple(expenses)
        self.listed_freight_ids: list[int] = []

    def list_by_freight_id(self, freight_id: int):
        self.listed_freight_ids.append(
            freight_id
        )
        return self.expenses


class FakeFinancialResultRepository:

    def __init__(self, existing=None):
        self.existing = existing
        self.added = None
        self.looked_up_ids: list[int] = []

    def get_by_freight_id(self, freight_id: int):
        self.looked_up_ids.append(
            freight_id
        )
        return self.existing

    def add(self, financial_result):
        self.added = financial_result
        return financial_result


class FakeUnitOfWork:

    def __init__(
        self,
        freight,
        quotes,
        assignments=(),
        expenses=(),
        existing_result=None
    ):
        self.freights = FakeFreightRepository(
            freight
        )
        self.quotes = FakeQuoteRepository(
            quotes
        )
        self.driver_assignments = (
            FakeDriverAssignmentRepository(
                assignments
            )
        )
        self.expenses = FakeExpenseRepository(
            expenses
        )
        self.financial_results = (
            FakeFinancialResultRepository(
                existing_result
            )
        )
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class FakeUnitOfWorkFactory:

    def __init__(
        self,
        freight,
        quotes,
        assignments=(),
        expenses=(),
        existing_result=None
    ):
        self.freight = freight
        self.quotes = quotes
        self.assignments = assignments
        self.expenses = expenses
        self.existing_result = existing_result
        self.created: list[FakeUnitOfWork] = []

    def create(self):
        unit_of_work = FakeUnitOfWork(
            freight=self.freight,
            quotes=self.quotes,
            assignments=self.assignments,
            expenses=self.expenses,
            existing_result=self.existing_result
        )
        self.created.append(
            unit_of_work
        )
        return unit_of_work


def make_default_quotes():
    primary_version = make_version(
        version_id=1001,
        contracted_price="10000.00",
        administrative_cost="400.00"
    )
    complementary_version = make_version(
        version_id=1002,
        contracted_price="1200.00",
        administrative_cost="80.00",
        toll_amount="0.00",
        insurance="0.00",
        tax_rate="0.10"
    )
    not_approved_version = make_version(
        version_id=1003,
        contracted_price="500.00",
        administrative_cost="50.00"
    )

    return (
        make_quote(
            quote_id=101,
            quote_type=QuoteType.PRIMARY,
            status=QuoteStatus.APPROVED,
            version=primary_version
        ),
        make_quote(
            quote_id=102,
            quote_type=QuoteType.COMPLEMENTARY,
            status=QuoteStatus.APPROVED,
            version=complementary_version
        ),
        make_quote(
            quote_id=103,
            quote_type=QuoteType.COMPLEMENTARY,
            status=QuoteStatus.NEGOTIATION,
            version=not_approved_version
        )
    )


class FinalizeFreightFinancialResultTests(
    unittest.TestCase
):

    def test_finalizes_completed_freight_using_only_approved_quotes(
        self
    ) -> None:
        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=make_default_quotes(),
            assignments=(
                make_closed_assignment(
                    "2000.00"
                ),
                make_closed_assignment(
                    "2300.00"
                )
            ),
            expenses=(
                make_expense(
                    "300.00"
                ),
                make_expense(
                    "999.00",
                    considered=False
                )
            )
        )

        result = FinalizeFreightFinancialResult(
            factory
        ).execute(
            freight_id=77
        )

        self.assertEqual(
            result.contracted_revenue,
            Decimal("11200.00")
        )
        self.assertEqual(
            result.actual_driver_amount,
            Decimal("4300.00")
        )
        self.assertEqual(
            result.toll_amount,
            Decimal("100.00")
        )
        self.assertEqual(
            result.actual_expenses_total,
            Decimal("300.00")
        )
        self.assertEqual(
            result.freight_insurance_total,
            Decimal("10.00")
        )
        self.assertEqual(
            result.tax_total,
            Decimal("1120.0000")
        )
        self.assertEqual(
            result.administrative_cost_allocated,
            Decimal("480.00")
        )
        self.assertEqual(
            result.total_cost,
            Decimal("6310.0000")
        )
        self.assertEqual(
            result.realized_result,
            Decimal("4890.0000")
        )
        self.assertIsNotNone(
            result.finalized_at.tzinfo
        )

        unit_of_work = factory.created[-1]

        self.assertEqual(
            unit_of_work.freights.locked_ids,
            [77]
        )
        self.assertEqual(
            unit_of_work.quotes.locked_freight_ids,
            [77]
        )
        self.assertEqual(
            unit_of_work.driver_assignments.listed_freight_ids,
            [77]
        )
        self.assertEqual(
            unit_of_work.expenses.listed_freight_ids,
            [77]
        )
        self.assertIs(
            unit_of_work.financial_results.added,
            result
        )
        self.assertTrue(
            unit_of_work.committed
        )

    def test_accepts_completed_freight_with_only_primary_quote(
        self
    ) -> None:
        version = make_version(
            1001,
            "10000.00",
            "400.00"
        )
        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=(
                make_quote(
                    101,
                    QuoteType.PRIMARY,
                    QuoteStatus.APPROVED,
                    version
                ),
            )
        )

        result = FinalizeFreightFinancialResult(
            factory
        ).execute(
            77
        )

        self.assertEqual(
            result.contracted_revenue,
            Decimal("10000.00")
        )
        self.assertTrue(
            factory.created[-1].committed
        )

    def test_rejects_invalid_freight_id_before_opening_uow(
        self
    ) -> None:
        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=make_default_quotes()
        )

        with self.assertRaises(
            InvalidFreightDataError
        ):
            FinalizeFreightFinancialResult(
                factory
            ).execute(
                0
            )

        self.assertEqual(
            factory.created,
            []
        )

    def test_rejects_missing_freight(
        self
    ) -> None:
        factory = FakeUnitOfWorkFactory(
            freight=None,
            quotes=()
        )

        with self.assertRaises(
            FreightNotFoundError
        ):
            FinalizeFreightFinancialResult(
                factory
            ).execute(
                77
            )

        self.assertFalse(
            factory.created[-1].committed
        )

    def test_rejects_freight_that_is_not_completed(
        self
    ) -> None:
        for status in (
            FreightStatus.PENDING,
            FreightStatus.IN_PROGRESS,
            FreightStatus.CANCELLED
        ):
            with self.subTest(
                status=status
            ):
                factory = FakeUnitOfWorkFactory(
                    freight=make_freight(
                        status
                    ),
                    quotes=make_default_quotes()
                )

                with self.assertRaisesRegex(
                    InvalidFreightStateError,
                    "Somente frete concluído"
                ):
                    FinalizeFreightFinancialResult(
                        factory
                    ).execute(
                        77
                    )

                self.assertFalse(
                    factory.created[-1].committed
                )

    def test_rejects_existing_financial_result(
        self
    ) -> None:
        existing = SimpleNamespace(
            freight_id=77
        )
        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=make_default_quotes(),
            existing_result=existing
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "já possui fechamento financeiro"
        ):
            FinalizeFreightFinancialResult(
                factory
            ).execute(
                77
            )

        unit_of_work = factory.created[-1]
        self.assertEqual(
            unit_of_work.quotes.locked_freight_ids,
            []
        )
        self.assertFalse(
            unit_of_work.committed
        )

    def test_rejects_when_primary_quote_is_missing(
        self
    ) -> None:
        version = make_version(
            1002,
            "1200.00",
            "80.00"
        )
        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=(
                make_quote(
                    102,
                    QuoteType.COMPLEMENTARY,
                    QuoteStatus.APPROVED,
                    version
                ),
            )
        )

        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "exatamente seu orçamento principal"
        ):
            FinalizeFreightFinancialResult(
                factory
            ).execute(
                77
            )

    def test_rejects_when_primary_quote_is_not_approved(
        self
    ) -> None:
        version = make_version(
            1001,
            "10000.00",
            "400.00"
        )
        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=(
                make_quote(
                    101,
                    QuoteType.PRIMARY,
                    QuoteStatus.NEGOTIATION,
                    version
                ),
            )
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Orçamento principal.*aprovado"
        ):
            FinalizeFreightFinancialResult(
                factory
            ).execute(
                77
            )

    def test_rejects_different_primary_quote(
        self
    ) -> None:
        version = make_version(
            1004,
            "10000.00",
            "400.00"
        )
        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=(
                make_quote(
                    104,
                    QuoteType.PRIMARY,
                    QuoteStatus.APPROVED,
                    version
                ),
            )
        )

        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "exatamente seu orçamento principal"
        ):
            FinalizeFreightFinancialResult(
                factory
            ).execute(
                77
            )

    def test_rejects_approved_quote_without_matching_version(
        self
    ) -> None:
        version = make_version(
            1001,
            "10000.00",
            "400.00"
        )
        quote = make_quote(
            101,
            QuoteType.PRIMARY,
            QuoteStatus.APPROVED,
            version,
            approved_version_id=9999
        )
        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=(quote,)
        )

        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "Versão aprovada precisa pertencer"
        ):
            FinalizeFreightFinancialResult(
                factory
            ).execute(
                77
            )

    def test_rejects_active_driver_assignment_from_inconsistent_data(
        self
    ) -> None:
        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=make_default_quotes(),
            assignments=(
                make_active_assignment(),
            )
        )

        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "Participação ativa"
        ):
            FinalizeFreightFinancialResult(
                factory
            ).execute(
                77
            )

        self.assertFalse(
            factory.created[-1].committed
        )

    def test_rejects_incomplete_approved_version_financial_data(
        self
    ) -> None:
        version = make_version(
            1001,
            "10000.00",
            "400.00"
        )
        version.administrative_cost = None

        factory = FakeUnitOfWorkFactory(
            freight=make_freight(),
            quotes=(
                make_quote(
                    101,
                    QuoteType.PRIMARY,
                    QuoteStatus.APPROVED,
                    version
                ),
            )
        )

        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "administrative_cost é obrigatório"
        ):
            FinalizeFreightFinancialResult(
                factory
            ).execute(
                77
            )

        self.assertFalse(
            factory.created[-1].committed
        )


if __name__ == "__main__":
    unittest.main()
