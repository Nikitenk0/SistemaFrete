from typing import Protocol

from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderAffiliation,
)


class DriverTransportProviderAffiliationRepository(Protocol):

    def add(
        self,
        affiliation: DriverTransportProviderAffiliation,
    ) -> DriverTransportProviderAffiliation:
        ...

    def save(
        self,
        affiliation: DriverTransportProviderAffiliation,
    ) -> DriverTransportProviderAffiliation:
        ...

    def get_active_by_driver_id(
        self,
        driver_id: int,
    ) -> DriverTransportProviderAffiliation | None:
        ...

    def list_by_driver_id(
        self,
        driver_id: int,
    ) -> tuple[DriverTransportProviderAffiliation, ...]:
        ...

    def list_active_by_provider_id(
        self,
        transport_provider_id: int,
    ) -> tuple[DriverTransportProviderAffiliation, ...]:
        ...
