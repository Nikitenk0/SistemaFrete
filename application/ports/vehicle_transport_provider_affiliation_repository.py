from typing import Protocol

from domain.models.vehicle_transport_provider_affiliation import (
    VehicleTransportProviderAffiliation,
)


class VehicleTransportProviderAffiliationRepository(Protocol):

    def add(
        self,
        affiliation: VehicleTransportProviderAffiliation,
    ) -> VehicleTransportProviderAffiliation:
        ...

    def save(
        self,
        affiliation: VehicleTransportProviderAffiliation,
    ) -> VehicleTransportProviderAffiliation:
        ...

    def get_active_by_vehicle_id(
        self,
        vehicle_id: int,
    ) -> VehicleTransportProviderAffiliation | None:
        ...

    def list_by_vehicle_id(
        self,
        vehicle_id: int,
    ) -> tuple[VehicleTransportProviderAffiliation, ...]:
        ...

    def list_active_by_provider_id(
        self,
        transport_provider_id: int,
    ) -> tuple[VehicleTransportProviderAffiliation, ...]:
        ...
