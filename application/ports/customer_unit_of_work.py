from types import TracebackType
from typing import Protocol

from application.ports.customer_repository import (
    CustomerRepository
)


class CustomerUnitOfWork(Protocol):

    @property
    def customers(
        self
    ) -> CustomerRepository:
        ...

    def commit(
        self
    ) -> None:
        ...

    def rollback(
        self
    ) -> None:
        ...

    def __enter__(
        self
    ) -> "CustomerUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        ...


class CustomerUnitOfWorkFactory(Protocol):

    def create(
        self
    ) -> CustomerUnitOfWork:
        ...