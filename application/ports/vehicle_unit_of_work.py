from types import TracebackType
from typing import Protocol

from application.ports.vehicle_repository import (
    VehicleRepository
)


class VehicleUnitOfWork(Protocol):

    @property
    def vehicles(
        self
    ) -> VehicleRepository:
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
    ) -> "VehicleUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        ...


class VehicleUnitOfWorkFactory(Protocol):

    def create(
        self
    ) -> VehicleUnitOfWork:
        ...
