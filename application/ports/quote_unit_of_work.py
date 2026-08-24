from types import TracebackType
from typing import Protocol

from application.ports.quote_number_generator import (
    QuoteNumberGenerator
)
from application.ports.quote_repository import (
    QuoteRepository
)


class QuoteUnitOfWork(Protocol):

    @property
    def quotes(
        self
    ) -> QuoteRepository:
        ...

    @property
    def quote_numbers(
        self
    ) -> QuoteNumberGenerator:
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
    ) -> "QuoteUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        ...


class QuoteUnitOfWorkFactory(Protocol):

    def create(
        self
    ) -> QuoteUnitOfWork:
        ...