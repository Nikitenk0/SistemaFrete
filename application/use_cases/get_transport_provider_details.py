from application.dtos.transport_provider_query import (
    TransportProviderDetails,
    TransportProviderDriverDetails,
    TransportProviderVehicleDetails,
)
from application.exceptions import (
    InvalidTransportProviderDataError,
    TransportProviderNotFoundError,
)
from application.ports.transport_provider_unit_of_work import (
    TransportProviderUnitOfWorkFactory,
)


class GetTransportProviderDetails:

    def __init__(
        self,
        unit_of_work_factory: TransportProviderUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        transport_provider_id: int,
    ) -> TransportProviderDetails:
        if transport_provider_id < 1:
            raise InvalidTransportProviderDataError(
                "transport_provider_id inválido"
            )

        with self._unit_of_work_factory.create() as unit_of_work:
            provider = unit_of_work.providers.get_by_id(
                transport_provider_id
            )
            if provider is None:
                raise TransportProviderNotFoundError(
                    "Prestador de transporte não encontrado"
                )

            driver_links = (
                unit_of_work.driver_affiliations
                .list_active_by_provider_id(
                    transport_provider_id
                )
            )
            vehicle_links = (
                unit_of_work.vehicle_affiliations
                .list_active_by_provider_id(
                    transport_provider_id
                )
            )

            drivers = []
            for link in driver_links:
                driver = unit_of_work.drivers.get_by_id(
                    link.driver_id
                )
                if driver is None:
                    continue
                drivers.append(
                    TransportProviderDriverDetails(
                        driver_id=driver.driver_id,
                        name=driver.name,
                        cpf=driver.cpf,
                        role=link.role,
                        started_at=link.started_at,
                    )
                )

            vehicles = []
            for link in vehicle_links:
                vehicle = unit_of_work.vehicles.get_by_id(
                    link.vehicle_id
                )
                if vehicle is None:
                    continue
                vehicles.append(
                    TransportProviderVehicleDetails(
                        vehicle_id=vehicle.vehicle_id,
                        plate=vehicle.plate,
                        vehicle_type=vehicle.vehicle_type,
                        relation=link.relation,
                        started_at=link.started_at,
                    )
                )

            return TransportProviderDetails(
                provider=provider,
                drivers=tuple(
                    sorted(
                        drivers,
                        key=lambda item: (
                            item.name.casefold(),
                            item.driver_id,
                        ),
                    )
                ),
                vehicles=tuple(
                    sorted(
                        vehicles,
                        key=lambda item: (
                            item.plate,
                            item.vehicle_id,
                        ),
                    )
                ),
            )
