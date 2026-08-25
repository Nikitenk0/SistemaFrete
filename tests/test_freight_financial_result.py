import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

from domain.freight_financial_result import (
    calculate_freight_financial_result
)
from domain.models.freight_financial_result import (
    FreightFinancialResult
)


NOW = datetime(
    2026,
    8,
    25,
    18,
    0,
    tzinfo=timezone.utc
)


class FakeAssignment:
    def __init__(
        self,
        amount: str | None,
        active: bool = False
    ):
        self.actual_driver_amount = (
            None
            if amount is None
            else Decimal(amount)
        )
        self.is_active = active


class FakeExpense:
    def __init__(
        self,
        value: str,
        considered: bool = True
    ):
        self.value = Decimal(value)
        self.is_considered = considered


def make_version(
    contracted_price: str = "10000.00",
    toll_amount: str = "500.00",
    insurance: str = "100.00",
    tax_rate: str = "0.10",
    administrative_cost: str = "400.00",
    tax_value: str = "9999.00"
):
    return SimpleNamespace(
        contracted_price=Decimal(contracted_price),
        toll_amount=Decimal(toll_amount),
        freight_insurance_total=Decimal(insurance),
        tax_rate=Decimal(tax_rate),
        administrative_cost=Decimal(
            administrative_cost
        ),
        tax_value=Decimal(tax_value)
    )


class FreightFinancialResultEntityTests(unittest.TestCase):

    def test_accepts_consistent_snapshot(self) -> None:
        result = FreightFinancialResult(
            freight_id=77,
            contracted_revenue=Decimal("10000"),
            actual_driver_amount=Decimal("2000"),
            toll_amount=Decimal("500"),
            actual_expenses_total=Decimal("300"),
            freight_insurance_total=Decimal("100"),
            tax_total=Decimal("1000"),
            administrative_cost_allocated=Decimal("400"),
            total_cost=Decimal("4300"),
            realized_result=Decimal("5700"),
            realized_margin=(
                Decimal("5700") / Decimal("4300")
            ),
            finalized_at=NOW
        )

        self.assertEqual(
            result.total_cost,
            Decimal("4300")
        )

    def test_rejects_invalid_freight_id(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "freight_id inválido"
        ):
            FreightFinancialResult(
                freight_id=0,
                contracted_revenue=0,
                actual_driver_amount=0,
                toll_amount=0,
                actual_expenses_total=0,
                freight_insurance_total=0,
                tax_total=0,
                administrative_cost_allocated=0,
                total_cost=0,
                realized_result=0,
                realized_margin=None,
                finalized_at=NOW
            )

    def test_rejects_negative_cost_component(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "não podem ser negativos"
        ):
            FreightFinancialResult(
                freight_id=77,
                contracted_revenue=100,
                actual_driver_amount=-1,
                toll_amount=0,
                actual_expenses_total=0,
                freight_insurance_total=0,
                tax_total=0,
                administrative_cost_allocated=0,
                total_cost=0,
                realized_result=100,
                realized_margin=None,
                finalized_at=NOW
            )

    def test_rejects_inconsistent_total_cost(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "total_cost inconsistente"
        ):
            FreightFinancialResult(
                freight_id=77,
                contracted_revenue=100,
                actual_driver_amount=10,
                toll_amount=0,
                actual_expenses_total=0,
                freight_insurance_total=0,
                tax_total=0,
                administrative_cost_allocated=0,
                total_cost=11,
                realized_result=89,
                realized_margin=Decimal("89") / Decimal("11"),
                finalized_at=NOW
            )

    def test_rejects_inconsistent_result(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "realized_result inconsistente"
        ):
            FreightFinancialResult(
                freight_id=77,
                contracted_revenue=100,
                actual_driver_amount=10,
                toll_amount=0,
                actual_expenses_total=0,
                freight_insurance_total=0,
                tax_total=0,
                administrative_cost_allocated=0,
                total_cost=10,
                realized_result=91,
                realized_margin=Decimal("91") / Decimal("10"),
                finalized_at=NOW
            )

    def test_rejects_inconsistent_margin(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "realized_margin inconsistente"
        ):
            FreightFinancialResult(
                freight_id=77,
                contracted_revenue=100,
                actual_driver_amount=10,
                toll_amount=0,
                actual_expenses_total=0,
                freight_insurance_total=0,
                tax_total=0,
                administrative_cost_allocated=0,
                total_cost=10,
                realized_result=90,
                realized_margin=Decimal("0.90"),
                finalized_at=NOW
            )

    def test_zero_cost_has_undefined_margin(self) -> None:
        result = FreightFinancialResult(
            freight_id=77,
            contracted_revenue=100,
            actual_driver_amount=0,
            toll_amount=0,
            actual_expenses_total=0,
            freight_insurance_total=0,
            tax_total=0,
            administrative_cost_allocated=0,
            total_cost=0,
            realized_result=100,
            realized_margin=None,
            finalized_at=NOW
        )

        self.assertIsNone(
            result.realized_margin
        )


