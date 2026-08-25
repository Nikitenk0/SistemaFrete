from types import TracebackType
from typing import Protocol

from application.ports.driver_repository import (
    DriverRepository
)
from application.ports.freight_driver_assignment_repository import (
    FreightDriverAssignmentRepository
)
from application.ports.freight_repository import (
    FreightRepository
)
from application.ports.freight_transport_unit_repository import (
    FreightTransportUnitRepository
)


class FreightDriverAssignmentUnitOfWork(Protocol):

    @property
    def freights(
        self
    ) -> FreightRepository:
        ...

    @property
    def transport_units(
        self
    ) -> FreightTransportUnitRepository:
        ...

    @property
    def drivers(
        self
    ) -> DriverRepository:
        ...

    @property
    def driver_assignments(
        self
    ) -> FreightDriverAssignmentRepository:
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
    ) -> "FreightDriverAssignmentUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        ...


class FreightDriverAssignmentUnitOfWorkFactory(Protocol):

    def create(
        self
    ) -> FreightDriverAssignmentUnitOfWork:
        ...
