from datetime import datetime, timezone
from decimal import Decimal

from application.exceptions import (
    FreightNotFoundError,
    InvalidFreightDataError
)
from application.ports.freight_expense_unit_of_work import (
    FreightExpenseUnitOfWorkFactory
)
from domain.models.freight_expense import (
    FreightExpense,
    FreightExpenseType
)


class AddFreightExpense:

    def __init__(
        self,
        unit_of_work_factory: FreightExpenseUnitOfWorkFactory
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        freight_id: int,
        expense_type: FreightExpenseType,
        value: Decimal,
        occurred_at: datetime,
        custom_description: str | None = None,
        observation: str | None = None,
        created_by: int | None = None
    ) -> FreightExpense:

        if freight_id < 1:
            raise InvalidFreightDataError("freight_id inválido")

        if created_by is not None and created_by < 1:
            raise InvalidFreightDataError("created_by inválido")

        with self._unit_of_work_factory.create() as unit_of_work:
            freight = unit_of_work.freights.get_by_id_for_update(
                freight_id
            )

            if freight is None:
                raise FreightNotFoundError("Frete não encontrado")

            try:
                expense = FreightExpense(
                    freight_id=freight_id,
                    expense_type=expense_type,
                    value=value,
                    occurred_at=occurred_at,
                    custom_description=custom_description,
                    observation=observation,
                    is_considered=True,
                    created_at=datetime.now(timezone.utc),
                    created_by=created_by
                )
            except ValueError as error:
                raise InvalidFreightDataError(str(error)) from error

            created_expense = unit_of_work.expenses.add(expense)
            unit_of_work.commit()
            return created_expense
