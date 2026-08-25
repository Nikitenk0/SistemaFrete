from application.exceptions import (
    FreightExpenseNotFoundError,
    FreightNotFoundError,
    InvalidFreightDataError
)
from application.ports.freight_expense_unit_of_work import (
    FreightExpenseUnitOfWorkFactory
)
from domain.models.freight_expense import FreightExpense


class ChangeFreightExpenseConsideration:

    def __init__(
        self,
        unit_of_work_factory: FreightExpenseUnitOfWorkFactory
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        freight_id: int,
        freight_expense_id: int,
        is_considered: bool
    ) -> FreightExpense:

        if freight_id < 1:
            raise InvalidFreightDataError("freight_id inválido")

        if freight_expense_id < 1:
            raise InvalidFreightDataError(
                "freight_expense_id inválido"
            )

        if not isinstance(is_considered, bool):
            raise InvalidFreightDataError(
                "is_considered inválido"
            )

        with self._unit_of_work_factory.create() as unit_of_work:
            freight = unit_of_work.freights.get_by_id_for_update(
                freight_id
            )

            if freight is None:
                raise FreightNotFoundError("Frete não encontrado")

            expense = unit_of_work.expenses.get_by_id(
                freight_expense_id
            )

            if (
                expense is None
                or expense.freight_id != freight_id
            ):
                raise FreightExpenseNotFoundError(
                    "Despesa do frete não encontrada"
                )

            if expense.is_considered == is_considered:
                return expense

            try:
                updated_expense = expense.with_consideration(
                    is_considered
                )
            except ValueError as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            saved_expense = unit_of_work.expenses.save(
                updated_expense
            )
            unit_of_work.commit()
            return saved_expense
