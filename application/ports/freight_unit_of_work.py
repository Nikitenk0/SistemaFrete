from types import TracebackType
from typing import Protocol

from application.ports.freight_repository import (
    FreightRepository
)
from application.ports.freight_transport_unit_repository import (
    FreightTransportUnitRepository
)
from application.ports.quote_repository import (
    QuoteRepository
)


class FreightUnitOfWork(Protocol):

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
    def quotes(
        self
    ) -> QuoteRepository:
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
    ) -> "FreightUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        ...


class FreightUnitOfWorkFactory(Protocol):

    def create(
        self
    ) -> FreightUnitOfWork:
        ...
