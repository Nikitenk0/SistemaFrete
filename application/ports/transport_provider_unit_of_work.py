from types import TracebackType
from typing import Protocol

from application.ports.driver_repository import (
    DriverRepository,
)
from application.ports.driver_transport_provider_affiliation_repository import (
    DriverTransportProviderAffiliationRepository,
)
from application.ports.transport_provider_repository import (
    TransportProviderRepository,
)
from application.ports.vehicle_repository import (
    VehicleRepository,
)
from application.ports.vehicle_transport_provider_affiliation_repository import (
    VehicleTransportProviderAffiliationRepository,
)


class TransportProviderUnitOfWork(Protocol):

    @property
    def providers(
        self,
    ) -> TransportProviderRepository:
        ...

    @property
    def driver_affiliations(
        self,
    ) -> DriverTransportProviderAffiliationRepository:
        ...

    @property
    def vehicle_affiliations(
        self,
    ) -> VehicleTransportProviderAffiliationRepository:
        ...

    @property
    def drivers(
        self,
    ) -> DriverRepository:
        ...

    @property
    def vehicles(
        self,
    ) -> VehicleRepository:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def __enter__(
        self,
    ) -> "TransportProviderUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...


class TransportProviderUnitOfWorkFactory(Protocol):

    def create(
        self,
    ) -> TransportProviderUnitOfWork:
        ...
