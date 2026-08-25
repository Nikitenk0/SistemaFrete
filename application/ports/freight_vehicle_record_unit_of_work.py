from types import TracebackType
from typing import Protocol

from application.ports.freight_repository import (
    FreightRepository
)
from application.ports.freight_transport_unit_repository import (
    FreightTransportUnitRepository
)
from application.ports.freight_vehicle_record_repository import (
    FreightVehicleRecordRepository
)


class FreightVehicleRecordUnitOfWork(Protocol):

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
    def vehicle_records(
        self
    ) -> FreightVehicleRecordRepository:
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
    ) -> "FreightVehicleRecordUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        ...


class FreightVehicleRecordUnitOfWorkFactory(Protocol):

    def create(
        self
    ) -> FreightVehicleRecordUnitOfWork:
        ...
