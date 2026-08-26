from types import TracebackType
from typing import Protocol

from application.ports.driver_repository import DriverRepository
from application.ports.driver_transport_provider_affiliation_repository import (
    DriverTransportProviderAffiliationRepository,
)
from application.ports.freight_driver_assignment_repository import (
    FreightDriverAssignmentRepository,
)
from application.ports.freight_operational_assignment_repository import (
    FreightOperationalAssignmentRepository,
)
from application.ports.freight_repository import FreightRepository
from application.ports.freight_transport_unit_repository import (
    FreightTransportUnitRepository,
)
from application.ports.freight_vehicle_record_repository import (
    FreightVehicleRecordRepository,
)
from application.ports.transport_provider_repository import (
    TransportProviderRepository,
)
from application.ports.vehicle_repository import VehicleRepository
from application.ports.vehicle_transport_provider_affiliation_repository import (
    VehicleTransportProviderAffiliationRepository,
)


class FreightOperationalAssignmentUnitOfWork(Protocol):

    @property
    def freights(self) -> FreightRepository:
        ...

    @property
    def transport_units(self) -> FreightTransportUnitRepository:
        ...

    @property
    def driver_assignments(self) -> FreightDriverAssignmentRepository:
        ...

    @property
    def vehicle_records(self) -> FreightVehicleRecordRepository:
        ...

    @property
    def operational_assignments(
        self,
    ) -> FreightOperationalAssignmentRepository:
        ...

    @property
    def providers(self) -> TransportProviderRepository:
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
    def drivers(self) -> DriverRepository:
        ...

    @property
    def vehicles(self) -> VehicleRepository:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def __enter__(
        self,
    ) -> "FreightOperationalAssignmentUnitOfWork":
        ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...


class FreightOperationalAssignmentUnitOfWorkFactory(Protocol):

    def create(
        self,
    ) -> FreightOperationalAssignmentUnitOfWork:
        ...
