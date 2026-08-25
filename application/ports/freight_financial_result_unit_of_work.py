from types import TracebackType
from typing import Protocol

from application.ports.freight_driver_assignment_repository import (
    FreightDriverAssignmentRepository
)
from application.ports.freight_expense_repository import (
    FreightExpenseRepository
)
from application.ports.freight_financial_quote_repository import (
    FreightFinancialQuoteRepository
)
from application.ports.freight_financial_result_repository import (
    FreightFinancialResultRepository
)
from application.ports.freight_repository import (
    FreightRepository
)


class FreightFinancialResultUnitOfWork(Protocol):

    @property
    def freights(self) -> FreightRepository:
        ...

    @property
    def quotes(self) -> FreightFinancialQuoteRepository:
        ...

    @property
    def driver_assignments(
        self
    ) -> FreightDriverAssignmentRepository:
        ...

    @property
    def expenses(self) -> FreightExpenseRepository:
        ...

    @property
    def financial_results(
        self
    ) -> FreightFinancialResultRepository:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def __enter__(
        self
    ) -> "FreightFinancialResultUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        ...


class FreightFinancialResultUnitOfWorkFactory(Protocol):

    def create(
        self
    ) -> FreightFinancialResultUnitOfWork:
        ...
