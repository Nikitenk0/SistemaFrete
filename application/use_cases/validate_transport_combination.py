from dataclasses import dataclass

from application.exceptions import (
    DriverNotFoundError,
    InvalidDriverStateError,
    InvalidTransportProviderDataError,
    InvalidTransportProviderStateError,
    InvalidVehicleDataError,
    TransportProviderNotFoundError,
    VehicleNotFoundError,
)
from application.ports.transport_provider_unit_of_work import (
    TransportProviderUnitOfWorkFactory,
)
from domain.models.driver import DriverStatus
from domain.models.transport_provider import TransportProviderStatus
from domain.models.vehicle import VehicleStatus


@dataclass(frozen=True)
class ValidTransportCombination:
    transport_provider_id: int
    driver_id: int
    vehicle_id: int


class ValidateTransportCombination:

    def __init__(
        self,
        unit_of_work_factory: TransportProviderUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        transport_provider_id: int,
        driver_id: int,
        vehicle_id: int,
    ) -> ValidTransportCombination:
        if transport_provider_id < 1:
            raise InvalidTransportProviderDataError(
                "transport_provider_id inválido"
            )
        if driver_id < 1:
            raise InvalidTransportProviderDataError(
                "driver_id inválido"
            )
        if vehicle_id < 1:
            raise InvalidVehicleDataError(
                "vehicle_id inválido"
            )

        with self._unit_of_work_factory.create() as unit_of_work:
            provider = unit_of_work.providers.get_by_id(
                transport_provider_id
            )
            if provider is None:
                raise TransportProviderNotFoundError(
                    "Prestador de transporte não encontrado"
                )
            if provider.status != TransportProviderStatus.ACTIVE:
                raise InvalidTransportProviderStateError(
                    "Prestador inativo"
                )

            driver = unit_of_work.drivers.get_by_id(
                driver_id
            )
            if driver is None:
                raise DriverNotFoundError(
                    "Motorista não encontrado"
                )
            if driver.status != DriverStatus.ACTIVE:
                raise InvalidDriverStateError(
                    "Motorista inativo"
                )

            vehicle = unit_of_work.vehicles.get_by_id(
                vehicle_id
            )
            if vehicle is None:
                raise VehicleNotFoundError(
                    "Veículo não encontrado"
                )
            if vehicle.status != VehicleStatus.ACTIVE:
                raise InvalidTransportProviderStateError(
                    "Veículo inativo"
                )

            driver_affiliation = (
                unit_of_work.driver_affiliations
                .get_active_by_driver_id(
                    driver_id
                )
            )
            if (
                driver_affiliation is None
                or driver_affiliation.transport_provider_id
                != transport_provider_id
            ):
                raise InvalidTransportProviderStateError(
                    "Motorista não possui vínculo ativo "
                    "com o prestador selecionado"
                )

            vehicle_affiliation = (
                unit_of_work.vehicle_affiliations
                .get_active_by_vehicle_id(
                    vehicle_id
                )
            )
            if (
                vehicle_affiliation is None
                or vehicle_affiliation.transport_provider_id
                != transport_provider_id
            ):
                raise InvalidTransportProviderStateError(
                    "Veículo não possui vínculo ativo "
                    "com o prestador selecionado"
                )

            return ValidTransportCombination(
                transport_provider_id=transport_provider_id,
                driver_id=driver_id,
                vehicle_id=vehicle_id,
            )
