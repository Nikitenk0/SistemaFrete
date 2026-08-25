from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class FreightFinancialResult:

    freight_id: int

    contracted_revenue: Decimal
    actual_driver_amount: Decimal
    toll_amount: Decimal
    actual_expenses_total: Decimal
    freight_insurance_total: Decimal
    tax_total: Decimal
    administrative_cost_allocated: Decimal

    total_cost: Decimal
    realized_result: Decimal
    realized_margin: Decimal | None

    finalized_at: datetime

    freight_financial_result_id: int | None = None

    def __post_init__(self) -> None:
        if self.freight_id < 1:
            raise ValueError("freight_id inválido")

        if (
            self.freight_financial_result_id is not None
            and self.freight_financial_result_id < 1
        ):
            raise ValueError(
                "freight_financial_result_id inválido"
            )

        if self.finalized_at is None:
            raise ValueError("finalized_at é obrigatório")

        contracted_revenue = self._decimal(
            self.contracted_revenue,
            "contracted_revenue"
        )
        actual_driver_amount = self._decimal(
            self.actual_driver_amount,
            "actual_driver_amount"
        )
        toll_amount = self._decimal(
            self.toll_amount,
            "toll_amount"
        )
        actual_expenses_total = self._decimal(
            self.actual_expenses_total,
            "actual_expenses_total"
        )
        freight_insurance_total = self._decimal(
            self.freight_insurance_total,
            "freight_insurance_total"
        )
        tax_total = self._decimal(
            self.tax_total,
            "tax_total"
        )
        administrative_cost_allocated = self._decimal(
            self.administrative_cost_allocated,
            "administrative_cost_allocated"
        )
        total_cost = self._decimal(
            self.total_cost,
            "total_cost"
        )
        realized_result = self._decimal(
            self.realized_result,
            "realized_result"
        )

        realized_margin = (
            None
            if self.realized_margin is None
            else self._decimal(
                self.realized_margin,
                "realized_margin"
            )
        )

        non_negative_values = (
            contracted_revenue,
            actual_driver_amount,
            toll_amount,
            actual_expenses_total,
            freight_insurance_total,
            tax_total,
            administrative_cost_allocated,
            total_cost
        )

        if any(
            value < Decimal("0")
            for value in non_negative_values
        ):
            raise ValueError(
                "Valores financeiros de custo e receita "
                "não podem ser negativos"
            )

        expected_total_cost = (
            actual_driver_amount
            + toll_amount
            + actual_expenses_total
            + freight_insurance_total
            + tax_total
            + administrative_cost_allocated
        )

        if total_cost != expected_total_cost:
            raise ValueError("total_cost inconsistente")

        expected_result = (
            contracted_revenue
            - total_cost
        )

        if realized_result != expected_result:
            raise ValueError("realized_result inconsistente")

        expected_margin = (
            realized_result / total_cost
            if total_cost != Decimal("0")
            else None
        )

        if realized_margin != expected_margin:
            raise ValueError("realized_margin inconsistente")

        object.__setattr__(
            self,
            "contracted_revenue",
            contracted_revenue
        )
        object.__setattr__(
            self,
            "actual_driver_amount",
            actual_driver_amount
        )
        object.__setattr__(
            self,
            "toll_amount",
            toll_amount
        )
        object.__setattr__(
            self,
            "actual_expenses_total",
            actual_expenses_total
        )
        object.__setattr__(
            self,
            "freight_insurance_total",
            freight_insurance_total
        )
        object.__setattr__(
            self,
            "tax_total",
            tax_total
        )
        object.__setattr__(
            self,
            "administrative_cost_allocated",
            administrative_cost_allocated
        )
        object.__setattr__(
            self,
            "total_cost",
            total_cost
        )
        object.__setattr__(
            self,
            "realized_result",
            realized_result
        )
        object.__setattr__(
            self,
            "realized_margin",
            realized_margin
        )

    @staticmethod
    def _decimal(
        value,
        field_name: str
    ) -> Decimal:
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as error:
            raise ValueError(
                f"{field_name} inválido"
            ) from error

        if not decimal_value.is_finite():
            raise ValueError(
                f"{field_name} inválido"
            )

        return decimal_value
