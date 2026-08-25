from types import TracebackType
from typing import Protocol

from application.ports.driver_repository import (
    DriverRepository
)


class DriverUnitOfWork(Protocol):

    @property
    def drivers(
        self
    ) -> DriverRepository:
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
    ) -> "DriverUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        ...


class DriverUnitOfWorkFactory(Protocol):

    def create(
        self
    ) -> DriverUnitOfWork:
        ...
