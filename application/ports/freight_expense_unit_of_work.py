from types import TracebackType
from typing import Protocol

from application.ports.freight_expense_repository import (
    FreightExpenseRepository
)
from application.ports.freight_repository import FreightRepository


class FreightExpenseUnitOfWork(Protocol):

    @property
    def freights(self) -> FreightRepository:
        ...

    @property
    def expenses(self) -> FreightExpenseRepository:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def __enter__(self) -> "FreightExpenseUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        ...


class FreightExpenseUnitOfWorkFactory(Protocol):

    def create(self) -> FreightExpenseUnitOfWork:
        ...
