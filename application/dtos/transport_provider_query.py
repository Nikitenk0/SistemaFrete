from dataclasses import dataclass
from datetime import datetime

from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderRole,
)
from domain.models.transport_provider import (
    TransportProvider,
)
from domain.models.vehicle import VehicleType
from domain.models.vehicle_transport_provider_affiliation import (
    VehicleTransportProviderRelation,
)


@dataclass(frozen=True)
class TransportProviderDriverDetails:
    driver_id: int
    name: str
    cpf: str
    role: DriverTransportProviderRole
    started_at: datetime


@dataclass(frozen=True)
class TransportProviderVehicleDetails:
    vehicle_id: int
    plate: str
    vehicle_type: VehicleType
    relation: VehicleTransportProviderRelation
    started_at: datetime


@dataclass(frozen=True)
class TransportProviderDetails:
    provider: TransportProvider
    drivers: tuple[TransportProviderDriverDetails, ...] = ()
    vehicles: tuple[TransportProviderVehicleDetails, ...] = ()