class FreightFinancialResultCalculationTests(
    unittest.TestCase
):

    def test_calculates_single_quote_snapshot(self) -> None:
        result = calculate_freight_financial_result(
            freight_id=77,
            approved_quote_versions=(
                make_version(),
            ),
            driver_assignments=(
                FakeAssignment("2000.00"),
            ),
            expenses=(
                FakeExpense("300.00"),
            ),
            finalized_at=NOW
        )

        self.assertEqual(
            result.contracted_revenue,
            Decimal("10000.00")
        )
        self.assertEqual(
            result.tax_total,
            Decimal("1000.0000")
        )
        self.assertEqual(
            result.total_cost,
            Decimal("4300.0000")
        )
        self.assertEqual(
            result.realized_result,
            Decimal("5700.0000")
        )

    def test_aggregates_approved_versions(self) -> None:
        result = calculate_freight_financial_result(
            freight_id=77,
            approved_quote_versions=(
                make_version(
                    contracted_price="10000",
                    toll_amount="500",
                    insurance="100",
                    tax_rate="0.10",
                    administrative_cost="400"
                ),
                make_version(
                    contracted_price="1200",
                    toll_amount="50",
                    insurance="20",
                    tax_rate="0.10",
                    administrative_cost="80"
                )
            ),
            driver_assignments=(
                FakeAssignment("2000"),
                FakeAssignment("2300"),
                FakeAssignment("3800")
            ),
            expenses=(),
            finalized_at=NOW
        )

        self.assertEqual(
            result.contracted_revenue,
            Decimal("11200")
        )
        self.assertEqual(
            result.administrative_cost_allocated,
            Decimal("480")
        )
        self.assertEqual(
            result.actual_driver_amount,
            Decimal("8100")
        )

    def test_ignores_not_considered_expense(self) -> None:
        result = calculate_freight_financial_result(
            freight_id=77,
            approved_quote_versions=(
                make_version(),
            ),
            driver_assignments=(
                FakeAssignment("2000"),
            ),
            expenses=(
                FakeExpense("300", True),
                FakeExpense("999", False)
            ),
            finalized_at=NOW
        )

        self.assertEqual(
            result.actual_expenses_total,
            Decimal("300")
        )

    def test_tax_uses_contracted_price_and_rate(self) -> None:
        version = make_version(
            contracted_price="6200",
            tax_rate="0.20",
            tax_value="9999"
        )

        result = calculate_freight_financial_result(
            freight_id=77,
            approved_quote_versions=(version,),
            driver_assignments=(
                FakeAssignment("1000"),
            ),
            expenses=(),
            finalized_at=NOW
        )

        self.assertEqual(
            result.tax_total,
            Decimal("1240.00")
        )
        self.assertNotEqual(
            result.tax_total,
            version.tax_value
        )

    def test_rejects_active_driver_assignment(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Participação ativa"
        ):
            calculate_freight_financial_result(
                freight_id=77,
                approved_quote_versions=(
                    make_version(),
                ),
                driver_assignments=(
                    FakeAssignment(None, active=True),
                ),
                expenses=(),
                finalized_at=NOW
            )

    def test_rejects_missing_contracted_price(self) -> None:
        version = make_version()
        version.contracted_price = None

        with self.assertRaisesRegex(
            ValueError,
            "contracted_price é obrigatório"
        ):
            calculate_freight_financial_result(
                freight_id=77,
                approved_quote_versions=(version,),
                driver_assignments=(),
                expenses=(),
                finalized_at=NOW
            )

    def test_rejects_missing_administrative_cost(self) -> None:
        version = make_version()
        version.administrative_cost = None

        with self.assertRaisesRegex(
            ValueError,
            "administrative_cost é obrigatório"
        ):
            calculate_freight_financial_result(
                freight_id=77,
                approved_quote_versions=(version,),
                driver_assignments=(),
                expenses=(),
                finalized_at=NOW
            )

    def test_rejects_without_approved_versions(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "ao menos uma versão"
        ):
            calculate_freight_financial_result(
                freight_id=77,
                approved_quote_versions=(),
                driver_assignments=(),
                expenses=(),
                finalized_at=NOW
            )

    def test_realized_margin_uses_total_cost_as_base(self) -> None:
        result = calculate_freight_financial_result(
            freight_id=77,
            approved_quote_versions=(
                make_version(
                    contracted_price="100",
                    toll_amount="0",
                    insurance="0",
                    tax_rate="0",
                    administrative_cost="0"
                ),
            ),
            driver_assignments=(
                FakeAssignment("80"),
            ),
            expenses=(),
            finalized_at=NOW
        )

        self.assertEqual(
            result.realized_result,
            Decimal("20")
        )
        self.assertEqual(
            result.realized_margin,
            Decimal("0.25")
        )

    def test_allows_negative_realized_result_and_margin(self) -> None:
        result = calculate_freight_financial_result(
            freight_id=77,
            approved_quote_versions=(
                make_version(
                    contracted_price="100",
                    toll_amount="0",
                    insurance="0",
                    tax_rate="0",
                    administrative_cost="0"
                ),
            ),
            driver_assignments=(
                FakeAssignment("120"),
            ),
            expenses=(),
            finalized_at=NOW
        )

        self.assertEqual(
            result.realized_result,
            Decimal("-20")
        )
        self.assertEqual(
            result.realized_margin,
            Decimal("-20") / Decimal("120")
        )


if __name__ == "__main__":
    unittest.main()
