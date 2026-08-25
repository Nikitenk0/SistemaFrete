from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal, InvalidOperation

from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)
from domain.models.freight_expense import (
    FreightExpense
)
from domain.models.freight_financial_result import (
    FreightFinancialResult
)
from domain.models.quote_version import (
    QuoteVersion
)


ZERO = Decimal("0")
ONE = Decimal("1")


def calculate_freight_financial_result(
    freight_id: int,
    approved_quote_versions: Sequence[QuoteVersion],
    driver_assignments: Sequence[FreightDriverAssignment],
    expenses: Sequence[FreightExpense],
    finalized_at: datetime
) -> FreightFinancialResult:

    if freight_id < 1:
        raise ValueError("freight_id inválido")

    if finalized_at is None:
        raise ValueError("finalized_at é obrigatório")

    if not approved_quote_versions:
        raise ValueError(
            "Frete precisa possuir ao menos uma versão "
            "de orçamento aprovada"
        )

    contracted_revenue = ZERO
    toll_amount = ZERO
    freight_insurance_total = ZERO
    tax_total = ZERO
    administrative_cost_allocated = ZERO

    for version in approved_quote_versions:
        contracted_price = _required_non_negative_decimal(
            version.contracted_price,
            "contracted_price"
        )
        version_toll = _required_non_negative_decimal(
            version.toll_amount,
            "toll_amount"
        )
        version_insurance = _required_non_negative_decimal(
            version.freight_insurance_total,
            "freight_insurance_total"
        )
        tax_rate = _required_non_negative_decimal(
            version.tax_rate,
            "tax_rate"
        )
        administrative_cost = _required_non_negative_decimal(
            version.administrative_cost,
            "administrative_cost"
        )

        if tax_rate >= ONE:
            raise ValueError("tax_rate inválida")

        contracted_revenue += contracted_price
        toll_amount += version_toll
        freight_insurance_total += version_insurance
        tax_total += contracted_price * tax_rate
        administrative_cost_allocated += administrative_cost

    actual_driver_amount = ZERO

    for assignment in driver_assignments:
        if assignment.is_active:
            raise ValueError(
                "Participação ativa de motorista não pode "
                "compor fechamento financeiro"
            )

        amount = _required_non_negative_decimal(
            assignment.actual_driver_amount,
            "actual_driver_amount"
        )

        actual_driver_amount += amount

    actual_expenses_total = sum(
        (
            _required_non_negative_decimal(
                expense.value,
                "expense.value"
            )
            for expense in expenses
            if expense.is_considered
        ),
        start=ZERO
    )

    total_cost = (
        actual_driver_amount
        + toll_amount
        + actual_expenses_total
        + freight_insurance_total
        + tax_total
        + administrative_cost_allocated
    )

    realized_result = (
        contracted_revenue
        - total_cost
    )

    realized_margin = (
        realized_result / total_cost
        if total_cost != ZERO
        else None
    )

    return FreightFinancialResult(
        freight_id=freight_id,
        contracted_revenue=contracted_revenue,
        actual_driver_amount=actual_driver_amount,
        toll_amount=toll_amount,
        actual_expenses_total=actual_expenses_total,
        freight_insurance_total=freight_insurance_total,
        tax_total=tax_total,
        administrative_cost_allocated=(
            administrative_cost_allocated
        ),
        total_cost=total_cost,
        realized_result=realized_result,
        realized_margin=realized_margin,
        finalized_at=finalized_at
    )


def _required_non_negative_decimal(
    value,
    field_name: str
) -> Decimal:
    if value is None:
        raise ValueError(
            f"{field_name} é obrigatório para fechamento financeiro"
        )

    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise ValueError(
            f"{field_name} inválido"
        ) from error

    if (
        not decimal_value.is_finite()
        or decimal_value < ZERO
    ):
        raise ValueError(
            f"{field_name} inválido"
        )

    return decimal_value
